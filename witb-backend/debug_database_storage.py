"""Debug database storage vs scraping disconnect."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text


async def check_database_storage():
    """Check what's actually stored vs what should be scraped."""
    engine = create_async_engine('sqlite+aiosqlite:///./dev.db')
    async_session = async_sessionmaker(engine)
    
    async with async_session() as session:
        # Find Ryan Fox
        result = await session.execute(text("""
            SELECT * FROM players WHERE name LIKE '%Ryan%Fox%'
        """))
        
        player = result.fetchone()
        if player:
            print(f'🏌️ Player found: {player.name}')
            print(f'   ID: {player.id}')
            print(f'   Ranking: {player.ranking}')
            print(f'   Last updated: {player.last_updated}')
            
            # Check his equipment using proper parameterized query
            items_result = await session.execute(text("""
                SELECT category, brand, model, loft, shaft, source_url, last_updated 
                FROM witb_items 
                WHERE player_id = :player_id
            """), {"player_id": player.id})
            
            items = items_result.fetchall()
            print(f'\n📦 Equipment items in database: {len(items)}')
            
            if items:
                for i, item in enumerate(items, 1):
                    print(f'   {i}. {item.category}: {item.brand} {item.model}')
                    if item.loft:
                        print(f'      Loft: {item.loft}')
                    if item.shaft:
                        print(f'      Shaft: {item.shaft}')
                    print(f'      Source: {item.source_url}')
                    print(f'      Updated: {item.last_updated}')
                    print()
            else:
                print('   ❌ No equipment items found in database!')
                print(f'   ⚠️  But scraper found 9 items for this player')
                
        else:
            print('❌ Ryan Fox not found in players table!')
            
        print('\n' + '='*60)
        
        # Check all players with zero items to see the pattern
        zero_items_result = await session.execute(text("""
            SELECT p.name, p.ranking, p.last_updated, COUNT(w.id) as item_count
            FROM players p 
            LEFT JOIN witb_items w ON p.id = w.player_id 
            WHERE p.ranking <= 50
            GROUP BY p.id, p.name, p.ranking, p.last_updated
            HAVING COUNT(w.id) = 0
            ORDER BY p.ranking
        """))
        
        zero_players = zero_items_result.fetchall()
        
        if zero_players:
            print(f'🚨 PLAYERS WITH ZERO ITEMS ({len(zero_players)} total):')
            for player in zero_players:
                print(f'   #{player.ranking}: {player.name} (last_updated: {player.last_updated})')
        else:
            print('✅ All players have at least 1 equipment item!')


if __name__ == "__main__":
    asyncio.run(check_database_storage())