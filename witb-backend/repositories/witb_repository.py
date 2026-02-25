"""WITB repository for database operations following CLAUDE.md D-4."""

from typing import Any

from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
from custom_types import PlayerId, WITBItemId


class WITBRepository:
    """Repository for WITB item database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_witb_item(
        self, player_id: PlayerId, item_data: dict
    ) -> models.WITBItem:
        """Create a new WITB item for a player."""
        db_item = models.WITBItem(**item_data, player_id=player_id)
        self.db.add(db_item)
        await self.db.commit()
        await self.db.refresh(db_item)
        return db_item

    async def get_witb_item_by_id(self, item_id: WITBItemId) -> models.WITBItem:
        """Get WITB item by ID."""
        result = await self.db.execute(
            select(models.WITBItem).where(models.WITBItem.id == item_id)
        )
        return result.scalars().first()

    async def replace_player_equipment(
        self, player_id: PlayerId, new_items: list[models.WITBItem]
    ) -> None:
        """Replace all WITB items for a player with new items."""
        # Delete existing items for this player
        await self.db.execute(
            delete(models.WITBItem).where(models.WITBItem.player_id == player_id)
        )

        # Add new items
        for item in new_items:
            self.db.add(item)

        await self.db.commit()

    async def get_club_usage_leaderboard(
        self, category_filter: str | None = None, limit: int | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        """Get club usage statistics grouped by category."""
        # Build base query for club usage counts
        base_query = select(
            models.WITBItem.category,
            models.WITBItem.brand,
            models.WITBItem.model,
            func.count().label("count"),
        ).group_by(
            models.WITBItem.category, models.WITBItem.brand, models.WITBItem.model
        )

        # Apply category filter if provided
        if category_filter:
            base_query = base_query.where(
                models.WITBItem.category.ilike(f"%{category_filter}%")
            )

        # Get usage counts
        result = await self.db.execute(base_query)
        usage_data = result.fetchall()

        # Get total counts per category for percentage calculation
        category_totals_query = select(
            models.WITBItem.category, func.count().label("total_count")
        ).group_by(models.WITBItem.category)

        if category_filter:
            category_totals_query = category_totals_query.where(
                models.WITBItem.category.ilike(f"%{category_filter}%")
            )

        category_totals_result = await self.db.execute(category_totals_query)
        category_totals = {
            row.category: row.total_count for row in category_totals_result
        }

        # Organize data by category
        leaderboard_data: dict[str, list[dict[str, Any]]] = {}

        for row in usage_data:
            category = row.category
            if category not in leaderboard_data:
                leaderboard_data[category] = []

            total_in_category = category_totals.get(category, 0)
            percentage = (
                (row.count / total_in_category * 100) if total_in_category > 0 else 0
            )

            leaderboard_data[category].append(
                {
                    "brand": row.brand,
                    "model": row.model,
                    "count": row.count,
                    "percentage": round(percentage, 1),
                }
            )

        # Sort each category by count descending and add rank
        for category in leaderboard_data:
            leaderboard_data[category].sort(key=lambda x: x["count"], reverse=True)
            for i, item in enumerate(leaderboard_data[category]):
                item["rank"] = i + 1

            # Apply limit if specified
            if limit:
                leaderboard_data[category] = leaderboard_data[category][:limit]

        return leaderboard_data

    async def get_distinct_brands(self) -> list[str]:
        """Get all unique brands from WITB items."""
        query = (
            select(models.WITBItem.brand)
            .distinct()
            .where(models.WITBItem.brand.isnot(None))
            .order_by(models.WITBItem.brand)
        )
        result = await self.db.execute(query)
        brands = [row[0] for row in result.fetchall() if row[0]]
        return brands
