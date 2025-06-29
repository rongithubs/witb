#!/usr/bin/env python3
"""
WITB Table Scraper Module
Scrapes WITB data from PGA Club Tracker pages.
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import random
from typing import List, Dict, Optional
from witb_models import WITBItem, PlayerWITB, PlayerInfo

class WITBScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # User agents for rotation
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
    
    def rotate_user_agent(self):
        """Rotate User-Agent for best practices."""
        self.session.headers['User-Agent'] = random.choice(self.user_agents)
    
    def scrape_player_witb(self, player: PlayerInfo) -> Optional[PlayerWITB]:
        """Scrape WITB data for a single player."""
        try:
            self.rotate_user_agent()
            
            response = self.session.get(player.url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            witb_items = self.extract_current_witb_table(soup, player.name)
            
            if not witb_items:
                return None
            
            return PlayerWITB(
                name=player.name,
                country=player.country,
                tour=player.tour,
                ranking=player.ranking,
                witb_items=witb_items,
                source_url=player.url,
                player_id=player.id
            )
            
        except Exception:
            return None
    
    def extract_current_witb_table(self, soup: BeautifulSoup, player_name: str) -> List[WITBItem]:
        """Extract the current WITB table, stopping at 'All bags for {player name}'."""
        witb_items = []
        
        # Find the cutoff point
        cutoff_element = None
        for element in soup.find_all(string=re.compile(r"All bags for", re.IGNORECASE)):
            if player_name.lower() in element.lower():
                cutoff_element = element.parent
                break
        
        # Find all tables on the page
        tables = soup.find_all('table')
        
        for table in tables:
            # Check if this table is before the cutoff point
            if cutoff_element and self._is_element_after_cutoff(table, cutoff_element):
                continue
            
            # Check if this looks like a WITB table
            if self._is_witb_table(table):
                items = self._extract_items_from_witb_table(table)
                witb_items.extend(items)
                
                # If we found a good WITB table, stop looking
                if items:
                    break
        
        return witb_items
    
    def _is_element_after_cutoff(self, element, cutoff_element) -> bool:
        """Check if an element appears after the cutoff element in the DOM."""
        try:
            all_elements = cutoff_element.find_parent().find_all()
            cutoff_index = all_elements.index(cutoff_element)
            
            element_family = [element] + list(element.find_all()) + list(element.parents)
            
            for elem in element_family:
                if elem in all_elements:
                    elem_index = all_elements.index(elem)
                    if elem_index > cutoff_index:
                        return True
            
            return False
        except (ValueError, AttributeError):
            return False
    
    def _is_witb_table(self, table) -> bool:
        """Check if a table looks like a WITB table."""
        header_row = table.find('tr')
        if not header_row:
            return False
        
        headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
        expected_columns = ['club', 'brand', 'model', 'loft', 'shaft']
        
        matches = 0
        for expected in expected_columns:
            for header in headers:
                if expected in header or header in expected:
                    matches += 1
                    break
        
        return matches >= 3
    
    def _extract_items_from_witb_table(self, table) -> List[WITBItem]:
        """Extract WITB items from a confirmed WITB table."""
        items = []
        rows = table.find_all('tr')
        
        if not rows:
            return items
        
        # Get header row to understand column positions
        header_row = rows[0]
        headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
        
        # Map column positions
        col_map = self._map_columns(headers)
        
        # Process data rows
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            
            if len(cells) < 3:
                continue
            
            item = self._extract_item_from_row(cells, col_map)
            if item:
                items.append(item)
        
        return items
    
    def _map_columns(self, headers: List[str]) -> Dict[str, int]:
        """Map expected columns to their positions in the table."""
        col_map = {}
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            
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
    
    def _extract_item_from_row(self, cells: List, col_map: Dict[str, int]) -> Optional[WITBItem]:
        """Extract a WITB item from a table row."""
        try:
            category = self._get_cell_value(cells, col_map.get('category'))
            brand = self._get_cell_value(cells, col_map.get('brand'))
            model = self._get_cell_value(cells, col_map.get('model'))
            loft = self._get_cell_value(cells, col_map.get('loft'))
            shaft = self._get_cell_value(cells, col_map.get('shaft'))
            
            # If we don't have explicit columns, try to parse from available data
            if not all([category, brand, model]):
                return self._parse_combined_data(cells)
            
            # Clean and validate data
            category = self._clean_category(category)
            brand = self._clean_text(brand)
            model = self._clean_text(model)
            loft = self._clean_text(loft)
            shaft = self._clean_text(shaft)
            
            if category and brand and model:
                return WITBItem(
                    category=category,
                    brand=brand,
                    model=model,
                    loft=loft,
                    shaft=shaft
                )
            
        except Exception:
            pass
        
        return None
    
    def _get_cell_value(self, cells: List, col_index: Optional[int]) -> Optional[str]:
        """Get value from a specific cell index."""
        if col_index is None or col_index >= len(cells):
            return None
        return cells[col_index].get_text().strip()
    
    def _parse_combined_data(self, cells: List) -> Optional[WITBItem]:
        """Parse WITB item when columns aren't clearly separated."""
        if len(cells) < 2:
            return None
        
        text_data = []
        for cell in cells[:5]:
            text = cell.get_text().strip()
            if text and text not in ['-', 'N/A', '']:
                text_data.append(text)
        
        if len(text_data) >= 2:
            category = self._clean_category(text_data[0])
            brand_model = text_data[1]
            brand, model = self._separate_brand_model(brand_model)
            
            loft = text_data[2] if len(text_data) > 2 else None
            shaft = text_data[3] if len(text_data) > 3 else None
            
            if category and brand and model:
                return WITBItem(
                    category=category,
                    brand=brand,
                    model=model,
                    loft=self._clean_text(loft),
                    shaft=self._clean_text(shaft)
                )
        
        return None
    
    def _separate_brand_model(self, text: str) -> tuple:
        """Separate brand and model from combined text."""
        if not text:
            return None, None
        
        brands = [
            'TaylorMade', 'Titleist', 'Callaway', 'Ping', 'Mizuno', 'Cobra', 
            'Cleveland', 'Wilson', 'Srixon', 'Vokey', 'Nike', 'Adams', 'Benross'
        ]
        
        text_lower = text.lower()
        
        for brand in brands:
            if brand.lower() in text_lower:
                brand_pos = text_lower.find(brand.lower())
                model = text[brand_pos + len(brand):].strip()
                return brand, model
        
        # If no known brand found, assume first word is brand
        parts = text.split(None, 1)
        if len(parts) >= 2:
            return parts[0], parts[1]
        elif len(parts) == 1:
            return parts[0], ""
        
        return None, None
    
    def _clean_category(self, text: Optional[str]) -> Optional[str]:
        """Clean and standardize category text."""
        if not text:
            return None
        
        text = text.strip().lower()
        
        category_map = {
            'dr': 'Driver',
            'driver': 'Driver',
            '3w': 'Fairway Wood',
            '5w': 'Fairway Wood',
            'wood': 'Fairway Wood',
            'fairway wood': 'Fairway Wood',
            'hybrid': 'Hybrid',
            'hy': 'Hybrid',
            'iron': 'Iron',
            'irons': 'Iron',
            'wedge': 'Wedge',
            'pw': 'Wedge',
            'gw': 'Wedge',
            'sw': 'Wedge',
            'lw': 'Wedge',
            'putter': 'Putter'
        }
        
        # Check for iron numbers
        iron_match = re.search(r'(\d+)[-\s]*iron', text)
        if iron_match:
            return f"{iron_match.group(1)}-Iron"
        
        # Check for wedge degrees
        wedge_match = re.search(r'(\d+)[°\s]*wedge', text)
        if wedge_match:
            return f"{wedge_match.group(1)}° Wedge"
        
        # Check for wood numbers
        wood_match = re.search(r'(\d+)[-\s]*wood', text)
        if wood_match:
            return f"{wood_match.group(1)}-Wood"
        
        return category_map.get(text, text.title())
    
    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        """Clean general text fields."""
        if not text:
            return None
        
        text = text.strip()
        
        if text in ['-', 'N/A', 'n/a', '']:
            return None
        
        return text
    
    def scrape_multiple_players(self, players: List[PlayerInfo], verbose: bool = True) -> List[PlayerWITB]:
        """Scrape WITB data for multiple players."""
        results = []
        
        if verbose:
            print(f"Scraping WITB data for {len(players)} players...")
            print("=" * 60)
        
        for i, player in enumerate(players, 1):
            if verbose:
                print(f"{i:2d}. {player.name:<25} ", end="", flush=True)
            
            player_witb = self.scrape_player_witb(player)
            
            if player_witb:
                results.append(player_witb)
                if verbose:
                    print(f"✓ {len(player_witb.witb_items)} items")
            else:
                if verbose:
                    print("✗ No data")
            
            # Respectful delays
            if i % 10 == 0:
                delay = random.uniform(2, 3)
                if verbose:
                    print(f"    Pausing {delay:.1f}s...")
                time.sleep(delay)
            else:
                time.sleep(random.uniform(0.5, 1))
        
        return results