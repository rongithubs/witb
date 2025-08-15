from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


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
