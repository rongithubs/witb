"""Debug Ryan Fox scraping issue."""

import asyncio

from services.scraper_service import PGAClubTrackerScraper


async def debug_ryan_fox():
    """Test Ryan Fox URL parsing directly."""
    scraper = PGAClubTrackerScraper(request_delay=0.5)
    url = "https://www.pgaclubtracker.com/players/ryan-fox-witb-whats-in-the-bag"

    try:
        print(f"Testing URL: {url}")

        # Fetch the HTML directly
        html_content = await scraper._fetch_html(url)
        print(f"✅ HTML fetched successfully ({len(html_content)} characters)")

        # Test date parsing
        last_updated = scraper._parse_last_updated(html_content)
        print(f"📅 Last updated: {last_updated}")

        # Test equipment parsing - this is the key test
        equipment = scraper._parse_equipment_table(html_content)
        print(f"🏌️ Equipment found: {len(equipment)} items")

        if equipment:
            for i, item in enumerate(equipment, 1):
                print(f"  {i}. {item.category}: {item.brand} {item.model}")
                if item.loft:
                    print(f"     Loft: {item.loft}")
                if item.shaft:
                    print(f"     Shaft: {item.shaft}")
        else:
            print("❌ NO EQUIPMENT FOUND - This is the problem!")

            # Let's debug the table parsing
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, "lxml")

            print("\n🔍 Debugging table detection:")

            # Try our selectors
            selectors = [
                "table",
                "table.equipment",
                "div.equipment table",
                ".witb-table table",
            ]

            for selector in selectors:
                tables = soup.select(selector)
                print(f"  Selector '{selector}': Found {len(tables)} tables")

            # Find ALL tables
            all_tables = soup.find_all("table")
            print(f"  Total tables in page: {len(all_tables)}")

            if all_tables:
                print("\n📋 First table structure:")
                first_table = all_tables[0]
                print(f"  Table classes: {first_table.get('class', 'None')}")
                print(
                    f"  Parent div classes: {first_table.parent.get('class', 'None') if first_table.parent else 'None'}"
                )

                # Check table headers
                headers = first_table.find_all("th")
                if headers:
                    print(f"  Headers: {[th.get_text().strip() for th in headers]}")

                # Check first few rows
                rows = first_table.find_all("tr")
                print(f"  Total rows: {len(rows)}")
                if len(rows) > 1:
                    first_data_row = rows[1]  # Skip header
                    cells = first_data_row.find_all(["td", "th"])
                    print(
                        f"  First row cells: {[cell.get_text().strip() for cell in cells]}"
                    )

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_ryan_fox())
