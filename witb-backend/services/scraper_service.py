"""PGA Club Tracker HTML scraper service following CLAUDE.md C-4."""

import re
import asyncio
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

import aiohttp
from bs4 import BeautifulSoup


@dataclass
class EquipmentItem:
    """Equipment item data structure."""

    category: str
    brand: str
    model: str
    loft: Optional[str] = None
    shaft: Optional[str] = None


@dataclass
class WITBData:
    """Complete WITB data structure."""

    last_updated: Optional[datetime]
    equipment: List[EquipmentItem]
    source_url: str


class PGAClubTrackerScraper:
    """Scraper for PGA Club Tracker WITB pages."""

    def __init__(self, request_delay: float = 2.0):
        """
        Initialize scraper with rate limiting.

        Args:
            request_delay: Seconds to wait between requests (default: 2.0)
        """
        self.request_delay = request_delay
        self.user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )

    async def scrape_player_witb(self, url: str) -> WITBData:
        """
        Scrape WITB data from PGA Club Tracker player page.

        Args:
            url: Complete URL to player's WITB page

        Returns:
            WITBData with parsed equipment and last updated date

        Raises:
            aiohttp.ClientError: If HTTP request fails
            ValueError: If required data cannot be parsed
        """
        html_content = await self._fetch_html(url)

        last_updated = self._parse_last_updated(html_content)
        equipment = self._parse_equipment_table(html_content)

        if not equipment:
            raise ValueError(f"No equipment data found for URL: {url}")

        return WITBData(last_updated=last_updated, equipment=equipment, source_url=url)

    async def _fetch_html(self, url: str) -> str:
        """Fetch HTML content with proper headers and rate limiting."""
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status != 200:
                    raise aiohttp.ClientError(f"HTTP {response.status} for URL: {url}")

                html_content = await response.text()

        # Rate limiting
        await asyncio.sleep(self.request_delay)

        return html_content

    def _parse_last_updated(self, html_content: str) -> Optional[datetime]:
        """Parse last updated date from HTML content - specifically the date below the WITB header."""
        soup = BeautifulSoup(html_content, "lxml")

        # First, try to find the date right below "What's in [name]'s bag?" header
        # Look for h1 or h2 elements containing "What's in" and "bag"
        header_selectors = [
            'h1:contains("What\'s in")',
            'h2:contains("What\'s in")', 
            'h1:contains("bag")',
            'h2:contains("bag")',
            '[class*="title"]:contains("What\'s in")',
            '[class*="header"]:contains("What\'s in")'
        ]
        
        # Since BeautifulSoup doesn't support :contains, we'll search manually
        potential_headers = soup.find_all(['h1', 'h2', 'div', 'span'], 
                                        class_=re.compile(r'(title|header|heading)', re.I))
        
        # Also check all h1/h2 elements regardless of class
        potential_headers.extend(soup.find_all(['h1', 'h2']))
        
        for header in potential_headers:
            header_text = header.get_text().strip().lower()
            if "what's in" in header_text and "bag" in header_text:
                # Found the header, now look for the date in the next few siblings
                current = header
                for _ in range(5):  # Check next 5 siblings
                    current = current.find_next_sibling()
                    if not current:
                        break
                    
                    text = current.get_text().strip()
                    # Look for date patterns in this sibling (with and without comma, with flexible spacing)
                    date_patterns = [
                        r'([A-Z][a-z]+ +\d{1,2}, +\d{4})',  # "June  8, 2025" (spaces around comma)
                        r'([A-Z][a-z]+ \d{1,2}, \d{4})',     # "June 8, 2025" (standard format)
                        r'([A-Z][a-z]+ +\d{1,2} +\d{4})'     # "June  8  2025" (spaces instead of comma)
                    ]
                    
                    for pattern in date_patterns:
                        date_match = re.search(pattern, text)
                        if date_match:
                            date_str = date_match.group(1).strip()
                            # Normalize the date string by removing extra spaces
                            date_str = re.sub(r'\s+', ' ', date_str)
                            
                            # Try different formats
                            try:
                                # Try with comma first
                                if ',' in date_str:
                                    return datetime.strptime(date_str, "%B %d, %Y")
                                else:
                                    # Try without comma
                                    return datetime.strptime(date_str, "%B %d %Y")
                            except ValueError:
                                try:
                                    if ',' in date_str:
                                        return datetime.strptime(date_str, "%b %d, %Y")
                                    else:
                                        return datetime.strptime(date_str, "%b %d %Y")
                                except ValueError:
                                    continue
        
        # Fallback: search entire page for date patterns
        text_content = soup.get_text()
        fallback_patterns = [
            r"[Uu]pdated[:\s]*([A-Z][a-z]+ \d{1,2}, \d{4})",
            r"[Ll]ast updated[:\s]*([A-Z][a-z]+ \d{1,2}, \d{4})",
            r"([A-Z][a-z]+ \d{1,2}, \d{4})",  # With comma
            r"([A-Z][a-z]+ +\d{1,2} +\d{4})",  # Without comma (spaces)
        ]

        for pattern in fallback_patterns:
            match = re.search(pattern, text_content)
            if match:
                date_str = match.group(1).strip()
                date_str = re.sub(r'\s+', ' ', date_str)  # Normalize spaces
                
                try:
                    if ',' in date_str:
                        return datetime.strptime(date_str, "%B %d, %Y")
                    else:
                        return datetime.strptime(date_str, "%B %d %Y")
                except ValueError:
                    try:
                        if ',' in date_str:
                            return datetime.strptime(date_str, "%b %d, %Y")
                        else:
                            return datetime.strptime(date_str, "%b %d %Y")
                    except ValueError:
                        continue

        # If no date found, return None to indicate we couldn't find the bag update date
        return None

    def _parse_equipment_table(self, html_content: str) -> List[EquipmentItem]:
        """Parse equipment table from HTML content."""
        soup = BeautifulSoup(html_content, "lxml")
        equipment_items = []

        # Find the equipment table - try multiple selectors
        table_selectors = [
            "table",  # Generic table
            "table.equipment",  # Specific class
            "div.equipment table",  # Table inside equipment div
            ".witb-table table",  # Alternative class structure
        ]

        table = None
        for selector in table_selectors:
            table = soup.select_one(selector)
            if table:
                break

        if not table:
            return equipment_items

        # Find table rows, skip header row
        rows = table.find_all("tr")[1:]  # Skip header

        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 3:  # Minimum: club, brand, model
                category = self._clean_text(cells[0].get_text())
                brand = self._clean_text(cells[1].get_text())
                model = self._clean_text(cells[2].get_text())

                # Optional fields
                loft = self._clean_text(cells[3].get_text()) if len(cells) > 3 else None
                shaft = (
                    self._clean_text(cells[4].get_text()) if len(cells) > 4 else None
                )

                if category and brand and model:
                    equipment_items.append(
                        EquipmentItem(
                            category=category,
                            brand=brand,
                            model=model,
                            loft=loft,
                            shaft=shaft,
                        )
                    )

        return equipment_items

    def _clean_text(self, text: str) -> Optional[str]:
        """Clean and normalize text content."""
        if not text:
            return None

        # Remove extra whitespace and normalize
        cleaned = re.sub(r"\s+", " ", text.strip())

        # Return None for empty strings
        return cleaned if cleaned else None
