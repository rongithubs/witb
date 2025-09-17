"""User WITB repository for database operations following CLAUDE.md D-4."""

import re
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
from custom_types import UserId, UserWITBItemId


class UserWITBRepository:
    """Repository for user WITB item database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user_witb_item(self, user_id: UserId, item_data: dict) -> models.UserWITBItem:
        """Create a new user WITB item."""
        new_item = models.UserWITBItem(user_id=user_id, **item_data)
        self.db.add(new_item)
        try:
            await self.db.commit()
            await self.db.refresh(new_item)
            return new_item
        except IntegrityError:
            await self.db.rollback()
            raise

    async def get_user_bag(self, user_id: UserId) -> list[models.UserWITBItem]:
        """Get all WITB items for a user, sorted by golf club order."""
        result = await self.db.execute(
            select(models.UserWITBItem).where(models.UserWITBItem.user_id == user_id)
        )
        items = result.scalars().all()

        # Sort items using golf club ordering logic
        if items:
            items = self._sort_user_witb_items(list(items))

        return items

    async def get_user_witb_item_by_id(
        self, item_id: UserWITBItemId, user_id: UserId
    ) -> models.UserWITBItem | None:
        """Get a specific user WITB item by ID, ensuring it belongs to the user."""
        result = await self.db.execute(
            select(models.UserWITBItem).where(
                models.UserWITBItem.id == item_id,
                models.UserWITBItem.user_id == user_id
            )
        )
        return result.scalars().first()

    async def update_user_witb_item(
        self, item_id: UserWITBItemId, user_id: UserId, update_data: dict
    ) -> models.UserWITBItem | None:
        """Update a user WITB item."""
        item = await self.get_user_witb_item_by_id(item_id, user_id)
        if not item:
            return None

        for key, value in update_data.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)

        try:
            await self.db.commit()
            await self.db.refresh(item)
            return item
        except IntegrityError:
            await self.db.rollback()
            raise

    async def delete_user_witb_item(
        self, item_id: UserWITBItemId, user_id: UserId
    ) -> bool:
        """Delete a user WITB item."""
        print(f"DELETE REPO DEBUG - Looking for item_id: {item_id}, user_id: {user_id}")
        item = await self.get_user_witb_item_by_id(item_id, user_id)
        print(f"DELETE REPO DEBUG - Found item: {item}")
        if not item:
            print(f"DELETE REPO DEBUG - Item not found, returning False")
            return False

        print(f"DELETE REPO DEBUG - Deleting item: {item.id}")
        await self.db.delete(item)
        try:
            await self.db.commit()
            print(f"DELETE REPO DEBUG - Successfully deleted and committed")
            return True
        except IntegrityError as e:
            print(f"DELETE REPO DEBUG - IntegrityError during commit: {e}")
            await self.db.rollback()
            raise

    def _sort_user_witb_items(
        self, witb_items: list[models.UserWITBItem]
    ) -> list[models.UserWITBItem]:
        """Sort user WITB items from longest to shortest clubs following proper golf bag organization."""

        # Define club order from longest to shortest (case-insensitive)
        club_order = {
            "driver": 1,
            "mini driver": 2,
            "3-wood": 3,
            "3+-wood": 3,  # Handle 3+ wood variation
            "5-wood": 4,
            "7-wood": 5,
            "9-wood": 6,
            "hybrid": 7,
            "iron": 8,
            "wedge": 9,
            "putter": 10,
            "ball": 11,
            "grip": 12,
        }

        def sort_key(item):
            # Primary sort by club category (case-insensitive)
            category_lower = item.category.lower()
            primary = club_order.get(category_lower, 99)

            # Secondary sort within same category
            if category_lower == "iron":
                # For irons, try to extract iron number from model/loft
                model_text = f"{item.model} {item.loft or ''}".upper()
                if "PW" in model_text or "PITCHING" in model_text:
                    return (primary, 10)  # PW after 9 iron
                # Try to find iron number
                match = re.search(r"\b([4-9])\b", model_text)
                if match:
                    return (primary, int(match.group(1)))
                # Handle ranges like "5-PW"
                range_match = re.search(r"(\d+)-", model_text)
                if range_match:
                    return (primary, int(range_match.group(1)))
                return (primary, 99)

            elif category_lower == "wedge":
                # For wedges, sort by loft degree
                if item.loft:
                    match = re.search(r"(\d+)", item.loft)
                    if match:
                        return (primary, int(match.group(1)))
                return (primary, 99)

            return (primary, 0)

        return sorted(witb_items, key=sort_key)