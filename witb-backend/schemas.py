from datetime import date, datetime
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


class BrandResponse(BaseModel):
    """Schema for brands list response."""

    brands: list[str]
    total: int


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


class FavoritePlayerRequest(BaseModel):
    """Schema for adding player to favorites."""

    player_id: UUID


class FavoritePlayerResponse(BaseModel):
    """Schema for favorite player with player details."""

    id: UUID
    player: Player
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserFavoritesResponse(BaseModel):
    """Schema for user's favorite players list."""

    favorites: list[FavoritePlayerResponse]
    total: int


# eBay API Integration Schemas


class EBaySearchRequest(BaseModel):
    """Schema for eBay product search requests."""

    brand: str | None = None
    model: str | None = None
    category: str | None = None
    condition: str | None = "New"
    max_price: float | None = None
    min_price: float | None = None
    limit: int = 20


class EBayPriceInfo(BaseModel):
    """Schema for eBay product pricing information."""

    current_price: float
    currency: str = "USD"
    condition: str
    shipping_cost: float | None = None
    buy_it_now_price: float | None = None
    auction_end_time: datetime | None = None


class EBayProduct(BaseModel):
    """Schema for eBay product listing."""

    product_id: str
    title: str
    brand: str | None = None
    model: str | None = None
    category: str | None = None
    price_info: EBayPriceInfo
    listing_url: str
    image_url: str | None = None
    seller_info: dict | None = None
    location: str | None = None
    listing_type: str  # "Auction", "FixedPrice", etc.


class EBaySearchResponse(BaseModel):
    """Schema for eBay search results."""

    products: list[EBayProduct]
    total_found: int
    page: int
    per_page: int
    search_query: str


class EBayEnrichmentRequest(BaseModel):
    """Schema for enriching WITB items with eBay data."""

    witb_item_ids: list[UUID]
    search_options: EBaySearchRequest | None = None


class EnrichedWITBItem(WITBItem):
    """Schema for WITB item enriched with eBay pricing data."""

    ebay_product_id: str | None = None
    current_price: float | None = None
    price_currency: str | None = None
    price_condition: str | None = None
    price_last_updated: datetime | None = None
    ebay_listing_url: str | None = None


# User WITB Item Schemas


class UserWITBItemBase(BaseModel):
    category: str
    brand: str
    model: str
    loft: str | None = None
    shaft: str | None = None
    carry_distance: int | None = None
    notes: str | None = None
    purchase_date: date | None = None
    purchase_price: float | None = None


class UserWITBItem(UserWITBItemBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserWITBItemCreate(UserWITBItemBase):
    pass


class UserWITBItemUpdate(BaseModel):
    category: str | None = None
    brand: str | None = None
    model: str | None = None
    loft: str | None = None
    shaft: str | None = None
    carry_distance: int | None = None
    notes: str | None = None
    purchase_date: date | None = None
    purchase_price: float | None = None


class UserBagResponse(BaseModel):
    """Schema for user's complete bag of equipment."""

    items: list[UserWITBItem]
    total: int
