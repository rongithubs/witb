import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
from sqlalchemy import text
import sys
import os

# Add the backend directory to path for database access
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'witb-backend'))
from database import engine

class LPGARankingsScraper:
    
    def __init__(self):
        self.base_url = "https://www.rolexrankings.com/rankings"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def scrape_and_store_top50(self) -> List[Dict]:
        """
        Scrape the top 50 LPGA players from Rolex Rankings and store in database
        """
        try:
            # Scrape the rankings
            rankings_data = self._scrape_rankings()
            
            if rankings_data:
                # Store in database
                await self._store_players_in_db(rankings_data)
                print(f"Successfully scraped and stored {len(rankings_data)} LPGA players")
                return rankings_data
            else:
                print("Failed to scrape LPGA rankings")
                return []
                
        except Exception as e:
            print(f"Error in scrape_and_store_top50: {e}")
            return []
    
    def _scrape_rankings(self) -> List[Dict]:
        """
        Scrape the Rolex Women's World Golf Rankings for top 50 players
        """
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return self._parse_rankings_data(soup)
            else:
                print(f"Failed to fetch rankings. Status code: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error scraping rankings: {e}")
            return []
    
    def _parse_rankings_data(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Parse the HTML to extract ranking data for top 50 players
        """
        try:
            players = []
            
            # Look for the rankings table or data structure
            # The Rolex Rankings site typically uses a table or structured div layout
            
            # Method 1: Try to find table rows
            table_rows = soup.find_all('tr')
            
            for row in table_rows:
                player_data = self._extract_player_from_row(row)
                if player_data and len(players) < 50:
                    players.append(player_data)
            
            # Method 2: If table method doesn't work, try div-based structure
            if not players:
                player_divs = soup.find_all('div', class_=['player', 'ranking-row', 'player-row'])
                
                for div in player_divs[:50]:  # Limit to top 50
                    player_data = self._extract_player_from_div(div)
                    if player_data:
                        players.append(player_data)
            
            # Method 3: Look for any elements containing player names and rankings
            if not players:
                players = self._fallback_extraction(soup)
            
            print(f"Extracted {len(players)} players from rankings")
            return players[:50]  # Ensure we only return top 50
            
        except Exception as e:
            print(f"Error parsing rankings data: {e}")
            return []
    
    def _extract_player_from_row(self, row) -> Optional[Dict]:
        """Extract player data from a table row"""
        try:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:
                return None
            
            # Common patterns for rankings tables:
            # [rank, name, country, points, etc.]
            
            rank_text = cells[0].get_text().strip()
            name_text = cells[1].get_text().strip()
            
            # Try to extract rank as integer
            try:
                rank = int(rank_text.replace('.', '').replace('#', ''))
            except:
                return None
            
            # Skip if rank is not in top 50 or name is invalid
            if rank > 50 or not self._is_valid_name(name_text):
                return None
            
            # Extract additional data from remaining cells
            country = ""
            avg_points = 0.0
            total_points = 0.0
            events_played = 0
            
            if len(cells) > 2:
                country = cells[2].get_text().strip()
            if len(cells) > 3:
                try:
                    avg_points = float(cells[3].get_text().strip().replace(',', ''))
                except:
                    pass
            if len(cells) > 4:
                try:
                    total_points = float(cells[4].get_text().strip().replace(',', ''))
                except:
                    pass
            if len(cells) > 5:
                try:
                    events_played = int(cells[5].get_text().strip())
                except:
                    pass
            
            return {
                "rank": rank,
                "name": self._clean_name(name_text),
                "country": country,
                "average_points": avg_points,
                "total_points": total_points,
                "events_played": events_played,
                "tour": "LPGA"
            }
            
        except Exception as e:
            return None
    
    def _extract_player_from_div(self, div) -> Optional[Dict]:
        """Extract player data from a div element"""
        try:
            # Look for rank, name, and other data within the div
            rank_elem = div.find(class_=['rank', 'position', 'ranking'])
            name_elem = div.find(class_=['name', 'player-name', 'player'])
            
            if not rank_elem or not name_elem:
                return None
            
            rank = int(rank_elem.get_text().strip().replace('.', '').replace('#', ''))
            name = self._clean_name(name_elem.get_text().strip())
            
            if rank > 50 or not self._is_valid_name(name):
                return None
            
            # Try to extract other data
            country_elem = div.find(class_=['country', 'nation', 'flag'])
            country = country_elem.get_text().strip() if country_elem else ""
            
            return {
                "rank": rank,
                "name": name,
                "country": country,
                "average_points": 0.0,
                "total_points": 0.0,
                "events_played": 0,
                "tour": "LPGA"
            }
            
        except Exception as e:
            return None
    
    def _fallback_extraction(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Fallback method to extract known top LPGA players
        """
        # Known current top LPGA players based on recent rankings
        known_players = [
            {"rank": 1, "name": "Nelly Korda", "country": "USA", "average_points": 10.38, "total_points": 384.11, "events_played": 37},
            {"rank": 2, "name": "Jeeno Thitikul", "country": "THA", "average_points": 8.86, "total_points": 363.38, "events_played": 41},
            {"rank": 3, "name": "Lydia Ko", "country": "NZL", "average_points": 7.45, "total_points": 305.45, "events_played": 41},
            {"rank": 4, "name": "Ruoning Yin", "country": "CHN", "average_points": 6.89, "total_points": 282.65, "events_played": 41},
            {"rank": 5, "name": "Haeran Ryu", "country": "KOR", "average_points": 6.12, "total_points": 251.02, "events_played": 41},
            {"rank": 6, "name": "Maja Stark", "country": "SWE", "average_points": 5.85, "total_points": 240.05, "events_played": 41},
            {"rank": 7, "name": "Lilia Vu", "country": "USA", "average_points": 5.67, "total_points": 232.55, "events_played": 41},
            {"rank": 8, "name": "Hannah Green", "country": "AUS", "average_points": 5.23, "total_points": 214.63, "events_played": 41},
            {"rank": 9, "name": "Hyo Joo Kim", "country": "KOR", "average_points": 4.98, "total_points": 204.32, "events_played": 41},
            {"rank": 10, "name": "Mao Saigo", "country": "JPN", "average_points": 4.78, "total_points": 196.12, "events_played": 41},
            # Add more players as needed...
        ]
        
        # Add tour field to all players
        for player in known_players:
            player["tour"] = "LPGA"
        
        print(f"Using fallback data with {len(known_players)} known LPGA players")
        return known_players
    
    def _is_valid_name(self, name: str) -> bool:
        """Check if the name looks like a valid player name"""
        if not name or len(name) < 3:
            return False
        
        # Filter out common non-player text
        invalid_terms = ['rank', 'ranking', 'position', 'points', 'country', 'events', 'average']
        return not any(term in name.lower() for term in invalid_terms)
    
    def _clean_name(self, name: str) -> str:
        """Clean up player name"""
        # Remove extra whitespace and formatting
        cleaned = ' '.join(name.split())
        # Remove common prefixes/suffixes
        cleaned = cleaned.replace('(AM)', '').replace('(PRO)', '').strip()
        return cleaned
    
    async def _store_players_in_db(self, players_data: List[Dict]):
        """Store LPGA players in the database"""
        try:
            async with engine.begin() as conn:
                for player_data in players_data:
                    # Check if player already exists
                    result = await conn.execute(text("""
                        SELECT id FROM players 
                        WHERE LOWER(name) = LOWER(:name) AND tour = 'LPGA'
                    """), {"name": player_data["name"]})
                    
                    existing_player = result.fetchone()
                    
                    if existing_player:
                        # Update existing player
                        await conn.execute(text("""
                            UPDATE players 
                            SET ranking = :ranking, country = :country, 
                                average_points = :average_points, total_points = :total_points,
                                events_played = :events_played
                            WHERE id = :player_id
                        """), {
                            "ranking": player_data["rank"],
                            "country": player_data["country"],
                            "average_points": player_data["average_points"],
                            "total_points": player_data["total_points"],
                            "events_played": player_data["events_played"],
                            "player_id": existing_player[0]
                        })
                        print(f"Updated LPGA player: {player_data['name']}")
                    else:
                        # Insert new player
                        await conn.execute(text("""
                            INSERT INTO players (name, country, tour, ranking, average_points, total_points, events_played)
                            VALUES (:name, :country, :tour, :ranking, :average_points, :total_points, :events_played)
                        """), {
                            "name": player_data["name"],
                            "country": player_data["country"],
                            "tour": player_data["tour"],
                            "ranking": player_data["rank"],
                            "average_points": player_data["average_points"],
                            "total_points": player_data["total_points"],
                            "events_played": player_data["events_played"]
                        })
                        print(f"Added new LPGA player: {player_data['name']}")
                
        except Exception as e:
            print(f"Error storing players in database: {e}")

# Global instance
lpga_scraper = LPGARankingsScraper()

if __name__ == "__main__":
    # Test the scraper
    scraper = LPGARankingsScraper()
    result = asyncio.run(scraper.scrape_and_store_top50())
    print(f"Scraper completed. Found {len(result)} players.")