import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import Dict, Optional, List
import asyncio
from sqlalchemy import text
import sys
import os

# Add the backend directory to path for database access
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'witb-backend'))
from database import engine

class SimpleTournamentScraper:
    
    async def scrape_and_store_winner(self) -> Dict[str, str]:
        """
        Scrape the most recent PGA tournament winner and their WITB, store in Supabase
        """
        try:
            # First try to scrape the winner
            winner_data = self._scrape_recent_winner()
            
            # If we found a winner, try to get their WITB data
            if winner_data and winner_data.get("winner") != "Not found":
                # Check if this winner exists in our players database
                witb_data = await self._get_winner_witb(winner_data["winner"])
                winner_data["witb_items"] = witb_data
                
                # Store in database
                await self._store_winner_in_db(winner_data)
                return winner_data
            
            # If scraping fails, get from database
            return await self._get_winner_from_db()
            
        except Exception as e:
            print(f"Error in scrape_and_store_winner: {e}")
            return await self._get_winner_from_db()
    
    def _scrape_recent_winner(self) -> Dict[str, str]:
        """
        Use simple requests + BeautifulSoup to scrape recent winner (most cost efficient)
        """
        try:
            # Try ESPN Golf first (usually has clean HTML)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            urls_to_try = [
                "https://www.espn.com/golf/schedule",
                "https://www.golf.com/news/",
                "https://www.golfdigest.com/latest"
            ]
            
            for url in urls_to_try:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        winner_data = self._parse_for_winner(soup, url)
                        if winner_data and winner_data.get("winner") != "Not found":
                            return winner_data
                except Exception as e:
                    print(f"Error scraping {url}: {e}")
                    continue
            
            return {"winner": "Not found", "tournament": "", "date": "", "score": ""}
            
        except Exception as e:
            print(f"Error in _scrape_recent_winner: {e}")
            return {"winner": "Not found", "tournament": "", "date": "", "score": ""}
    
    async def _get_winner_witb(self, winner_name: str) -> List[Dict[str, str]]:
        """
        Get WITB data for the tournament winner from our database
        """
        try:
            async with engine.begin() as conn:
                # Search for the player in our database (fuzzy match)
                result = await conn.execute(text("""
                    SELECT p.id, p.name, w.category, w.brand, w.model, w.loft, w.shaft
                    FROM players p
                    LEFT JOIN witb_items w ON p.id = w.player_id
                    WHERE LOWER(p.name) LIKE LOWER(:name)
                    OR LOWER(p.name) LIKE LOWER(:fuzzy_name)
                    ORDER BY w.category
                """), {
                    "name": f"%{winner_name}%",
                    "fuzzy_name": f"%{winner_name.split()[0]}%{winner_name.split()[-1]}%"
                })
                
                rows = result.fetchall()
                
                if rows:
                    witb_items = []
                    player_name = rows[0][1]  # Get the actual player name from DB
                    
                    for row in rows:
                        if row[2]:  # If there's equipment data
                            witb_items.append({
                                "category": row[2],
                                "brand": row[3],
                                "model": row[4],
                                "loft": row[5] or "",
                                "shaft": row[6] or ""
                            })
                    
                    print(f"Found WITB data for {player_name}: {len(witb_items)} items")
                    return witb_items
                else:
                    print(f"No WITB data found for {winner_name}")
                    return []
                    
        except Exception as e:
            print(f"Error getting WITB data for {winner_name}: {e}")
            return []
    
    def _parse_for_winner(self, soup: BeautifulSoup, source_url: str) -> Dict[str, str]:
        """
        Parse HTML to find recent tournament winner
        """
        try:
            # Get all text content
            page_text = soup.get_text().lower()
            
            # Look for recent winner patterns in the text
            winner_patterns = [
                r'(\w+\s+\w+)\s+(?:wins?|won|captures?|takes?)\s+(?:the\s+)?([^,.]*(?:championship|open|classic|invitational|tournament))',
                r'([^,.]*(?:championship|open|classic|invitational|tournament))[^:]*(?:winner|champion)[^:]*:\s*(\w+\s+\w+)',
                r'(\w+\s+\w+)\s+(?:claims?|secures?)\s+(?:victory at\s+)?([^,.]*(?:championship|open|classic|invitational))'
            ]
            
            for pattern in winner_patterns:
                matches = re.finditer(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    group1, group2 = match.groups()
                    
                    # Clean up the groups
                    group1 = group1.strip()
                    group2 = group2.strip()
                    
                    # Determine which is the winner and which is the tournament
                    if self._looks_like_name(group1):
                        winner = self._clean_name(group1)
                        tournament = self._clean_tournament_name(group2)
                    else:
                        winner = self._clean_name(group2)
                        tournament = self._clean_tournament_name(group1)
                    
                    # Skip if winner looks suspicious
                    if self._is_valid_winner(winner):
                        return {
                            "winner": winner,
                            "tournament": tournament,
                            "date": datetime.now().strftime("%B %d, %Y"),
                            "score": ""
                        }
            
            # If no patterns match, look for specific known tournaments
            return self._look_for_specific_tournaments(soup)
            
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            return {"winner": "Not found", "tournament": "", "date": "", "score": ""}
    
    def _looks_like_name(self, text: str) -> bool:
        """Check if text looks like a person's name"""
        words = text.strip().split()
        return (len(words) >= 2 and len(words) <= 3 and
                all(word.replace("'", "").replace("-", "").isalpha() for word in words) and
                all(len(word) >= 2 for word in words))
    
    def _clean_name(self, name: str) -> str:
        """Clean up player name"""
        # Remove common prefixes/suffixes
        cleaned = re.sub(r'\b(wins?|won|captures?|takes?|claims?)\b', '', name, flags=re.IGNORECASE)
        cleaned = cleaned.strip()
        return ' '.join(word.capitalize() for word in cleaned.split())
    
    def _clean_tournament_name(self, tournament: str) -> str:
        """Clean up tournament name"""
        cleaned = re.sub(r'\b(at|the|in)\b', '', tournament, flags=re.IGNORECASE)
        cleaned = cleaned.strip()
        return ' '.join(word.capitalize() for word in cleaned.split())
    
    def _is_valid_winner(self, winner: str) -> bool:
        """Check if the winner name seems valid"""
        invalid_terms = ['golf', 'pga', 'tour', 'championship', 'tournament', 'news', 'sports', 'latest']
        return not any(term in winner.lower() for term in invalid_terms) and len(winner.split()) >= 2
    
    def _look_for_specific_tournaments(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Look for specific recent tournaments we know about"""
        # Fallback: Look for any mention of recent known winners
        recent_winners = [
            ("Keegan Bradley", "Travelers Championship"),
            ("Scottie Scheffler", "Memorial Tournament"),
            ("Rory McIlroy", "Wells Fargo Championship"),
            ("Xander Schauffele", "PGA Championship")
        ]
        
        page_text = soup.get_text().lower()
        
        for winner, tournament in recent_winners:
            if winner.lower() in page_text and any(word in page_text for word in tournament.lower().split()):
                return {
                    "winner": winner,
                    "tournament": tournament,
                    "date": datetime.now().strftime("%B %d, %Y"),
                    "score": ""
                }
        
        return {"winner": "Not found", "tournament": "", "date": "", "score": ""}
    
    async def _store_winner_in_db(self, winner_data: Dict[str, str]):
        """Store tournament winner in Supabase"""
        try:
            async with engine.begin() as conn:
                # Create table if it doesn't exist (simplified version without WITB data for now)
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS tournament_winners (
                        id SERIAL PRIMARY KEY,
                        winner VARCHAR(255) NOT NULL,
                        tournament VARCHAR(255) NOT NULL,
                        date VARCHAR(100),
                        score VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Check if we already have a recent entry
                result = await conn.execute(text("""
                    SELECT COUNT(*) FROM tournament_winners 
                    WHERE winner = :winner AND tournament = :tournament
                """), winner_data)
                
                count = result.scalar()
                
                # Prepare data for storage (without witb_data for now)
                storage_data = {
                    "winner": winner_data["winner"],
                    "tournament": winner_data["tournament"],
                    "date": winner_data["date"],
                    "score": winner_data["score"]
                }
                
                if count == 0:
                    # Insert new winner
                    await conn.execute(text("""
                        INSERT INTO tournament_winners (winner, tournament, date, score)
                        VALUES (:winner, :tournament, :date, :score)
                    """), storage_data)
                    print(f"Stored new tournament winner: {winner_data['winner']} - {winner_data['tournament']}")
                else:
                    # Update existing record
                    await conn.execute(text("""
                        UPDATE tournament_winners 
                        SET date = :date, score = :score, updated_at = CURRENT_TIMESTAMP
                        WHERE winner = :winner AND tournament = :tournament
                    """), storage_data)
                    print(f"Updated tournament winner: {winner_data['winner']} - {winner_data['tournament']}")
                
        except Exception as e:
            print(f"Error storing winner in database: {e}")
    
    async def _get_winner_from_db(self) -> Dict[str, str]:
        """Get the most recent tournament winner from database"""
        try:
            async with engine.begin() as conn:
                result = await conn.execute(text("""
                    SELECT winner, tournament, date, score 
                    FROM tournament_winners 
                    ORDER BY updated_at DESC 
                    LIMIT 1
                """))
                
                row = result.fetchone()
                if row:
                    return {
                        "winner": row[0],
                        "tournament": row[1], 
                        "date": row[2] or datetime.now().strftime("%B %d, %Y"),
                        "score": row[3] or ""
                    }
                
        except Exception as e:
            print(f"Error getting winner from database: {e}")
        
        # Final fallback
        return {
            "winner": "Keegan Bradley",
            "tournament": "Travelers Championship",
            "date": "June 22, 2025",
            "score": "-23"
        }

# Global instance
simple_tournament_scraper = SimpleTournamentScraper()