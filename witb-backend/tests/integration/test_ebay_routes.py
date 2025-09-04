"""Integration tests for eBay routes following CLAUDE.md T-2."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from tests.fixtures.ebay_api_responses import EBayAPIFixtures


class TestEBayRoutes:
    """Integration tests for eBay API routes."""

    @pytest.fixture
    def client(self):
        """FastAPI test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_ebay_repo(self):
        """Mock eBay repository for testing."""
        return AsyncMock()

    @patch("services.ebay_service.EBayRepository")
    def test_search_golf_equipment_returns_valid_response(
        self, mock_repo_class, client
    ):
        """Test search endpoint returns properly formatted response."""
        mock_repo = AsyncMock()
        mock_repo.search_products.return_value = EBayAPIFixtures.valid_search_response()
        mock_repo_class.return_value = mock_repo

        response = client.get(
            "/ebay/search",
            params={
                "brand": "TaylorMade",
                "model": "Stealth",
                "condition": "New",
                "limit": 10,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "products" in data
        assert "total_found" in data
        assert "search_query" in data
        assert len(data["products"]) <= 10
        assert data["search_query"] == "TaylorMade Stealth"

        # Verify product structure
        if data["products"]:
            product = data["products"][0]
            required_fields = [
                "product_id",
                "title",
                "price_info",
                "listing_url",
                "listing_type",
            ]
            for field in required_fields:
                assert field in product, f"Missing field: {field}"

    @patch("services.ebay_service.EBayRepository")
    def test_search_golf_equipment_with_price_filters(self, mock_repo_class, client):
        """Test search endpoint with price filtering parameters."""
        mock_repo = AsyncMock()
        mock_repo.search_products.return_value = EBayAPIFixtures.valid_search_response()
        mock_repo_class.return_value = mock_repo

        response = client.get(
            "/ebay/search",
            params={
                "brand": "Titleist",
                "min_price": 100.00,
                "max_price": 500.00,
                "condition": "Used",
            },
        )

        assert response.status_code == 200

        # Verify repository was called with correct parameters
        mock_repo.search_products.assert_called_once()
        call_args = mock_repo.search_products.call_args
        assert call_args.kwargs["brand"] == "Titleist"
        assert call_args.kwargs["min_price"] == 100.00
        assert call_args.kwargs["max_price"] == 500.00
        assert call_args.kwargs["condition"] == "Used"

    @patch("services.ebay_service.EBayRepository")
    def test_search_golf_equipment_handles_empty_results(self, mock_repo_class, client):
        """Test search endpoint when no results are found."""
        mock_repo = AsyncMock()
        mock_repo.search_products.return_value = EBayAPIFixtures.empty_search_response()
        mock_repo_class.return_value = mock_repo

        response = client.get("/ebay/search", params={"brand": "NonExistentBrand"})

        assert response.status_code == 200
        data = response.json()

        assert data["total_found"] == 0
        assert len(data["products"]) == 0
        assert data["search_query"] == "NonExistentBrand"

    def test_search_golf_equipment_validates_parameters(self, client):
        """Test search endpoint parameter validation."""
        # Test limit validation
        response = client.get("/ebay/search", params={"limit": 0})
        assert response.status_code == 422  # Validation error

        response = client.get("/ebay/search", params={"limit": 300})
        assert response.status_code == 422  # Exceeds maximum

        # Test negative price validation
        response = client.get("/ebay/search", params={"min_price": -100})
        assert response.status_code == 200  # Should accept, let eBay API handle

    @patch("services.ebay_service.EBayRepository")
    def test_search_golf_equipment_handles_api_errors(self, mock_repo_class, client):
        """Test search endpoint error handling."""
        from exceptions import DatabaseOperationError

        mock_repo = AsyncMock()
        mock_repo.search_products.side_effect = DatabaseOperationError(
            "search_products", "eBay API error"
        )
        mock_repo_class.return_value = mock_repo

        response = client.get("/ebay/search", params={"brand": "TaylorMade"})

        assert response.status_code == 500
        assert "eBay API error" in response.json()["detail"]

    @patch("services.ebay_service.EBayRepository")
    def test_get_product_details_returns_valid_response(self, mock_repo_class, client):
        """Test product details endpoint returns properly formatted response."""
        mock_repo = AsyncMock()
        mock_repo.get_product_details.return_value = (
            EBayAPIFixtures.valid_product_details_response()
        )
        mock_repo_class.return_value = mock_repo

        product_id = "334567890123"
        response = client.get(f"/ebay/product/{product_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["product_id"] == product_id
        assert "title" in data
        assert "price_info" in data
        assert "listing_url" in data

        # Verify price_info structure
        price_info = data["price_info"]
        assert "current_price" in price_info
        assert "currency" in price_info
        assert "condition" in price_info

    @patch("services.ebay_service.EBayRepository")
    def test_get_product_details_handles_not_found(self, mock_repo_class, client):
        """Test product details endpoint when product is not found."""
        from exceptions import DatabaseOperationError

        mock_repo = AsyncMock()
        mock_repo.get_product_details.side_effect = DatabaseOperationError(
            "get_product_details", "Product 123456789 not found"
        )
        mock_repo_class.return_value = mock_repo

        response = client.get("/ebay/product/123456789")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @patch("services.ebay_service.EBayRepository")
    def test_get_product_details_handles_api_errors(self, mock_repo_class, client):
        """Test product details endpoint error handling."""
        from exceptions import DatabaseOperationError

        mock_repo = AsyncMock()
        mock_repo.get_product_details.side_effect = DatabaseOperationError(
            "get_product_details", "eBay API error"
        )
        mock_repo_class.return_value = mock_repo

        response = client.get("/ebay/product/334567890123")

        assert response.status_code == 500
        assert "eBay API error" in response.json()["detail"]

    def test_enrich_witb_items_accepts_valid_request(self, client):
        """Test WITB enrichment endpoint accepts valid request structure."""
        request_data = {
            "witb_item_ids": [
                "550e8400-e29b-41d4-a716-446655440000",
                "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            ],
            "search_options": {"brand": "TaylorMade", "condition": "New", "limit": 10},
        }

        # This will return empty list since enrich_witb_items_with_pricing is placeholder
        response = client.post("/ebay/enrich-witb", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)  # Returns list of EnrichedWITBItem

    def test_enrich_witb_items_validates_request_format(self, client):
        """Test WITB enrichment endpoint validates request format."""
        # Missing required field
        invalid_request = {"search_options": {"brand": "TaylorMade"}}

        response = client.post("/ebay/enrich-witb", json=invalid_request)
        assert response.status_code == 422  # Validation error

        # Invalid UUID format
        invalid_uuid_request = {"witb_item_ids": ["not-a-valid-uuid"]}

        response = client.post("/ebay/enrich-witb", json=invalid_uuid_request)
        assert response.status_code == 422  # Validation error

    @patch("services.ebay_service.EBayRepository")
    def test_search_golf_equipment_handles_mixed_valid_invalid_items(
        self, mock_repo_class, client
    ):
        """Test search endpoint handles response with mix of valid/invalid items."""
        mock_repo = AsyncMock()
        mock_repo.search_products.return_value = (
            EBayAPIFixtures.search_response_with_mixed_items()
        )
        mock_repo_class.return_value = mock_repo

        response = client.get("/ebay/search", params={"brand": "Titleist"})

        assert response.status_code == 200
        data = response.json()

        # Should only return valid items (1 out of 2)
        assert len(data["products"]) == 1
        assert data["products"][0]["product_id"] == "334567890123"

    def test_search_endpoint_default_parameters(self, client):
        """Test search endpoint uses appropriate default values."""
        with patch("services.ebay_service.EBayRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.search_products.return_value = (
                EBayAPIFixtures.empty_search_response()
            )
            mock_repo_class.return_value = mock_repo

            response = client.get("/ebay/search")

            assert response.status_code == 200

            # Verify default parameters were used
            call_args = mock_repo.search_products.call_args
            assert call_args.kwargs["condition"] == "New"
            assert call_args.kwargs["limit"] == 20
            assert call_args.kwargs["brand"] is None
            assert call_args.kwargs["model"] is None

    @patch("services.ebay_service.EBayRepository")
    def test_oauth_token_error_propagates_correctly(self, mock_repo_class, client):
        """Test that OAuth token errors are handled appropriately."""
        from exceptions import DatabaseOperationError

        mock_repo = AsyncMock()
        mock_repo.search_products.side_effect = DatabaseOperationError(
            "get_access_token", "eBay credentials not configured"
        )
        mock_repo_class.return_value = mock_repo

        response = client.get("/ebay/search", params={"brand": "TaylorMade"})

        assert response.status_code == 500
        assert "credentials not configured" in response.json()["detail"]
