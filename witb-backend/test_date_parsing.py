"""Test the date parsing logic directly."""

import asyncio
import re
from datetime import datetime
from bs4 import BeautifulSoup
from services.scraper_service import PGAClubTrackerScraper


async def test_date_parsing():
    """Test the date parsing with debug output."""
    scraper = PGAClubTrackerScraper(request_delay=0.5)
    url = "https://www.pgaclubtracker.com/players/ryan-fox-witb-whats-in-the-bag"
    
    html_content = await scraper._fetch_html(url)
    soup = BeautifulSoup(html_content, "lxml")
    
    print("🔍 Testing date parsing logic...\n")
    
    # Look for h1 tags specifically
    h1_tags = soup.find_all('h1')
    print(f"Found {len(h1_tags)} h1 tags:")
    
    for i, h1 in enumerate(h1_tags):
        text = h1.get_text().strip()
        print(f"  H1 #{i}: '{text}'")
        
        if "what's in" in text.lower() and "bag" in text.lower():
            print(f"    ✅ This is the WITB header!")
            
            # Check siblings
            current = h1
            for j in range(5):
                current = current.find_next_sibling()
                if not current:
                    break
                    
                sibling_text = current.get_text().strip()
                print(f"    Sibling {j+1} ({current.name}): '{sibling_text}'")
                
                # Test our patterns on this text
                date_patterns = [
                    r'([A-Z][a-z]+ +\d{1,2}, +\d{4})',  # "June  8, 2025" (spaces around comma)
                    r'([A-Z][a-z]+ \d{1,2}, \d{4})',     # "June 8, 2025" (standard format)
                    r'([A-Z][a-z]+ +\d{1,2} +\d{4})'     # "June  8  2025" (spaces instead of comma)
                ]
                
                for k, pattern in enumerate(date_patterns):
                    match = re.search(pattern, sibling_text)
                    if match:
                        date_str = match.group(1).strip()
                        normalized = re.sub(r'\s+', ' ', date_str)
                        print(f"      🎯 Pattern {k+1} matched: '{normalized}'")
                        
                        try:
                            if ',' in normalized:
                                parsed = datetime.strptime(normalized, "%B %d, %Y")
                            else:
                                parsed = datetime.strptime(normalized, "%B %d %Y")
                            print(f"      ✅ Parsed as: {parsed}")
                            return
                        except ValueError as e:
                            print(f"      ❌ Parse failed: {e}")
    
    print("\n❌ No WITB header found or no date in siblings")


if __name__ == "__main__":
    asyncio.run(test_date_parsing())