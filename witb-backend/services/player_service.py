"""Player service for business logic following CLAUDE.md O-4."""

import json
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from brand_urls import get_brand_url
from custom_types import PlayerId
from exceptions import (
    DatabaseOperationError,
    InvalidPlayerIdError,
    PlayerAlreadyExistsError,
    PlayerNotFoundError,
)
from repositories.player_repository import PlayerRepository
from repositories.witb_repository import WITBRepository


class PlayerService:
    """Service for player business logic."""

    def __init__(self, db: AsyncSession):
        self.player_repo = PlayerRepository(db)
        self.witb_repo = WITBRepository(db)
        self.db = db

    def _enrich_witb_items_with_urls(
        self, items: list[schemas.WITBItem]
    ) -> list[schemas.WITBItem]:
        """Add brand URLs to WITB items that don't have specific product URLs."""
        for item in items:
            if not item.product_url and item.brand:
                item.product_url = get_brand_url(item.brand)
        return items

    async def create_player(self, player_data: schemas.PlayerCreate) -> schemas.Player:
        """Create a new player."""
        try:
            new_player = await self.player_repo.create_player(player_data.model_dump())
            return schemas.Player.model_validate(new_player)
        except IntegrityError:
            raise PlayerAlreadyExistsError(player_data.name)

    async def get_player_by_id(self, player_id: str) -> schemas.Player:
        """Get player by ID with enriched WITB items."""
        try:
            player_uuid = UUID(player_id)
        except ValueError:
            raise InvalidPlayerIdError(player_id)

        player = await self.player_repo.get_player_by_id(PlayerId(player_uuid))
        if not player:
            raise PlayerNotFoundError(player_id)

        player_schema = schemas.Player.model_validate(player)
        self._enrich_witb_items_with_urls(player_schema.witb_items)
        return player_schema

    async def get_players_paginated(
        self, page: int, per_page: int, tour: str | None = None
    ) -> schemas.PaginatedPlayersResponse:
        """Get paginated players with optional tour filter and enriched WITB items."""
        offset = (page - 1) * per_page

        players, total = await self.player_repo.get_players_paginated(
            offset, per_page, tour
        )

        # Get OWGR system info
        system_info = await self._get_system_info()

        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page

        player_schemas = [schemas.Player.model_validate(p) for p in players]
        for player_schema in player_schemas:
            self._enrich_witb_items_with_urls(player_schema.witb_items)

        return schemas.PaginatedPlayersResponse(
            items=player_schemas,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            system_info=system_info,
        )

    async def _get_system_info(self) -> schemas.SystemInfo | None:
        """Get OWGR system update information."""
        logger = logging.getLogger(__name__)

        try:
            result = await self.db.execute(
                select(models.SystemUpdate).filter(
                    models.SystemUpdate.update_type == "owgr"
                )
            )
            owgr_update = result.scalar_one_or_none()

            if not owgr_update:
                return None

            details = {}
            if owgr_update.details:
                try:
                    details = json.loads(owgr_update.details)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse SystemUpdate details JSON: {e}")
                    # Continue with empty details rather than failing completely

            return schemas.SystemInfo(
                owgr_last_updated=owgr_update.last_updated,
                owgr_updated_count=details.get("updated_count", 0),
                owgr_total_processed=details.get("total_processed", 0),
            )
        except SQLAlchemyError as e:
            # Database connection or query errors - log but don't break main API
            logger.error(f"Database error fetching system info: {e}")
            return None
        except Exception as e:
            # Unexpected errors - log for debugging but don't break main API
            logger.error(f"Unexpected error fetching system info: {e}")
            return None

    async def search_player_exists(self, name: str) -> bool:
        """Check if player exists by name."""
        player = await self.player_repo.search_player_by_name(name)
        return bool(player)

    async def add_witb_item(
        self, player_id: str, item_data: schemas.WITBItemCreate
    ) -> schemas.WITBItem:
        """Add WITB item to player."""
        try:
            player_uuid = UUID(player_id)
        except ValueError:
            raise InvalidPlayerIdError(player_id)

        # Verify player exists
        player = await self.player_repo.get_player_by_id(PlayerId(player_uuid))
        if not player:
            raise PlayerNotFoundError(player_id)

        try:
            db_item = await self.witb_repo.create_witb_item(
                PlayerId(player_uuid), item_data.model_dump()
            )
            return schemas.WITBItem.model_validate(db_item)
        except Exception as e:
            await self.db.rollback()
            raise DatabaseOperationError("create_witb_item", str(e))
