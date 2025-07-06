"""WITB repository for database operations following CLAUDE.md D-4."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
from custom_types import PlayerId, WITBItemId


class WITBRepository:
    """Repository for WITB item database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_witb_item(
        self, 
        player_id: PlayerId, 
        item_data: dict
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