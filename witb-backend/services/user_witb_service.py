"""User WITB service for business logic following CLAUDE.md O-4."""

import logging
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from brand_urls import get_brand_url
from custom_types import UserId, UserWITBItemId
from exceptions import DatabaseOperationError, InvalidPlayerIdError
from repositories.user_witb_repository import UserWITBRepository


class UserWITBService:
    """Service for user WITB item business logic."""

    def __init__(self, db: AsyncSession):
        self.user_witb_repo = UserWITBRepository(db)
        self.db = db

    def _enrich_witb_items_with_urls(
        self, items: list[models.UserWITBItem]
    ) -> list[models.UserWITBItem]:
        """Add brand URLs to user WITB items for equipment links."""
        for item in items:
            if item.brand:
                # Create a product_url attribute for compatibility with existing components
                # Since UserWITBItem doesn't have product_url in the model,
                # we'll add it dynamically for the response
                item.product_url = get_brand_url(item.brand)
        return items

    async def create_user_witb_item(
        self, user_id: UserId, item_data: schemas.UserWITBItemCreate
    ) -> schemas.UserWITBItem:
        """Create a new user WITB item."""
        try:
            new_item = await self.user_witb_repo.create_user_witb_item(
                user_id, item_data.model_dump()
            )
            return schemas.UserWITBItem.model_validate(new_item)
        except IntegrityError as e:
            logging.error(f"Error creating user WITB item: {e}")
            raise DatabaseOperationError("Failed to create user WITB item")

    async def get_user_bag(self, user_id: UserId) -> schemas.UserBagResponse:
        """Get user's complete bag of equipment."""
        try:
            items = await self.user_witb_repo.get_user_bag(user_id)

            # Enrich items with brand URLs
            enriched_items = self._enrich_witb_items_with_urls(items)

            return schemas.UserBagResponse(
                items=[schemas.UserWITBItem.model_validate(item) for item in enriched_items],
                total=len(enriched_items)
            )
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving user bag: {e}")
            raise DatabaseOperationError("Failed to retrieve user bag")

    async def get_user_witb_item_by_id(
        self, item_id: UserWITBItemId, user_id: UserId
    ) -> schemas.UserWITBItem:
        """Get a specific user WITB item by ID."""
        try:
            item = await self.user_witb_repo.get_user_witb_item_by_id(item_id, user_id)
            if not item:
                raise InvalidPlayerIdError(str(item_id))  # Reusing exception for simplicity

            # Enrich with brand URL
            enriched_items = self._enrich_witb_items_with_urls([item])
            return schemas.UserWITBItem.model_validate(enriched_items[0])
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving user WITB item: {e}")
            raise DatabaseOperationError("Failed to retrieve user WITB item")

    async def update_user_witb_item(
        self, item_id: UserWITBItemId, user_id: UserId, update_data: schemas.UserWITBItemUpdate
    ) -> schemas.UserWITBItem:
        """Update a user WITB item."""
        try:
            # Filter out None values to avoid overwriting with None
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}

            updated_item = await self.user_witb_repo.update_user_witb_item(
                item_id, user_id, update_dict
            )
            if not updated_item:
                raise InvalidPlayerIdError(str(item_id))  # Reusing exception for simplicity

            # Enrich with brand URL
            enriched_items = self._enrich_witb_items_with_urls([updated_item])
            return schemas.UserWITBItem.model_validate(enriched_items[0])
        except IntegrityError as e:
            logging.error(f"Error updating user WITB item: {e}")
            raise DatabaseOperationError("Failed to update user WITB item")

    async def delete_user_witb_item(
        self, item_id: UserWITBItemId, user_id: UserId
    ) -> bool:
        """Delete a user WITB item."""
        try:
            print(f"DELETE SERVICE DEBUG - item_id: {item_id}, user_id: {user_id}")
            success = await self.user_witb_repo.delete_user_witb_item(item_id, user_id)
            print(f"DELETE SERVICE DEBUG - Repository returned success: {success}")
            if not success:
                print(f"DELETE SERVICE DEBUG - Item not found, raising InvalidPlayerIdError")
                raise InvalidPlayerIdError(str(item_id))  # Reusing exception for simplicity
            return success
        except InvalidPlayerIdError:
            # Re-raise the specific error instead of wrapping it
            raise
        except SQLAlchemyError as e:
            logging.error(f"Error deleting user WITB item: {e}")
            print(f"DELETE SERVICE DEBUG - SQLAlchemy error: {e}")
            raise DatabaseOperationError("Failed to delete user WITB item")