import asyncio
import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid

from sqlalchemy import delete, select

from database import SessionLocal
from models import Player, SystemUpdate, WITBItem

# Import the Gemini scraper function
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scraper")
)
from scrape_ogwr_gemini import fetch_ogwr_with_gemini


async def populate_ogwr_players():
    """
    Populate the database with top 50 OGWR players using Gemini AI scraper
    """
    print("🏌️ Starting to populate database with top 50 OGWR players...")

    # Get scraped player data using Gemini AI
    players_data = fetch_ogwr_with_gemini()

    if not players_data:
        print("❌ No player data found from Gemini scraper")
        return

    print(f"✅ Successfully scraped {len(players_data)} players with Gemini AI")

    # Get database session
    async with SessionLocal() as session:
        added_count = 0
        updated_count = 0
        skipped_count = 0

        for player_data in players_data:
            try:
                # Check if player already exists (by name)
                result = await session.execute(
                    select(Player).filter(Player.name == player_data["name"])
                )
                existing_player = result.scalar_one_or_none()

                # Parse ranking from rank string
                ranking = None
                try:
                    ranking = (
                        int(player_data.get("rank", 0))
                        if player_data.get("rank")
                        else None
                    )
                except (ValueError, TypeError):
                    ranking = None

                if existing_player:
                    # Update existing player with OGWR data if it's the same tour or we want to update
                    if existing_player.tour != "OGWR":
                        # Keep existing player, create new OGWR entry
                        new_ogwr_player = Player(
                            id=uuid.uuid4(),
                            name=player_data["name"],
                            country=player_data.get("country"),
                            tour="OGWR",
                            age=None,  # OGWR doesn't provide age
                            ranking=ranking,
                            photo_url=None,
                        )

                        session.add(new_ogwr_player)
                        print(
                            f"✅ Added OGWR entry for {player_data['name']} ({player_data.get('country', 'Unknown')})"
                        )
                        added_count += 1
                    else:
                        # Update existing OGWR entry
                        existing_player.ranking = ranking
                        existing_player.country = (
                            player_data.get("country") or existing_player.country
                        )
                        print(
                            f"🔄 Updated OGWR ranking for {player_data['name']} to #{ranking}"
                        )
                        updated_count += 1
                else:
                    # Create new OGWR player
                    new_player = Player(
                        id=uuid.uuid4(),
                        name=player_data["name"],
                        country=player_data.get("country"),
                        tour="OGWR",
                        age=None,  # OGWR doesn't typically provide age
                        ranking=ranking,
                        photo_url=None,
                    )

                    session.add(new_player)
                    print(
                        f"✅ Added {player_data['name']} (#{ranking}, {player_data.get('country', 'Unknown')})"
                    )
                    added_count += 1

            except Exception as e:
                print(f"❌ Error processing {player_data.get('name', 'Unknown')}: {e}")
                continue

        # Remove OGWR players who dropped out of the fresh top 50
        fresh_names = {p["name"] for p in players_data}
        result = await session.execute(
            select(Player).filter(Player.tour == "OGWR")
        )
        all_ogwr = result.scalars().all()

        deleted_count = 0
        for player in all_ogwr:
            if player.name not in fresh_names:
                await session.execute(
                    delete(WITBItem).where(WITBItem.player_id == player.id)
                )
                await session.delete(player)
                print(f"🗑️  Removed stale OGWR player: {player.name}")
                deleted_count += 1

        # Record the OWGR update in system updates table
        owgr_update_details = {
            "added_count": added_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "deleted_count": deleted_count,
            "total_processed": len(players_data),
        }

        # Find existing OWGR update record or create new one
        result = await session.execute(
            select(SystemUpdate).filter(SystemUpdate.update_type == "owgr")
        )
        owgr_record = result.scalar_one_or_none()

        if owgr_record:
            # Update existing record
            owgr_record.last_updated = datetime.now()
            owgr_record.details = json.dumps(owgr_update_details)
        else:
            # Create new record
            new_owgr_record = SystemUpdate(
                update_type="owgr",
                last_updated=datetime.now(),
                details=json.dumps(owgr_update_details),
            )
            session.add(new_owgr_record)

        # Commit all changes
        try:
            await session.commit()
            print("\n🎉 Database update complete!")
            print(f"   ✅ Added: {added_count} new OWGR players")
            print(f"   🔄 Updated: {updated_count} existing OWGR players")
            print(f"   ⏭️  Skipped: {skipped_count} players")
            print(f"   🗑️  Deleted: {deleted_count} stale OGWR players")
            print(f"   📊 Total players processed: {len(players_data)}")
            print("   🕒 OWGR update timestamp recorded")
        except Exception as e:
            await session.rollback()
            print(f"❌ Error committing to database: {e}")
            raise


async def main():
    """Main function to run the OGWR population script"""
    try:
        await populate_ogwr_players()
    except Exception as e:
        print(f"❌ Script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
