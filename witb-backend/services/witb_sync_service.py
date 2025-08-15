"""WITB data synchronization service following CLAUDE.md C-4."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

import models
from custom_types import PlayerId
from repositories.player_repository import PlayerRepository
from repositories.witb_repository import WITBRepository
from services.scraper_service import EquipmentItem, WITBData


class SyncAction(Enum):
    """Sync action results."""

    UPDATED = "updated"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class SyncResult:
    """Result of sync operation."""

    action: SyncAction
    items_count: int
    message: str


class WITBSyncService:
    """Service for synchronizing scraped WITB data with database."""

    def __init__(self, db: AsyncSession):
        """Initialize sync service with database session."""
        self.db = db
        self.player_repo = PlayerRepository(db)
        self.witb_repo = WITBRepository(db)

    async def sync_player_equipment(
        self, player_id: PlayerId, scraped_data: WITBData
    ) -> SyncResult:
        """
        Sync scraped WITB data with existing player data.

        Args:
            player_id: Player to update
            scraped_data: Scraped equipment data

        Returns:
            SyncResult indicating what action was taken
        """
        try:
            # Get existing player data
            existing_player = await self.player_repo.get_player_by_id(player_id)
            if not existing_player:
                return SyncResult(
                    action=SyncAction.ERROR,
                    items_count=0,
                    message=f"Player not found: {player_id}",
                )

            # Check if we should update based on dates
            should_update = self._should_update_data(
                existing_player.last_updated, scraped_data.last_updated
            )

            if not should_update:
                return SyncResult(
                    action=SyncAction.SKIPPED,
                    items_count=len(scraped_data.equipment),
                    message=f"Existing data is newer or equal. "
                    f"Existing: {existing_player.last_updated}, "
                    f"Scraped: {scraped_data.last_updated}",
                )

            # Convert scraped equipment to database models
            new_witb_items = self._convert_to_witb_items(
                scraped_data.equipment, player_id, scraped_data.source_url
            )

            # Update player's last_updated timestamp
            await self.player_repo.update_player(
                player_id, {"last_updated": scraped_data.last_updated or datetime.now()}
            )

            # Replace all equipment for this player
            await self.witb_repo.replace_player_equipment(player_id, new_witb_items)

            return SyncResult(
                action=SyncAction.UPDATED,
                items_count=len(new_witb_items),
                message=f"Updated {len(new_witb_items)} equipment items "
                f"for player {existing_player.name}",
            )

        except Exception as e:
            return SyncResult(
                action=SyncAction.ERROR, items_count=0, message=f"Sync failed: {str(e)}"
            )

    def _should_update_data(
        self, existing_date: datetime | None, scraped_date: datetime | None
    ) -> bool:
        """
        Determine if data should be updated based on timestamps.

        Args:
            existing_date: Last updated date from database
            scraped_date: Last updated date from scraped data

        Returns:
            True if data should be updated, False otherwise
        """
        # Always update if no existing data
        if existing_date is None:
            return True

        # Don't update if no scraped date available
        if scraped_date is None:
            return False

        # Update only if scraped data is newer
        return scraped_date > existing_date

    def _convert_to_witb_items(
        self, equipment: list[EquipmentItem], player_id: PlayerId, source_url: str
    ) -> list[models.WITBItem]:
        """
        Convert scraped equipment to WITBItem database models.

        Args:
            equipment: List of scraped equipment items
            player_id: Player ID to associate with items
            source_url: URL where data was scraped from

        Returns:
            List of WITBItem models ready for database insertion
        """
        witb_items = []

        for item in equipment:
            witb_item = models.WITBItem(
                player_id=player_id,
                category=item.category,
                brand=item.brand,
                model=item.model,
                loft=item.loft,
                shaft=item.shaft,
                source_url=source_url,
                product_url=None,  # Will be enriched later by service layer
            )
            witb_items.append(witb_item)

        return witb_items
