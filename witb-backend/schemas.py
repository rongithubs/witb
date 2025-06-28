from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class WITBItemBase(BaseModel):
    category: str
    brand: str
    model: str
    loft: Optional[str]
    shaft: Optional[str]

class WITBItem(WITBItemBase):
    id: UUID
    
    class Config:
        orm_mode = True

class PlayerBase(BaseModel):
    name: str
    country: Optional[str]
    tour: Optional[str]
    age: Optional[int]
    photo_url: Optional[str] = None

class Player(BaseModel):
    id: UUID
    name: str
    country: Optional[str]
    tour: Optional[str]
    age: Optional[int]
    photo_url: Optional[str] = None
    witb_items: List[WITBItem] = []

    class Config:
        orm_mode = True

class PlayerCreate(PlayerBase):
    pass
