"""eBay routes following CLAUDE.md O-4 (thin route handlers)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from dependencies import get_db
from exceptions import DatabaseOperationError
from services.ebay_service import EBayService

router = APIRouter(prefix="/ebay", tags=["ebay"])


@router.get("/search", response_model=schemas.EBaySearchResponse)
async def search_golf_equipment(
    brand: str | None = Query(None, description="Golf equipment brand"),
    model: str | None = Query(None, description="Equipment model"),
    category: str | None = Query(None, description="Equipment category"),
    condition: str | None = Query("New", description="Item condition"),
    max_price: float | None = Query(None, description="Maximum price"),
    min_price: float | None = Query(None, description="Minimum price"),
    limit: int = Query(20, ge=1, le=200, description="Number of results"),
    db: AsyncSession = Depends(get_db),
) -> schemas.EBaySearchResponse:
    """Search for golf equipment on eBay."""
    search_request = schemas.EBaySearchRequest(
        brand=brand,
        model=model,
        category=category,
        condition=condition,
        max_price=max_price,
        min_price=min_price,
        limit=limit,
    )

    service = EBayService(db)
    try:
        return await service.search_golf_equipment(search_request)
    except DatabaseOperationError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/product/{product_id}", response_model=schemas.EBayProduct)
async def get_product_details(
    product_id: str, db: AsyncSession = Depends(get_db)
) -> schemas.EBayProduct:
    """Get detailed information for a specific eBay product."""
    service = EBayService(db)
    try:
        return await service.get_product_details(product_id)
    except DatabaseOperationError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=404, detail=f"Product {product_id} not found"
            )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enrich-witb", response_model=list[schemas.EnrichedWITBItem])
async def enrich_witb_items(
    request: schemas.EBayEnrichmentRequest, db: AsyncSession = Depends(get_db)
) -> list[schemas.EnrichedWITBItem]:
    """Enrich WITB items with current eBay pricing data."""
    service = EBayService(db)
    try:
        # Convert UUID list to string list for service
        item_ids = [str(item_id) for item_id in request.witb_item_ids]
        return await service.enrich_witb_items_with_pricing(item_ids)
    except DatabaseOperationError as e:
        raise HTTPException(status_code=500, detail=str(e))
