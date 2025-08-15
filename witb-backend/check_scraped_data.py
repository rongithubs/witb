"""Check what WITB data has been scraped so far."""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


async def show_scraped_data():
    engine = create_async_engine("sqlite+aiosqlite:///./dev.db")
    async_session = async_sessionmaker(engine)

    async with async_session() as session:
        # Get players with WITB items
        result = await session.execute(
            text(
                """
            SELECT p.name, p.ranking, COUNT(w.id) as item_count, 
                   MIN(w.source_url) as source_url
            FROM players p 
            LEFT JOIN witb_items w ON p.id = w.player_id 
            WHERE p.ranking <= 25
            GROUP BY p.id, p.name, p.ranking
            ORDER BY p.ranking
        """
            )
        )

        players = result.fetchall()

        print("Top 25 Players WITB Status:")
        print("=" * 70)
        print(f'{"Rank":<4} {"Player Name":<25} {"Items":<6} {"Source":<15}')
        print("-" * 70)

        total_items = 0
        scraped_players = 0

        for rank, name, count, source_url in players:
            items_str = str(count) if count > 0 else "None"
            source_str = "PGA Club Tracker" if source_url else "None"

            print(f"{rank:<4} {name:<25} {items_str:<6} {source_str:<15}")

            if count > 0:
                total_items += count
                scraped_players += 1

        print("-" * 70)
        print(
            f"Summary: {scraped_players}/25 players scraped, {total_items} total items"
        )

        # Show detailed equipment for top 3 scraped players
        if scraped_players > 0:
            print("\nDetailed Equipment (Top 3 Scraped Players):")
            print("=" * 80)

            detailed_result = await session.execute(
                text(
                    """
                SELECT p.name, w.category, w.brand, w.model, w.loft, w.shaft
                FROM players p 
                JOIN witb_items w ON p.id = w.player_id 
                WHERE p.ranking <= 25 AND w.id IS NOT NULL
                ORDER BY p.ranking, w.category
                LIMIT 30
            """
                )
            )

            current_player = None
            for name, category, brand, model, loft, shaft in detailed_result.fetchall():
                if name != current_player:
                    if current_player is not None:
                        print()
                    print(f"{name}:")
                    current_player = name

                loft_str = f" ({loft})" if loft else ""
                shaft_str = f" - {shaft}" if shaft else ""
                print(f"  {category}: {brand} {model}{loft_str}{shaft_str}")


if __name__ == "__main__":
    asyncio.run(show_scraped_data())
