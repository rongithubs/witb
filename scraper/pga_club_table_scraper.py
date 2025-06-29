#!/usr/bin/env python3
"""
PGA Club Tracker Table Scraper
Scrapes the current WITB table data from PGA Club Tracker.
Focuses on the main table with Club, Brand, Model, Loft/No., Shaft columns.
Ignores historical data below "All bags for {player name}".
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
import random

@dataclass
class WITBItem:
    """WITB Item following the schema structure from models.py"""
    category: str  # Club type (Driver, Iron, etc.)
    brand: str     # Equipment brand
    model: str     # Club model
    loft: Optional[str] = None    # Loft/No. column
    shaft: Optional[str] = None   # Shaft column

@dataclass
class PlayerWITB:
    """Player with current WITB items."""
    name: str
    country: str
    tour: str
    ranking: int
    witb_items: List[WITBItem]
    source_url: str

class PGAClubTableScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # Best practices: Rotate User-Agents
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        ]
        
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_player_data(self) -> List[Dict]:
        """Get the 3 players with valid URLs."""
        return [
            {
                'name': 'Scottie Scheffler',
                'ranking': 1,
                'country': 'United States',
                'tour': 'PGA Tour',
                'url': 'https://www.pgaclubtracker.com/players/scottie-scheffler-witb-whats-in-the-bag'
            },
            {
                'name': 'Rory McIlroy',
                'ranking': 2,
                'country': 'Northern Ireland', 
                'tour': 'PGA Tour',
                'url': 'https://www.pgaclubtracker.com/players/rory-mcilroy-witb-whats-in-the-bag'
            },
            {
                'name': 'Sepp Straka',
                'ranking': 4,
                'country': 'Austria',
                'tour': 'PGA Tour',
                'url': 'https://www.pgaclubtracker.com/players/sepp-straka-witb-whats-in-the-bag'
            }
        ]
    
    def rotate_user_agent(self):
        """Rotate User-Agent for best practices."""
        self.session.headers['User-Agent'] = random.choice(self.user_agents)
    
    def scrape_player_witb(self, url: str, player_info: Dict) -> Optional[PlayerWITB]:
        """Scrape current WITB data from a player's page."""
        try:
            self.rotate_user_agent()
            
            print(f"Scraping current WITB for {player_info['name']}...")
            print(f"URL: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the current WITB table (before "All bags for {player name}")
            witb_items = self.extract_current_witb_table(soup, player_info['name'])
            
            if not witb_items:
                print(f"  No current WITB table found for {player_info['name']}")
                return None
            
            player_witb = PlayerWITB(
                name=player_info['name'],
                country=player_info['country'],
                tour=player_info['tour'],
                ranking=player_info['ranking'],
                witb_items=witb_items,
                source_url=url
            )
            
            print(f"  ✓ Found {len(witb_items)} clubs in current bag")
            return player_witb
            
        except requests.RequestException as e:
            print(f"  ✗ Request error for {url}: {e}")
            return None
        except Exception as e:
            print(f"  ✗ Unexpected error scraping {player_info['name']}: {e}")
            return None
    
    def extract_current_witb_table(self, soup: BeautifulSoup, player_name: str) -> List[WITBItem]:
        """Extract the current WITB table, stopping at 'All bags for {player name}'."""
        witb_items = []
        
        # Find the cutoff point - look for text containing "All bags for {player_name}"
        cutoff_text = f"All bags for {player_name}"
        cutoff_element = None
        
        # Search for the cutoff text
        for element in soup.find_all(text=re.compile(r"All bags for", re.IGNORECASE)):
            if player_name.lower() in element.lower():
                cutoff_element = element.parent
                break
        
        print(f"  Looking for WITB table before: '{cutoff_text}'")
        if cutoff_element:
            print(f"  Found cutoff point")
        else:
            print(f"  No cutoff point found, processing entire page")
        
        # Find all tables on the page
        tables = soup.find_all('table')
        
        for table in tables:
            # Check if this table is before the cutoff point
            if cutoff_element and self.is_element_after_cutoff(table, cutoff_element):
                print(f"  Skipping table after cutoff point")
                continue
            
            # Check if this looks like a WITB table
            if self.is_witb_table(table):
                print(f"  Processing WITB table with {len(table.find_all('tr'))} rows")
                items = self.extract_items_from_witb_table(table)
                witb_items.extend(items)
                
                # If we found a good WITB table, we can stop looking
                if items:
                    break
        
        return witb_items
    
    def is_element_after_cutoff(self, element, cutoff_element) -> bool:
        """Check if an element appears after the cutoff element in the DOM."""
        try:
            # Get all elements in document order
            all_elements = cutoff_element.find_parent().find_all()
            
            cutoff_index = all_elements.index(cutoff_element)
            
            # Check if our element or any of its parents/children appear after cutoff
            element_family = [element] + list(element.find_all()) + list(element.parents)
            
            for elem in element_family:
                if elem in all_elements:
                    elem_index = all_elements.index(elem)
                    if elem_index > cutoff_index:
                        return True
            
            return False
        except (ValueError, AttributeError):
            # If we can't determine order, err on the side of inclusion
            return False
    
    def is_witb_table(self, table) -> bool:
        """Check if a table looks like a WITB table."""
        # Look for header row with expected columns
        header_row = table.find('tr')
        if not header_row:
            return False
        
        headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
        
        # Expected column names (flexible matching)
        expected_columns = ['club', 'brand', 'model', 'loft', 'shaft']
        
        # Check if we have at least 3 of the expected columns
        matches = 0
        for expected in expected_columns:
            for header in headers:
                if expected in header or header in expected:
                    matches += 1
                    break
        
        is_witb = matches >= 3
        print(f"    Table headers: {headers}")
        print(f"    Column matches: {matches}/5 -> {'WITB table' if is_witb else 'Not WITB table'}")
        
        return is_witb
    
    def extract_items_from_witb_table(self, table) -> List[WITBItem]:
        """Extract WITB items from a confirmed WITB table."""
        items = []
        rows = table.find_all('tr')
        
        if not rows:
            return items
        
        # Get header row to understand column positions
        header_row = rows[0]
        headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
        
        # Map column positions
        col_map = self.map_columns(headers)
        print(f"    Column mapping: {col_map}")
        
        # Process data rows
        for row in rows[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            
            if len(cells) < 3:  # Need at least 3 columns for meaningful data
                continue
            
            item = self.extract_item_from_row(cells, col_map)
            if item:
                items.append(item)
        
        print(f"    Extracted {len(items)} items from table")
        return items
    
    def map_columns(self, headers: List[str]) -> Dict[str, int]:
        """Map expected columns to their positions in the table."""
        col_map = {}
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            
            # Map column types
            if any(keyword in header_lower for keyword in ['club', 'category', 'type']):
                col_map['category'] = i
            elif 'brand' in header_lower:
                col_map['brand'] = i
            elif 'model' in header_lower:
                col_map['model'] = i
            elif any(keyword in header_lower for keyword in ['loft', 'no', 'number', 'degree']):
                col_map['loft'] = i
            elif 'shaft' in header_lower:
                col_map['shaft'] = i
        
        return col_map
    
    def extract_item_from_row(self, cells: List, col_map: Dict[str, int]) -> Optional[WITBItem]:
        """Extract a WITB item from a table row."""
        try:
            # Get values from mapped columns
            category = self.get_cell_value(cells, col_map.get('category'))
            brand = self.get_cell_value(cells, col_map.get('brand'))
            model = self.get_cell_value(cells, col_map.get('model'))
            loft = self.get_cell_value(cells, col_map.get('loft'))
            shaft = self.get_cell_value(cells, col_map.get('shaft'))
            
            # If we don't have explicit columns, try to parse from available data
            if not all([category, brand, model]):
                return self.parse_combined_data(cells)
            
            # Clean and validate data
            category = self.clean_category(category)
            brand = self.clean_text(brand)
            model = self.clean_text(model)
            loft = self.clean_text(loft)
            shaft = self.clean_text(shaft)
            
            if category and brand and model:
                return WITBItem(
                    category=category,
                    brand=brand,
                    model=model,
                    loft=loft,
                    shaft=shaft
                )
            
        except Exception as e:
            print(f"      Error extracting item from row: {e}")
        
        return None
    
    def get_cell_value(self, cells: List, col_index: Optional[int]) -> Optional[str]:
        """Get value from a specific cell index."""
        if col_index is None or col_index >= len(cells):
            return None
        
        return cells[col_index].get_text().strip()
    
    def parse_combined_data(self, cells: List) -> Optional[WITBItem]:
        """Parse WITB item when columns aren't clearly separated."""
        if len(cells) < 2:
            return None
        
        # Try to extract from first few cells
        text_data = []
        for cell in cells[:5]:  # Look at first 5 cells
            text = cell.get_text().strip()
            if text and text not in ['-', 'N/A', '']:
                text_data.append(text)
        
        if len(text_data) >= 2:
            # Assume first is category, second is brand/model combination
            category = self.clean_category(text_data[0])
            
            # Try to separate brand and model from second cell
            brand_model = text_data[1]
            brand, model = self.separate_brand_model(brand_model)
            
            # Additional data for loft/shaft
            loft = text_data[2] if len(text_data) > 2 else None
            shaft = text_data[3] if len(text_data) > 3 else None
            
            if category and brand and model:
                return WITBItem(
                    category=category,
                    brand=brand,
                    model=model,
                    loft=self.clean_text(loft),
                    shaft=self.clean_text(shaft)
                )
        
        return None
    
    def separate_brand_model(self, text: str) -> tuple:
        """Separate brand and model from combined text."""
        if not text:
            return None, None
        
        # Common golf brands
        brands = [
            'TaylorMade', 'Titleist', 'Callaway', 'Ping', 'Mizuno', 'Cobra', 
            'Cleveland', 'Wilson', 'Srixon', 'Vokey', 'Nike', 'Adams', 'Benross'
        ]
        
        text_lower = text.lower()
        
        for brand in brands:
            if brand.lower() in text_lower:
                # Find the brand position and extract model
                brand_pos = text_lower.find(brand.lower())
                model = text[brand_pos + len(brand):].strip()
                return brand, model
        
        # If no known brand found, assume first word is brand
        parts = text.split(None, 1)  # Split on whitespace, max 2 parts
        if len(parts) >= 2:
            return parts[0], parts[1]
        elif len(parts) == 1:
            return parts[0], ""
        
        return None, None
    
    def clean_category(self, text: Optional[str]) -> Optional[str]:
        """Clean and standardize category text."""
        if not text:
            return None
        
        text = text.strip().lower()
        
        # Standardize common categories
        category_map = {
            'dr': 'driver',
            'driver': 'driver',
            '3w': 'fairway wood',
            '5w': 'fairway wood',
            'wood': 'fairway wood',
            'fairway wood': 'fairway wood',
            'hybrid': 'hybrid',
            'hy': 'hybrid',
            'iron': 'iron',
            'irons': 'iron',
            'wedge': 'wedge',
            'pw': 'wedge',
            'gw': 'wedge',
            'sw': 'wedge',
            'lw': 'wedge',
            'putter': 'putter'
        }
        
        # Check for iron numbers (3-iron, 7-iron, etc.)
        iron_match = re.search(r'(\d+)[-\s]*iron', text)
        if iron_match:
            return f"{iron_match.group(1)}-iron"
        
        # Check for wedge degrees
        wedge_match = re.search(r'(\d+)[°\s]*wedge', text)
        if wedge_match:
            return f"{wedge_match.group(1)}° wedge"
        
        return category_map.get(text, text.title())
    
    def clean_text(self, text: Optional[str]) -> Optional[str]:
        """Clean general text fields."""
        if not text:
            return None
        
        text = text.strip()
        
        # Remove if it's just a dash or N/A
        if text in ['-', 'N/A', 'n/a', '']:
            return None
        
        return text
    
    def scrape_all_players(self) -> List[PlayerWITB]:
        """Scrape WITB data for all players."""
        players = self.get_player_data()
        results = []
        
        print(f"Scraping current WITB table data for {len(players)} players...")
        print("=" * 60)
        
        for i, player_info in enumerate(players, 1):
            print(f"\n{i}. Processing {player_info['name']}...")
            
            player_witb = self.scrape_player_witb(player_info['url'], player_info)
            
            if player_witb:
                results.append(player_witb)
            
            # Best practices: Respectful delay
            if i < len(players):  # Don't wait after the last player
                delay = random.uniform(2, 4)
                print(f"  Waiting {delay:.1f}s before next request...")
                time.sleep(delay)
        
        return results
    
    def save_results(self, results: List[PlayerWITB], filename: str = "current_witb_data.json"):
        """Save scraped results to files."""
        # Save as JSON
        output_data = []
        
        for player in results:
            player_data = {
                'name': player.name,
                'country': player.country,
                'tour': player.tour,
                'ranking': player.ranking,
                'source_url': player.source_url,
                'witb_items': []
            }
            
            for item in player.witb_items:
                item_data = {
                    'category': item.category,
                    'brand': item.brand,
                    'model': item.model,
                    'loft': item.loft,
                    'shaft': item.shaft
                }
                player_data['witb_items'].append(item_data)
            
            output_data.append(player_data)
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\nResults saved to {filename}")
        
        # Save as readable text
        text_filename = filename.replace('.json', '.txt')
        with open(text_filename, 'w') as f:
            f.write("Current WITB Table Data\n")
            f.write("=" * 30 + "\n\n")
            
            for player in results:
                f.write(f"Player: {player.name} (Rank: {player.ranking})\n")
                f.write(f"Country: {player.country}\n")
                f.write(f"Tour: {player.tour}\n")
                f.write(f"Source: {player.source_url}\n")
                f.write(f"Current Bag ({len(player.witb_items)} clubs):\n")
                
                for item in player.witb_items:
                    f.write(f"  • {item.category}: {item.brand} {item.model}")
                    if item.loft:
                        f.write(f" ({item.loft})")
                    if item.shaft:
                        f.write(f" - Shaft: {item.shaft}")
                    f.write("\n")
                
                f.write("-" * 50 + "\n\n")
        
        print(f"Text version saved to {text_filename}")
    
    def print_summary(self, results: List[PlayerWITB]):
        """Print summary of scraping results."""
        total_clubs = sum(len(player.witb_items) for player in results)
        
        print(f"\n" + "=" * 50)
        print("CURRENT WITB SCRAPING SUMMARY")
        print("=" * 50)
        print(f"Players processed: {len(results)}")
        print(f"Total clubs in current bags: {total_clubs}")
        print(f"Average clubs per player: {total_clubs/len(results):.1f}" if results else 0)
        
        for player in results:
            print(f"  • {player.name}: {len(player.witb_items)} clubs")


def main():
    """Main function to run the current WITB table scraper."""
    scraper = PGAClubTableScraper()
    
    # Scrape current WITB data for all players
    results = scraper.scrape_all_players()
    
    # Save and summarize results
    if results:
        scraper.save_results(results)
        scraper.print_summary(results)
    else:
        print("No current WITB data was successfully scraped.")


if __name__ == "__main__":
    main()