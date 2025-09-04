"""eBay repository for API operations following CLAUDE.md D-4."""

import os
from datetime import datetime, timedelta
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from custom_types import EBayProductId
from exceptions import DatabaseOperationError


class EBayRepository:
    """Repository for eBay API operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client_id = os.getenv("EBAY_CLIENT_ID")
        self.client_secret = os.getenv("EBAY_CLIENT_SECRET")
        self.environment = os.getenv("EBAY_ENVIRONMENT", "SANDBOX")
        self.base_url = self._get_base_url()
        self._access_token: str | None = None
        self._token_expires: datetime | None = None

    def _get_base_url(self) -> str:
        """Get eBay API base URL based on environment."""
        if self.environment == "PRODUCTION":
            return "https://api.ebay.com"
        return "https://api.sandbox.ebay.com"

    async def _get_access_token(self) -> str:
        """Get OAuth access token using client credentials flow."""
        if (
            self._access_token
            and self._token_expires
            and datetime.now() < self._token_expires
        ):
            return self._access_token

        if not self.client_id or not self.client_secret:
            raise DatabaseOperationError(
                "get_access_token", "eBay credentials not configured"
            )

        auth_url = f"{self.base_url}/identity/v1/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        data = {
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    auth_url,
                    headers=headers,
                    data=data,
                    auth=(self.client_id, self.client_secret),
                    timeout=30.0,
                )
                response.raise_for_status()

                token_data = response.json()
                self._access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self._token_expires = datetime.now() + timedelta(
                    seconds=expires_in - 60
                )

                return self._access_token

            except httpx.HTTPStatusError as e:
                raise DatabaseOperationError(
                    "get_access_token", f"eBay API auth error: {e.response.status_code}"
                )
            except Exception as e:
                raise DatabaseOperationError("get_access_token", str(e))

    async def search_products(
        self,
        brand: str | None = None,
        model: str | None = None,
        category: str | None = None,
        condition: str | None = "New",
        max_price: float | None = None,
        min_price: float | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Search for golf equipment products on eBay."""
        access_token = await self._get_access_token()

        # Build search query
        query_parts = []
        if brand:
            query_parts.append(brand)
        if model:
            query_parts.append(model)
        if category:
            query_parts.append(category)
        if not query_parts:
            query_parts.append("golf")

        search_url = f"{self.base_url}/buy/browse/v1/item_summary/search"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        }

        params: dict[str, str] = {
            "q": " ".join(query_parts),
            "category_ids": "1617",  # Golf category
            "limit": str(min(limit, 200)),  # eBay API limit
        }

        # Add price filters
        filter_parts = []
        if condition:
            filter_parts.append(f"conditions:{condition}")
        if max_price:
            filter_parts.append(f"price:[..{max_price}]")
        if min_price:
            filter_parts.append(f"price:[{min_price}..]")

        if filter_parts:
            params["filter"] = ",".join(filter_parts)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    search_url, headers=headers, params=params, timeout=30.0
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                raise DatabaseOperationError(
                    "search_products", f"eBay search error: {e.response.status_code}"
                )
            except Exception as e:
                raise DatabaseOperationError("search_products", str(e))

    async def get_product_details(self, product_id: EBayProductId) -> dict[str, Any]:
        """Get detailed information for a specific eBay product."""
        access_token = await self._get_access_token()

        details_url = f"{self.base_url}/buy/browse/v1/item/{product_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(details_url, headers=headers, timeout=30.0)
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise DatabaseOperationError(
                        "get_product_details", f"Product {product_id} not found"
                    )
                raise DatabaseOperationError(
                    "get_product_details",
                    f"eBay product details error: {e.response.status_code}",
                )
            except Exception as e:
                raise DatabaseOperationError("get_product_details", str(e))
