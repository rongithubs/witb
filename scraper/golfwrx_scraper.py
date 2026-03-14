#!/usr/bin/env python3
"""
GolfWRX WITB Scraper
Scrapes WITB data from GolfWRX articles using Playwright (bypasses 403)
and BeautifulSoup (parses structured article HTML).
"""

import re
import time
import random
import unicodedata
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from bs4 import BeautifulSoup, Tag
from playwright.sync_api import sync_playwright

from witb_models import PlayerInfo, PlayerWITB, WITBItem

if TYPE_CHECKING:
    from playwright.sync_api import Page

_GOLFWRX_SEARCH_URL = "https://www.golfwrx.com/?s={query}&orderby=date&order=DESC"
_REQUEST_DELAY_RANGE = (2.0, 4.0)
_PLAYWRIGHT_TIMEOUT_MS = 30000

_ARTICLE_BODY_SELECTOR = "#mvp-content-main"
_ARTICLE_LINK_SELECTOR = "a[rel='bookmark']"

# Ordered longest-first so multi-word brands match before single-word prefixes.
_KNOWN_BRANDS = [
    "Scotty Cameron",
    "Golf Pride",
    "True Temper",
    "Graphite Design",
    "L.A.B. Golf",
    "Project X",
    "UST Mamiya",
    "Ben Hogan",
    "Nippon N.S. Pro",
    "TaylorMade",
    "Titleist",
    "Callaway",
    "Mizuno",
    "Cobra",
    "Srixon",
    "Cleveland",
    "Odyssey",
    "Bridgestone",
    "Fujikura",
    "Mitsubishi",
    "Aldila",
    "Lamkin",
    "SuperStroke",
    "Nippon",
    "PING",
    "Ping",
    "Nike",
    "PXG",
    "Honma",
    "Miura",
    "Adams",
    "Fourteen",
    "Yonex",
    "Winn",
    "Iomic",
    "KBS",
]


def _first_name_slug(player_name: str) -> str:
    """Return ASCII-normalized first name slug: 'Scottie Scheffler' → 'scottie', 'J.J. Spaun' → 'jj'."""
    first = player_name.strip().split()[0]
    normalized = unicodedata.normalize("NFKD", first).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^\w]", "", normalized.lower())


def _split_at_top_level_commas(text: str) -> List[str]:
    """Split 'Brand1 Model1 (loft1), Brand2 Model2 (loft2)' on commas outside parentheses."""
    entries: List[str] = []
    depth = 0
    current: List[str] = []
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            entries.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        entries.append("".join(current).strip())
    return [e for e in entries if e]


def _parse_brand_model_loft(text: str) -> tuple[str, str, Optional[str]]:
    """Extract (brand, model, loft) from a single club text like 'TaylorMade Qi4D (8 degrees)'."""
    text = text.strip()
    loft_match = re.search(r"\(([^)]+)\)\s*$", text)
    loft = loft_match.group(1) if loft_match else None
    rest = text[: loft_match.start()].strip() if loft_match else text

    for brand in _KNOWN_BRANDS:
        if rest.lower().startswith(brand.lower()):
            model = rest[len(brand) :].strip()
            return brand, model, loft

    # Fallback: first word is brand
    parts = rest.split(None, 1)
    return parts[0], (parts[1] if len(parts) > 1 else ""), loft


def extract_equipment_from_html(html: str, player_name: str) -> List[WITBItem]:
    """Parse GolfWRX article HTML and return structured WITBItems.

    Expects the HTML from .mvp-post-main-in where each club is a <p> tag:
      <p><strong>Driver:</strong> TaylorMade Qi4D (8 degrees)<br>
      Shaft: Fujikura Ventus Black 7 X</p>
    """
    soup = BeautifulSoup(html, "html.parser")
    items: List[WITBItem] = []

    for p in soup.find_all("p"):
        strong = p.find("strong")
        if not strong:
            continue

        strong_text = strong.get_text(strip=True)
        if not strong_text.endswith(":"):
            continue

        category = strong_text.rstrip(":")

        # Collect text nodes directly in <p> (skip the <strong> itself and <img> tags)
        full_text = ""
        shaft_text: Optional[str] = None
        after_br = False

        for node in p.children:
            if node == strong:
                continue
            if isinstance(node, Tag):
                if node.name == "br":
                    after_br = True
                elif node.name == "img":
                    continue
                else:
                    text = node.get_text()
                    if after_br:
                        shaft_text = (shaft_text or "") + text
                    else:
                        full_text += text
            else:
                text = str(node)
                if after_br:
                    shaft_text = (shaft_text or "") + text
                else:
                    full_text += text

        full_text = full_text.strip()
        shaft_raw = shaft_text.strip() if shaft_text else None

        # Extract shaft value: "Shaft: foo" or "Shafts: foo" or "Grip: foo"
        shaft: Optional[str] = None
        if shaft_raw:
            shaft_match = re.match(r"^(?:Shafts?|Grip):\s*(.+)", shaft_raw, re.IGNORECASE)
            if shaft_match:
                shaft = shaft_match.group(1).strip()

        if not full_text:
            continue

        # Split multi-club lines: "Srixon ZU85 (3, 4), TaylorMade P7TW (5-PW)"
        entries = _split_at_top_level_commas(full_text)
        for entry in entries:
            brand, model, loft = _parse_brand_model_loft(entry)
            if brand and model:
                items.append(
                    WITBItem(
                        category=category,
                        brand=brand,
                        model=model,
                        loft=loft,
                        shaft=shaft,
                    )
                )

    return items


_WITB_URL_EXCLUSIONS = ("time-machine", "club-junkie", "photos-from")


def _is_current_witb_url(href: str) -> bool:
    """Return True if the URL points to a current WITB article (not historical or single-club)."""
    return not any(pattern in href for pattern in _WITB_URL_EXCLUSIONS)


def _find_player_article_url(player_name: str, page: "Page") -> Optional[str]:
    """Find the most recent GolfWRX WITB article via date-sorted GolfWRX search.

    Uses first-name matching to handle possessives ('scotties-scheffler-winning-witb')
    and accented last names. Excludes time-machine and partial-equipment articles.
    Falls back to last-name matching for players with initials (e.g. J.J. Spaun).
    """
    search_url = _GOLFWRX_SEARCH_URL.format(query="+".join(player_name.split() + ["witb"]))
    first_name = _first_name_slug(player_name)
    last_name = _first_name_slug(player_name.strip().split()[-1])
    try:
        page.goto(search_url, wait_until="domcontentloaded", timeout=_PLAYWRIGHT_TIMEOUT_MS)
        page.wait_for_timeout(2000)
        links = page.locator(_ARTICLE_LINK_SELECTOR).all()
        # First pass: require first name in URL (handles most players + possessives)
        for link in links:
            href = (link.get_attribute("href") or "").lower()
            if "golfwrx.com" in href and "witb" in href and first_name in href and _is_current_witb_url(href):
                return link.get_attribute("href") or ""
        # Fallback: use last name (helps with initials like J.J. where first_name='jj' may not match)
        for link in links:
            href = (link.get_attribute("href") or "").lower()
            if "golfwrx.com" in href and "witb" in href and last_name in href and _is_current_witb_url(href):
                return link.get_attribute("href") or ""
    except Exception as e:
        print(f"  Error searching for {player_name}: {e}")
    return None


def _fetch_article_html(url: str, page: "Page") -> Optional[str]:
    """Render GolfWRX article page and return the equipment section HTML."""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=_PLAYWRIGHT_TIMEOUT_MS)
        page.wait_for_timeout(2000)
        element = page.locator(_ARTICLE_BODY_SELECTOR).first
        if element.count() > 0:
            return element.inner_html()
    except Exception as e:
        print(f"  Error fetching article {url}: {e}")
    return None


def _parse_article_date(page: "Page") -> Optional[datetime]:
    """Extract the article publish/update date from the loaded GolfWRX page."""
    try:
        locator = page.locator("time.post-date[datetime]").first
        if locator.count() > 0:
            raw = locator.get_attribute("datetime")
            if raw:
                return datetime.strptime(raw, "%Y-%m-%d")
    except Exception:
        pass
    return None


class GolfWRXScraper:
    """Scrapes WITB data from GolfWRX using Playwright + BeautifulSoup."""

    def scrape_multiple_players(
        self, players: List[PlayerInfo], verbose: bool = True
    ) -> List[PlayerWITB]:
        results: List[PlayerWITB] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
            try:
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/121.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1280, "height": 800},
                )
                page = context.new_page()
                page.add_init_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
                for i, player in enumerate(players, 1):
                    if verbose:
                        print(f"{i:2d}. {player.name:<25} ", end="", flush=True)

                    player_witb = self._scrape_one(player, page)
                    if player_witb:
                        results.append(player_witb)
                        if verbose:
                            print(f"✓ {len(player_witb.witb_items)} items")
                    else:
                        if verbose:
                            print("✗ No data found")

                    time.sleep(random.uniform(*_REQUEST_DELAY_RANGE))
            finally:
                browser.close()

        return results

    def _scrape_one(self, player: PlayerInfo, page: "Page") -> Optional[PlayerWITB]:
        article_url = _find_player_article_url(player.name, page)
        if not article_url:
            return None

        html = _fetch_article_html(article_url, page)
        if not html:
            return None

        witb_items = extract_equipment_from_html(html, player.name)
        if not witb_items:
            return None

        article_date = _parse_article_date(page)

        return PlayerWITB(
            name=player.name,
            country=player.country,
            tour=player.tour,
            ranking=player.ranking,
            witb_items=witb_items,
            source_url=article_url,
            player_id=player.id,
            last_updated=article_date,
        )
