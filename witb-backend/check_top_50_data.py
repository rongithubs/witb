"""Check complete top 50 WITB data."""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


async def show_top_50_data():
    engine = create_async_engine("sqlite+aiosqlite:///./dev.db")
    async_session = async_sessionmaker(engine)

    async with async_session() as session:
        # Get comprehensive stats for top 50 players
        result = await session.execute(
            text(
                """
            SELECT p.name, p.ranking, COUNT(w.id) as item_count, 
                   MIN(w.source_url) as source_url
            FROM players p 
            LEFT JOIN witb_items w ON p.id = w.player_id 
            WHERE p.ranking <= 50
            GROUP BY p.id, p.name, p.ranking
            ORDER BY p.ranking
        """
            )
        )

        players = result.fetchall()

        print("🏆 COMPLETE TOP 50 PLAYERS WITB STATUS")
        print("=" * 80)
        print(f"{'Rank':<4} {'Player Name':<25} {'Items':<6} {'Status':<15}")
        print("-" * 80)

        total_items = 0
        scraped_players = 0
        failed_players = []

        for rank, name, count, source_url in players:
            items_str = str(count) if count > 0 else "0"
            status = "✅ Scraped" if source_url else "❌ No Data"

            print(f"{rank:<4} {name:<25} {items_str:<6} {status:<15}")

            if count > 0:
                total_items += count
                scraped_players += 1
            elif source_url is None:
                failed_players.append(name)

        print("-" * 80)
        print("📊 FINAL STATISTICS:")
        print(
            f"   • Players scraped: {scraped_players}/50 ({scraped_players/50*100:.1f}% success rate)"
        )
        print(f"   • Total equipment items: {total_items}")
        print(
            f"   • Average items per player: {total_items/scraped_players:.1f}"
            if scraped_players > 0
            else "   • Average items per player: 0"
        )

        if failed_players:
            print(f"\n❌ FAILED PLAYERS ({len(failed_players)}):")
            for i, player in enumerate(failed_players, 1):
                print(f"   {i}. {player}")

        # Show brand distribution for top 10 drivers
        print("\n🏌️ TOP 10 DRIVER BRANDS:")
        driver_result = await session.execute(
            text(
                """
            SELECT w.brand, COUNT(*) as count
            FROM players p 
            JOIN witb_items w ON p.id = w.player_id 
            WHERE p.ranking <= 50 AND w.category LIKE '%Driver%'
            GROUP BY w.brand
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """
            )
        )

        for brand, count in driver_result.fetchall():
            print(f"   • {brand}: {count} players")


if __name__ == "__main__":
    asyncio.run(show_top_50_data())
