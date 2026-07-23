import asyncio
import re
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv(Path(__file__).parent.parent / "witb-backend" / ".env")

_COUNTRY_CODES: Dict[str, str] = {
    "us": "USA", "gb": "England", "gb-eng": "England", "gb-sct": "Scotland",
    "gb-wls": "Wales", "gb-nir": "Northern Ireland", "ie": "Ireland",
    "au": "Australia", "nz": "New Zealand", "za": "South Africa",
    "jp": "Japan", "kr": "South Korea", "cn": "China", "tw": "Taiwan",
    "de": "Germany", "fr": "France", "es": "Spain", "it": "Italy",
    "se": "Sweden", "no": "Norway", "dk": "Denmark", "fi": "Finland",
    "at": "Austria", "ch": "Switzerland", "be": "Belgium", "nl": "Netherlands",
    "ca": "Canada", "mx": "Mexico", "ar": "Argentina", "co": "Colombia",
    "ve": "Venezuela", "cl": "Chile", "br": "Brazil",
    "in": "India", "th": "Thailand", "my": "Malaysia", "sg": "Singapore",
    "ph": "Philippines", "id": "Indonesia",
    "cn-hk": "Hong Kong", "cn-tw": "Taiwan",
    "ng": "Nigeria", "zw": "Zimbabwe",
}

_NAME_CORRECTIONS: Dict[str, str] = {
    "Mcilroy": "McIlroy", "Macintyre": "MacIntyre", "Mcnealy": "McNealy",
    "Mccarty": "McCarty", "Aberg": "Åberg", "Hojgaard": "Højgaard",
    "Valimaki": "Välimäki", "Mckim": "McKim", "Dechambeau": "DeChambeau",
}


def _clean_rank(raw: str) -> int | None:
    match = re.search(r"\d+", raw)
    return int(match.group()) if match else None


def _clean_name(raw: str) -> str:
    name = raw.title().strip()
    for wrong, right in _NAME_CORRECTIONS.items():
        name = name.replace(wrong, right)
    return name


def _extract_country(flag_src: str) -> str:
    match = re.search(r"/([a-z-]+)\.svg$", flag_src or "")
    if match:
        return _COUNTRY_CODES.get(match.group(1), "Unknown")
    return "Unknown"


async def _scrape_owgr() -> List[Dict]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(
            "https://www.owgr.com/current-world-ranking",
            wait_until="networkidle",
            timeout=30000,
        )
        rows = await page.query_selector_all("table tbody tr")
        players = []
        for row in rows:
            cells = await row.query_selector_all("td")
            if len(cells) < 5:
                continue
            rank = _clean_rank(await cells[0].inner_text())
            if rank is None or rank > 50:
                continue
            name = _clean_name((await cells[4].inner_text()).strip())
            if not name:
                continue
            flag_img = await cells[3].query_selector("img")
            flag_src = await flag_img.get_attribute("src") if flag_img else ""
            country = _extract_country(flag_src)
            players.append({
                "rank": str(rank),
                "name": name,
                "country": country,
                "tour": "OGWR",
                "points": (await cells[5].inner_text()).strip() if len(cells) > 5 else None,
                "events": (await cells[7].inner_text()).strip() if len(cells) > 7 else None,
                "age": None,
            })
        await browser.close()
    return players


async def fetch_ogwr_with_gemini() -> List[Dict]:
    """Scrape top 50 OWGR players from owgr.com using Playwright."""
    print("🌐 Fetching OGWR page...")
    try:
        players = await _scrape_owgr()
        print(f"✅ Successfully scraped {len(players)} players from OWGR")
        return players
    except Exception as e:
        print(f"❌ Error scraping OWGR: {e}")
        return []


def fetch_ogwr_sync() -> List[Dict]:
    """Sync wrapper for use outside async contexts."""
    return asyncio.run(fetch_ogwr_with_gemini())
