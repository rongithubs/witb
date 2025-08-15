"""Debug HTML structure to find the date below WITB header."""

import asyncio

from bs4 import BeautifulSoup

from services.scraper_service import PGAClubTrackerScraper


async def debug_html_structure():
    """Examine HTML structure to find where the date is located."""
    scraper = PGAClubTrackerScraper(request_delay=0.5)
    url = "https://www.pgaclubtracker.com/players/ryan-fox-witb-whats-in-the-bag"

    try:
        print(f"Fetching: {url}")
        html_content = await scraper._fetch_html(url)
        soup = BeautifulSoup(html_content, "lxml")

        print("\n🔍 Looking for 'What's in' header and nearby dates...\n")

        # Find all headers that might contain the title
        all_headers = soup.find_all(["h1", "h2", "h3", "div", "span", "p"])

        for i, header in enumerate(all_headers):
            header_text = header.get_text().strip()

            # Check if this looks like the main WITB header
            if "what's in" in header_text.lower() and (
                "bag" in header_text.lower() or "witb" in header_text.lower()
            ):
                print(f"🎯 FOUND WITB HEADER #{i}:")
                print(f"   Tag: {header.name}")
                print(f"   Class: {header.get('class', 'None')}")
                print(f"   Text: '{header_text}'")

                # Show the next few siblings to find the date
                print("\n   Next siblings:")
                current = header
                for j in range(10):
                    current = current.find_next_sibling()
                    if not current:
                        break
                    sibling_text = current.get_text().strip()
                    if sibling_text:  # Only show non-empty siblings
                        print(f"   [{j+1}] {current.name}: '{sibling_text[:100]}'")

                        # Check if this might be a date
                        import re

                        date_match = re.search(
                            r"([A-Z][a-z]+ \d{1,2}, \d{4})", sibling_text
                        )
                        if date_match:
                            print(f"       ⭐ DATE FOUND: {date_match.group(1)}")

                print("\n" + "=" * 60 + "\n")

        # Also search for any dates in the entire page
        print("🔍 All dates found on page:")
        text_content = soup.get_text()
        import re

        all_dates = re.findall(r"[A-Z][a-z]+ \d{1,2}, \d{4}", text_content)

        for date in set(all_dates):  # Remove duplicates
            print(f"   📅 {date}")

        if not all_dates:
            print("   ❌ No dates found in standard format")

            # Try other date formats
            other_formats = [
                r"\d{1,2}/\d{1,2}/\d{4}",  # MM/DD/YYYY
                r"\d{4}-\d{1,2}-\d{1,2}",  # YYYY-MM-DD
                r"[A-Z][a-z]+ \d{4}",  # Month Year
            ]

            for pattern in other_formats:
                matches = re.findall(pattern, text_content)
                if matches:
                    print(f"   Alternative format dates: {matches[:5]}")  # Show first 5

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_html_structure())
