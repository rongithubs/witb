import requests
from datetime import datetime
from typing import Dict, List
from sqlalchemy import text
import sys
import os

# Add the backend directory to path for database access
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'witb-backend'))
from database import engine
from brand_urls import get_brand_url

class SimpleTournamentScraper:
    
    # Recent tournament winners (update quarterly)
    RECENT_WINNERS = [
        ("Aldrich Potgieter", "Rocket Classic"),  # Most recent
        ("Keegan Bradley", "Travelers Championship"),
        ("Scottie Scheffler", "Memorial Tournament"),
        ("Xander Schauffele", "PGA Championship"),
        ("Jon Rahm", "The Masters"),
        ("Hideki Matsuyama", "The Sentry"),
    ]
    
    async def scrape_and_store_winner(self) -> Dict[str, str]:
        """Get the most recent tournament winner and their WITB data"""
        try:
            # Try to find current winner from ESPN
            winner_data = self._get_current_winner()
            
            if winner_data and winner_data.get("winner") != "Not found":
                # Get WITB data from our database
                witb_data = await self._get_winner_witb(winner_data["winner"])
                winner_data["witb_items"] = witb_data
                
                # Store in database
                await self._store_winner_in_db(winner_data)
                return winner_data
            
            # Fallback to database
            return await self._get_winner_from_db()
            
        except Exception as e:
            print(f"Error in scrape_and_store_winner: {e}")
            return await self._get_winner_from_db()
    
    def _get_current_winner(self) -> Dict[str, str]:
        """Check ESPN page for current tournament winner"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get("https://www.espn.com/golf/schedule", headers=headers, timeout=10)
            
            if response.status_code == 200:
                page_text = response.text
                
                # Check for recent winners (most recent first)
                for winner, tournament in self.RECENT_WINNERS:
                    if winner in page_text and tournament in page_text:
                        print(f"Found recent winner: {winner} - {tournament}")
                        return {
                            "winner": winner,
                            "tournament": tournament,
                            "date": datetime.now().strftime("%B %d, %Y"),
                            "score": ""
                        }
                
                print("No recent winners found in ESPN page - may need to update RECENT_WINNERS list")
            
            return {"winner": "Not found", "tournament": "", "date": "", "score": ""}
            
        except Exception as e:
            print(f"Error checking ESPN: {e}")
            return {"winner": "Not found", "tournament": "", "date": "", "score": ""}
    
    async def _get_winner_witb(self, winner_name: str) -> List[Dict[str, str]]:
        """Get WITB data for the tournament winner from our database"""
        try:
            async with engine.begin() as conn:
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
                    for row in rows:
                        if row[2]:  # If there's equipment data
                            brand = row[3]
                            witb_item = {
                                "category": row[2],
                                "brand": brand,
                                "model": row[4],
                                "loft": row[5] or "",
                                "shaft": row[6] or "",
                                "product_url": get_brand_url(brand) if brand else None
                            }
                            witb_items.append(witb_item)
                    
                    print(f"Found WITB data for {winner_name}: {len(witb_items)} items")
                    return witb_items
                else:
                    print(f"No WITB data found for {winner_name}")
                    return []
                    
        except Exception as e:
            print(f"Error getting WITB data for {winner_name}: {e}")
            return []
    
    async def _store_winner_in_db(self, winner_data: Dict[str, str]):
        """Store tournament winner in database"""
        try:
            async with engine.begin() as conn:
                # Create table if needed
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
                
                # Check if already exists
                result = await conn.execute(text("""
                    SELECT COUNT(*) FROM tournament_winners 
                    WHERE winner = :winner AND tournament = :tournament
                """), winner_data)
                
                count = result.scalar()
                
                if count == 0:
                    # Insert new winner
                    await conn.execute(text("""
                        INSERT INTO tournament_winners (winner, tournament, date, score)
                        VALUES (:winner, :tournament, :date, :score)
                    """), winner_data)
                    print(f"Stored new tournament winner: {winner_data['winner']} - {winner_data['tournament']}")
                
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
                        "score": row[3] or "",
                        "witb_items": []
                    }
                
        except Exception as e:
            print(f"Error getting winner from database: {e}")
        
        # Final fallback
        return {
            "winner": "Aldrich Potgieter",
            "tournament": "Rocket Classic",
            "date": "July 04, 2025",
            "score": "",
            "witb_items": []
        }

# Global instance
simple_tournament_scraper = SimpleTournamentScraper()