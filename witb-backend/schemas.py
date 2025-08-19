from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WITBItemBase(BaseModel):
    category: str
    brand: str
    model: str
    loft: str | None
    shaft: str | None
    product_url: str | None = None
    source_url: str | None = None


class WITBItem(WITBItemBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class WITBItemCreate(WITBItemBase):
    pass


class PlayerBase(BaseModel):
    name: str
    country: str | None
    tour: str | None
    age: int | None
    ranking: int | None
    photo_url: str | None = None


class Player(BaseModel):
    id: UUID
    name: str
    country: str | None
    tour: str | None
    age: int | None
    ranking: int | None
    photo_url: str | None = None
    last_updated: datetime | None = None
    witb_items: list[WITBItem] = []

    model_config = ConfigDict(from_attributes=True)


class PlayerCreate(PlayerBase):
    pass


class SystemInfo(BaseModel):
    owgr_last_updated: datetime | None = None
    owgr_updated_count: int | None = None
    owgr_total_processed: int | None = None


class PaginatedPlayersResponse(BaseModel):
    items: list[Player]
    total: int
    page: int
    per_page: int
    total_pages: int
    system_info: SystemInfo | None = None


class ClubUsageItem(BaseModel):
    brand: str
    model: str
    count: int
    percentage: float
    rank: int
    brand_url: str | None = None


class LeaderboardResponse(BaseModel):
    categories: dict[str, list[ClubUsageItem]]
    total_categories: int
    total_unique_combinations: int


class UserBase(BaseModel):
    email: str | None = None
    phone: str | None = None


class User(UserBase):
    id: UUID
    supabase_user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    supabase_user_id: UUID


class AuthUser(BaseModel):
    """Schema for authenticated user with JWT token info."""

    user_id: UUID
    supabase_user_id: UUID
    email: str | None = None
    phone: str | None = None
    exp: int  # Token expiration timestamp
    iat: int  # Token issued at timestamp
