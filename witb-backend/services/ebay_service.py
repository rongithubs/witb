"""eBay service for business logic following CLAUDE.md O-4."""

import re
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from custom_types import EBayProductId
from exceptions import DatabaseOperationError
from repositories.ebay_repository import EBayRepository


class EBayService:
    """Service for eBay business logic."""

    def __init__(self, db: AsyncSession):
        self.ebay_repo = EBayRepository(db)
        self.db = db

    async def search_golf_equipment(
        self, search_request: schemas.EBaySearchRequest
    ) -> schemas.EBaySearchResponse:
        """Search for golf equipment on eBay with business logic filtering."""
        # Get raw search results from repository
        raw_results = await self.ebay_repo.search_products(
            brand=search_request.brand,
            model=search_request.model,
            category=search_request.category,
            condition=search_request.condition,
            max_price=search_request.max_price,
            min_price=search_request.min_price,
            limit=search_request.limit,
        )

        # Transform eBay API response to our schema
        products = []
        for item in raw_results.get("itemSummaries", []):
            try:
                product = self._transform_ebay_item_to_product(item)
                if product and self._is_relevant_golf_item(product, search_request):
                    products.append(product)
            except Exception:
                # Skip items that fail transformation - don't break the entire search
                continue

        # Build search query for response
        query_parts = []
        if search_request.brand:
            query_parts.append(search_request.brand)
        if search_request.model:
            query_parts.append(search_request.model)
        search_query = " ".join(query_parts) if query_parts else "golf equipment"

        return schemas.EBaySearchResponse(
            products=products,
            total_found=raw_results.get("total", len(products)),
            page=1,  # eBay API uses offset, we simplify to page 1 for now
            per_page=search_request.limit,
            search_query=search_query,
        )

    def _transform_ebay_item_to_product(
        self, item: dict[str, Any]
    ) -> schemas.EBayProduct | None:
        """Transform eBay API item to our product schema."""
        try:
            # Extract price information
            price_info = self._extract_price_info(item)
            if not price_info:
                return None

            # Extract basic product info
            title = item.get("title", "")
            brand, model = self._extract_brand_and_model(title)

            return schemas.EBayProduct(
                product_id=item["itemId"],
                title=title,
                brand=brand,
                model=model,
                category=self._categorize_golf_item(title),
                price_info=price_info,
                listing_url=item.get("itemWebUrl", ""),
                image_url=self._get_best_image_url(item),
                seller_info=self._extract_seller_info(item),
                location=item.get("itemLocation", {}).get("country"),
                listing_type=item.get("buyingOptions", ["FixedPrice"])[0],
            )
        except KeyError:
            # Required fields missing
            return None

    def _extract_price_info(self, item: dict[str, Any]) -> schemas.EBayPriceInfo | None:
        """Extract price information from eBay item."""
        price_data = item.get("price")
        if not price_data:
            return None

        try:
            current_price = float(price_data["value"])
            currency = price_data.get("currency", "USD")

            # Get condition
            condition = item.get("condition", "Unknown")
            if isinstance(condition, dict):
                condition = condition.get("conditionDisplayName", "Unknown")

            # Extract shipping cost if available
            shipping_cost = None
            shipping_options = item.get("shippingOptions", [])
            if shipping_options:
                shipping_info = shipping_options[0].get("shippingCost")
                if shipping_info and shipping_info.get("value"):
                    shipping_cost = float(shipping_info["value"])

            return schemas.EBayPriceInfo(
                current_price=current_price,
                currency=currency,
                condition=condition,
                shipping_cost=shipping_cost,
            )
        except (ValueError, KeyError, TypeError):
            return None

    def _extract_brand_and_model(self, title: str) -> tuple[str | None, str | None]:
        """Extract brand and model from product title using golf equipment patterns."""
        title_upper = title.upper()

        # Common golf brands
        golf_brands = {
            "TAYLORMADE": "TaylorMade",
            "TAYLOR MADE": "TaylorMade",
            "CALLAWAY": "Callaway",
            "TITLEIST": "Titleist",
            "PING": "Ping",
            "MIZUNO": "Mizuno",
            "COBRA": "Cobra",
            "WILSON": "Wilson",
            "CLEVELAND": "Cleveland",
            "SRIXON": "Srixon",
            "ODYSSEY": "Odyssey",
            "SCOTTY CAMERON": "Scotty Cameron",
        }

        brand = None
        for brand_key, brand_value in golf_brands.items():
            if brand_key in title_upper:
                brand = brand_value
                break

        # Extract model - typically the first few words after brand
        model = None
        if brand:
            # Find and remove brand from title (case insensitive) and extract model
            title_upper = title.upper()
            for brand_key in golf_brands:
                if brand_key in title_upper:
                    brand_pos = title_upper.find(brand_key)
                    if brand_pos != -1:
                        remaining = title[brand_pos + len(brand_key) :].strip()
                        words = remaining.split()[:3]  # Take up to 3 words as model
                        if words:
                            model = " ".join(words)
                        break

        return brand, model

    def _categorize_golf_item(self, title: str) -> str | None:
        """Categorize golf equipment based on title."""
        title_upper = title.upper()

        if any(word in title_upper for word in ["DRIVER", "1 WOOD"]):
            return "Driver"
        elif any(word in title_upper for word in ["WOOD", "3W", "5W", "7W"]):
            return "Wood"
        elif any(word in title_upper for word in ["HYBRID", "RESCUE", "UTILITY"]):
            return "Hybrid"
        elif any(word in title_upper for word in ["IRON", "IRONS"]) and not any(
            word in title_upper for word in ["WEDGE"]
        ):
            return "Iron"
        elif any(word in title_upper for word in ["WEDGE", "SW", "PW", "GW", "LW"]):
            return "Wedge"
        elif "PUTTER" in title_upper:
            return "Putter"
        elif any(word in title_upper for word in ["BALL", "GOLF BALL"]):
            return "Ball"

        return "Golf Equipment"

    def _is_relevant_golf_item(
        self, product: schemas.EBayProduct, search_request: schemas.EBaySearchRequest
    ) -> bool:
        """Filter products for relevance to golf equipment search."""
        # Basic golf equipment check
        title_upper = product.title.upper()
        golf_keywords = [
            "GOLF",
            "DRIVER",
            "IRON",
            "PUTTER",
            "WEDGE",
            "WOOD",
            "HYBRID",
            "BALL",
        ]

        if not any(keyword in title_upper for keyword in golf_keywords):
            return False

        # Brand matching if specified
        if search_request.brand and product.brand:
            if search_request.brand.upper() not in product.brand.upper():
                return False

        # Model matching if specified (fuzzy match)
        if search_request.model and product.model:
            if not self._fuzzy_model_match(search_request.model, product.model):
                return False

        # Category matching - be strict about club type
        if search_request.category:
            if not self._category_matches(product, search_request.category):
                return False

        return True

    def _fuzzy_model_match(self, search_model: str, product_model: str) -> bool:
        """Perform fuzzy matching for golf equipment models."""
        search_upper = search_model.upper()
        product_upper = product_model.upper()

        # Exact match
        if search_upper in product_upper or product_upper in search_upper:
            return True

        # Split into words and check for common words
        search_words = set(search_upper.split())
        product_words = set(product_upper.split())

        # If at least half the search words are found, consider it a match
        if search_words and len(search_words & product_words) >= len(search_words) / 2:
            return True

        return False

    def _category_matches(
        self, product: schemas.EBayProduct, requested_category: str
    ) -> bool:
        """Check if product category matches the requested category strictly."""
        if not product.category:
            return False

        # Check if category keywords are present
        if not self._has_category_keywords(
            product.title, product.category, requested_category
        ):
            return False

        # Apply category-specific exclusions
        if self._has_exclusion_keywords(product.title, requested_category):
            return False

        return True

    def _has_category_keywords(
        self, title: str, product_category: str, requested_category: str
    ) -> bool:
        """Check if title or product category contains required keywords."""
        # Convert all inputs to uppercase for case-insensitive matching
        title_upper = title.upper()
        product_category_upper = product_category.upper()
        requested_category_upper = requested_category.upper()

        category_keywords = {
            "DRIVER": ["DRIVER"],
            "WOOD": ["WOOD", "FAIRWAY"],
            "HYBRID": ["HYBRID", "RESCUE"],
            "IRON": ["IRON"],
            "WEDGE": ["WEDGE"],
            "PUTTER": ["PUTTER"],
            "BALL": ["BALL", "GOLF BALL"],
        }

        required_keywords = category_keywords.get(
            requested_category_upper, [requested_category_upper]
        )

        return any(
            keyword in title_upper or keyword in product_category_upper
            for keyword in required_keywords
        )

    def _has_exclusion_keywords(self, title: str, requested_category: str) -> bool:
        """Check if title contains exclusion keywords for the category."""
        # Convert inputs to uppercase for case-insensitive matching
        title_upper = title.upper()
        requested_category_upper = requested_category.upper()

        exclusion_rules = {
            "DRIVER": ["HYBRID", "RESCUE", "WOOD", "FAIRWAY", "3W", "5W", "7W"],
            # Add other exclusion rules as needed
        }

        exclude_keywords = exclusion_rules.get(requested_category_upper, [])
        return any(exclude in title_upper for exclude in exclude_keywords)

    def _get_best_image_url(self, item: dict[str, Any]) -> str | None:
        """Get the best quality image URL from eBay item."""
        image_info = item.get("image")
        if not image_info:
            return None

        # Prefer larger images if available
        if "imageUrl" in image_info:
            return image_info["imageUrl"]

        return None

    def _extract_seller_info(self, item: dict[str, Any]) -> dict[str, Any] | None:
        """Extract seller information from eBay item."""
        seller = item.get("seller")
        if not seller:
            return None

        return {
            "username": seller.get("username"),
            "feedback_percentage": seller.get("feedbackPercentage"),
            "feedback_score": seller.get("feedbackScore"),
        }

    async def get_product_details(self, product_id: str) -> schemas.EBayProduct:
        """Get detailed product information."""
        raw_product = await self.ebay_repo.get_product_details(
            EBayProductId(product_id)
        )

        product = self._transform_ebay_item_to_product(raw_product)
        if not product:
            raise DatabaseOperationError(
                "get_product_details", f"Failed to parse product {product_id}"
            )

        return product

    async def enrich_witb_items_with_pricing(
        self, witb_item_ids: list[str]
    ) -> list[schemas.EnrichedWITBItem]:
        """Enrich WITB items with current eBay pricing data."""
        # TODO: This would integrate with existing WITB repository
        # to fetch items and enrich them with eBay pricing
        # For now, return empty list as placeholder
        return []
