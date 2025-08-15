"""Database migration script to fix last_updated semantics."""

import asyncio

from sqlalchemy import text

from database import engine


async def migrate_database():
    """Apply database schema changes for proper last_updated semantics."""

    print("🔄 Starting database migration...")

    async with engine.begin() as conn:
        try:
            # 1. Add last_updated column to witb_items if it doesn't exist
            print("📝 Adding last_updated column to witb_items...")
            try:
                await conn.execute(
                    text(
                        """
                    ALTER TABLE witb_items ADD COLUMN last_updated DATETIME
                """
                    )
                )
                print("✅ Added last_updated column to witb_items")
            except Exception as e:
                if (
                    "duplicate column" in str(e).lower()
                    or "already exists" in str(e).lower()
                ):
                    print("ℹ️  last_updated column already exists in witb_items")
                else:
                    raise e

            # 2. Create system_updates table
            print("📝 Creating system_updates table...")
            try:
                await conn.execute(
                    text(
                        """
                    CREATE TABLE system_updates (
                        id UUID PRIMARY KEY,
                        update_type VARCHAR NOT NULL,
                        last_updated DATETIME NOT NULL,
                        details VARCHAR
                    )
                """
                    )
                )
                print("✅ Created system_updates table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("ℹ️  system_updates table already exists")
                else:
                    raise e

            # 3. Update existing witb_items to have last_updated timestamps
            print(
                "📝 Setting initial last_updated timestamps for existing WITB items..."
            )
            result = await conn.execute(
                text(
                    """
                UPDATE witb_items 
                SET last_updated = CURRENT_TIMESTAMP
                WHERE last_updated IS NULL
            """
                )
            )
            updated_rows = result.rowcount
            print(f"✅ Updated {updated_rows} WITB items with initial timestamps")

            # 4. Show current player last_updated values that will now represent WITB updates
            print(
                "📊 Current player last_updated values (these will now represent WITB data updates):"
            )
            result = await conn.execute(
                text(
                    """
                SELECT name, ranking, last_updated 
                FROM players 
                WHERE ranking <= 50
                ORDER BY ranking
                LIMIT 10
            """
                )
            )

            players = result.fetchall()
            for player in players:
                print(f"   #{player.ranking}: {player.name} - {player.last_updated}")

            print(f"   ... and {len(players)} more players")

            print("\n🎉 Database migration completed successfully!")
            print("\n📋 Changes applied:")
            print("   • Removed onupdate=func.now() from players.last_updated")
            print("   • Added last_updated column to witb_items table")
            print("   • Created system_updates table for tracking OWGR updates")
            print(
                "   • Players.last_updated now only changes when WITB data is scraped"
            )
            print(
                "   • OWGR updates will be tracked separately in system_updates table"
            )

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(migrate_database())
