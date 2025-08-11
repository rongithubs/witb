"""Scrape the final 9 missing players with zero items."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from scraper.pga_tracker_scraper import PGATrackerScraper


async def scrape_final_missing():
    """Scrape the final missing players that still have zero items."""
    engine = create_async_engine('sqlite+aiosqlite:///./dev.db')
    async_session = async_sessionmaker(engine)
    
    # The 9 players still missing from our debug
    missing_rankings = [27, 34, 37, 41, 42, 45, 46, 49, 50]
    
    async with async_session() as session:
        # Get the specific missing players
        result = await session.execute(text('''
            SELECT * FROM players 
            WHERE ranking IN (27, 34, 37, 41, 42, 45, 46, 49, 50)
            ORDER BY ranking
        '''))
        
        players = result.fetchall()
        print(f"Found {len(players)} missing players to scrape:")
        for p in players:
            print(f"  #{p.ranking}: {p.name}")
        
        if not players:
            print("No missing players found!")
            return
            
        # Initialize scraper
        scraper = PGATrackerScraper(session, request_delay=2.0)
        
        # Create player objects for scraper
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
        
        print(f"\n🚀 Starting targeted scrape of {len(player_objects)} players...")
        
        # Scrape each player individually with detailed logging
        results = []
        for i, player in enumerate(player_objects, 1):
            print(f"[{i}/{len(player_objects)}] Scraping {player.name} (#{player.ranking})...")
            
            try:
                result = await scraper._scrape_single_player(player)
                results.append(result)
                
                if result.status.value == "success":
                    print(f"  ✅ {result.message}")
                elif result.status.value == "skipped":
                    print(f"  ⏭️ {result.message}")
                else:
                    print(f"  ❌ {result.message}")
                    
                # Add extra delay between players
                if i < len(player_objects):
                    print("  ⏳ Waiting 3 seconds...")
                    await asyncio.sleep(3)
                    
            except Exception as e:
                print(f"  💥 Exception: {str(e)}")
                results.append(None)
        
        # Summary
        successful = sum(1 for r in results if r and r.status.value == "success")
        failed = sum(1 for r in results if r and r.status.value == "error")
        skipped = sum(1 for r in results if r and r.status.value == "skipped")
        exceptions = sum(1 for r in results if r is None)
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ⏭️ Skipped: {skipped}")
        print(f"   ❌ Failed: {failed}")
        print(f"   💥 Exceptions: {exceptions}")


if __name__ == "__main__":
    asyncio.run(scrape_final_missing())