"""WITB service for business logic following CLAUDE.md O-4."""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from brand_urls import BRAND_URLS, get_brand_url
from repositories.witb_repository import WITBRepository


class WitbService:
    """Service for WITB business logic."""

    def __init__(self, db: AsyncSession):
        self.witb_repo = WITBRepository(db)

    async def get_club_usage_leaderboard(
        self, category_filter: str | None = None, limit: int | None = 10
    ) -> schemas.LeaderboardResponse:
        """Get club usage leaderboard with enriched data."""
        raw_data = await self.witb_repo.get_club_usage_leaderboard(
            category_filter=category_filter, limit=limit
        )

        # Convert raw data to schema objects and enrich with URLs
        categories = {}
        for category, items in raw_data.items():
            category_items = []
            for item in items:
                club_item = schemas.ClubUsageItem(
                    brand=item["brand"],
                    model=item["model"],
                    count=item["count"],
                    percentage=item["percentage"],
                    rank=item["rank"],
                    brand_url=get_brand_url(item["brand"]),
                )
                category_items.append(club_item)
            categories[category] = category_items

        # Calculate total statistics
        total_categories = len(categories)
        total_unique_combinations = sum(len(items) for items in categories.values())

        return schemas.LeaderboardResponse(
            categories=categories,
            total_categories=total_categories,
            total_unique_combinations=total_unique_combinations,
        )

    async def get_recent_changes(
        self, since: datetime | None = None, limit: int = 50
    ) -> schemas.BagChangesResponse:
        """Get the recent bag-change feed (newest first) with player info."""
        changes = await self.witb_repo.get_recent_changes(since=since, limit=limit)
        items = [self._to_change_item(change) for change in changes]
        return schemas.BagChangesResponse(changes=items, total=len(items))

    @staticmethod
    def _to_change_item(change: models.WITBChange) -> schemas.BagChangeItem:
        """Map a WITBChange row plus its player onto the feed schema."""
        player = change.player
        return schemas.BagChangeItem(
            id=change.id,
            player_id=change.player_id,
            player_name=player.name if player else None,
            player_photo_url=player.photo_url if player else None,
            category=change.category,
            change_type=change.change_type,
            old_brand=change.old_brand,
            old_model=change.old_model,
            old_loft=change.old_loft,
            old_shaft=change.old_shaft,
            new_brand=change.new_brand,
            new_model=change.new_model,
            new_loft=change.new_loft,
            new_shaft=change.new_shaft,
            detected_at=change.detected_at,
        )

    async def get_brands(self) -> schemas.BrandResponse:
        """Get all unique brands from database and static list."""
        db_brands = await self.witb_repo.get_distinct_brands()
        static_brands = list(BRAND_URLS.keys())

        # Combine and deduplicate brands (case-insensitive)
        all_brands_lower = {}
        for brand in db_brands + static_brands:
            brand_lower = brand.lower()
            if brand_lower not in all_brands_lower:
                all_brands_lower[brand_lower] = brand

        # Get unique brands sorted alphabetically
        unique_brands = sorted(all_brands_lower.values())

        return schemas.BrandResponse(brands=unique_brands, total=len(unique_brands))
