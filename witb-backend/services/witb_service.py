"""WITB service for business logic following CLAUDE.md O-4."""


from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from brand_urls import get_brand_url
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
