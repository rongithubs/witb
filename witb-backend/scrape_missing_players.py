"""Scrape specific missing players that should exist on PGA Club Tracker."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

from scraper.pga_tracker_scraper import PGATrackerScraper


async def scrape_missing_players():
    """Scrape the 5 players that were missing but should exist."""
    engine = create_async_engine('sqlite+aiosqlite:///./dev.db')
    async_session = async_sessionmaker(engine)
    
    missing_rankings = [34, 37, 38, 41, 42]
    
    async with async_session() as session:
        # Get the specific missing players
        result = await session.execute(text('''
            SELECT * FROM players 
            WHERE ranking IN (34, 37, 38, 41, 42)
            ORDER BY ranking
        '''))
        
        players = result.fetchall()
        
        if not players:
            print("No players found with those rankings!")
            return
            
        print(f"Found {len(players)} missing players to scrape:")
        for p in players:
            print(f"  #{p.ranking}: {p.name}")
        
        # Initialize scraper
        scraper = PGATrackerScraper(session, request_delay=2.0)
        
        # Create player objects (simple mock structure)
        from dataclasses import dataclass
        
        @dataclass
        class Player:
            id: str
            name: str
            ranking: int
        
        player_objects = [
            Player(id=p.id, name=p.name, ranking=p.ranking) 
            for p in players
        ]
        
        print(f"\nStarting targeted scrape of {len(player_objects)} players...")
        
        # Scrape each player individually
        results = []
        for i, player in enumerate(player_objects, 1):
            print(f"[{i}/{len(player_objects)}] Scraping {player.name} (#{player.ranking})...")
            
            result = await scraper._scrape_single_player(player)
            results.append(result)
            
            if result.status.value == "success":
                print(f"  ✅ {result.message}")
            elif result.status.value == "skipped":
                print(f"  ⏭️ {result.message}")
            else:
                print(f"  ❌ {result.message}")
        
        # Summary
        successful = sum(1 for r in results if r.status.value == "success")
        failed = sum(1 for r in results if r.status.value == "error")
        skipped = sum(1 for r in results if r.status.value == "skipped")
        
        print(f"\n📊 Results: {successful} successful, {skipped} skipped, {failed} failed")


if __name__ == "__main__":
    asyncio.run(scrape_missing_players())