from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class WITBItemBase(BaseModel):
    category: str
    brand: str
    model: str
    loft: Optional[str]
    shaft: Optional[str]
    product_url: Optional[str] = None
    source_url: Optional[str] = None

class WITBItem(WITBItemBase):
    id: UUID
    
    class Config:
        from_attributes = True

class WITBItemCreate(WITBItemBase):
    pass

class PlayerBase(BaseModel):
    name: str
    country: Optional[str]
    tour: Optional[str]
    age: Optional[int]
    ranking: Optional[int]
    photo_url: Optional[str] = None

class Player(BaseModel):
    id: UUID
    name: str
    country: Optional[str]
    tour: Optional[str]
    age: Optional[int]
    ranking: Optional[int]
    photo_url: Optional[str] = None
    last_updated: Optional[datetime] = None
    witb_items: List[WITBItem] = []

    class Config:
        from_attributes = True

class PlayerCreate(PlayerBase):
    pass

class SystemInfo(BaseModel):
    owgr_last_updated: Optional[datetime] = None
    owgr_updated_count: Optional[int] = None
    owgr_total_processed: Optional[int] = None

class PaginatedPlayersResponse(BaseModel):
    items: List[Player]
    total: int
    page: int
    per_page: int
    total_pages: int
    system_info: Optional[SystemInfo] = None
