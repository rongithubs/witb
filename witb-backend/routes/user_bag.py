"""User bag routes following CLAUDE.md O-4 (thin route handlers)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from auth.dependencies import get_current_user_from_db
from custom_types import UserId, UserWITBItemId
from dependencies import get_db
from services.user_witb_service import UserWITBService

router = APIRouter(prefix="/user-bag", tags=["user-bag"])


@router.get("", response_model=schemas.UserBagResponse)
async def get_user_bag(
    current_user: schemas.User = Depends(get_current_user_from_db),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's complete bag of equipment."""
    service = UserWITBService(db)
    return await service.get_user_bag(UserId(current_user.id))


@router.post("", response_model=schemas.UserWITBItem, status_code=status.HTTP_201_CREATED)
async def add_equipment_to_bag(
    item_data: schemas.UserWITBItemCreate,
    current_user: schemas.User = Depends(get_current_user_from_db),
    db: AsyncSession = Depends(get_db),
):
    """Add new equipment to user's bag."""
    service = UserWITBService(db)
    return await service.create_user_witb_item(UserId(current_user.id), item_data)


@router.get("/{item_id}", response_model=schemas.UserWITBItem)
async def get_user_bag_item(
    item_id: str,
    current_user: schemas.User = Depends(get_current_user_from_db),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific item from user's bag."""
    try:
        item_uuid = UserWITBItemId(item_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID format"
        )

    service = UserWITBService(db)
    return await service.get_user_witb_item_by_id(item_uuid, UserId(current_user.id))


@router.put("/{item_id}", response_model=schemas.UserWITBItem)
async def update_user_bag_item(
    item_id: str,
    update_data: schemas.UserWITBItemUpdate,
    current_user: schemas.User = Depends(get_current_user_from_db),
    db: AsyncSession = Depends(get_db),
):
    """Update an item in user's bag."""
    try:
        item_uuid = UserWITBItemId(item_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID format"
        )

    service = UserWITBService(db)
    return await service.update_user_witb_item(item_uuid, UserId(current_user.id), update_data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_equipment_from_bag(
    item_id: str,
    current_user: schemas.User = Depends(get_current_user_from_db),
    db: AsyncSession = Depends(get_db),
):
    """Remove equipment from user's bag."""
    try:
        item_uuid = UserWITBItemId(item_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID format"
        )

    service = UserWITBService(db)
    await service.delete_user_witb_item(item_uuid, UserId(current_user.id))