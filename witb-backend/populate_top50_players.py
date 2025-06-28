import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from database import engine, SessionLocal
from models import Player
from sqlalchemy import select
import uuid

# Import the scraper function
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scraper'))
from scrape_pgatop50 import fetch_top50_espn

async def populate_top50_players():
    """
    Populate the database with top 50 PGA Tour players from ESPN scraper
    """
    print("🏌️ Starting to populate database with top 50 PGA Tour players...")
    
    # Get scraped player data
    players_data = fetch_top50_espn()
    
    if not players_data:
        print("❌ No player data found from scraper")
        return
    
    print(f"✅ Successfully scraped {len(players_data)} players")
    
    # Get database session
    async with SessionLocal() as session:
        added_count = 0
        skipped_count = 0
        
        for player_data in players_data:
            try:
                # Check if player already exists (by name)
                result = await session.execute(
                    select(Player).filter(Player.name == player_data['name'])
                )
                if result.scalar_one_or_none():
                    print(f"⏭️  Skipping {player_data['name']} - already exists")
                    skipped_count += 1
                    continue
                
                # Create new player (excluding age and earnings/events for now)
                new_player = Player(
                    id=uuid.uuid4(),
                    name=player_data['name'],
                    country=player_data.get('country'),
                    tour=player_data.get('tour'),
                    photo_url=None  # We don't have photo URLs from the scraper yet
                )
                
                session.add(new_player)
                print(f"✅ Added {player_data['name']} ({player_data.get('country', 'Unknown')})")
                added_count += 1
                
            except Exception as e:
                print(f"❌ Error adding {player_data.get('name', 'Unknown')}: {e}")
                continue
        
        # Commit all changes
        try:
            await session.commit()
            print(f"\n🎉 Database update complete!")
            print(f"   ✅ Added: {added_count} players")
            print(f"   ⏭️  Skipped: {skipped_count} players (already existed)")
            print(f"   📊 Total players in scrape: {len(players_data)}")
        except Exception as e:
            await session.rollback()
            print(f"❌ Error committing to database: {e}")
            raise

async def main():
    """Main function to run the population script"""
    try:
        await populate_top50_players()
    except Exception as e:
        print(f"❌ Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())