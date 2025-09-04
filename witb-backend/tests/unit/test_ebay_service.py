"""Unit tests for EBayService following CLAUDE.md testing guidelines."""

from unittest.mock import AsyncMock

import pytest

import schemas
from services.ebay_service import EBayService
from tests.fixtures.ebay_api_responses import EBayAPIFixtures


class TestEBayService:
    """Unit tests for EBayService following CLAUDE.md T-7."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def ebay_service(self, mock_db):
        """EBayService instance with mocked dependencies."""
        service = EBayService(mock_db)
        service.ebay_repo = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_search_golf_equipment_transforms_response_correctly(
        self, ebay_service
    ):
        """Test that search_golf_equipment transforms eBay API response correctly."""
        # Mock repository response
        ebay_service.ebay_repo.search_products.return_value = (
            EBayAPIFixtures.valid_search_response()
        )

        search_request = schemas.EBaySearchRequest(
            brand="TaylorMade", model="Stealth", limit=20
        )

        result = await ebay_service.search_golf_equipment(search_request)

        assert isinstance(result, schemas.EBaySearchResponse)
        assert len(result.products) == 2
        assert result.total_found == 125
        assert result.search_query == "TaylorMade Stealth"

        # Verify first product transformation
        first_product = result.products[0]
        assert first_product.product_id == "334567890123"
        assert (
            first_product.title
            == "TaylorMade Stealth Driver 10.5° Right Hand Regular Flex"
        )
        assert first_product.brand == "TaylorMade"
        assert first_product.price_info.current_price == 399.99
        assert first_product.price_info.currency == "USD"

    @pytest.mark.asyncio
    async def test_search_golf_equipment_handles_empty_results(self, ebay_service):
        """Test search handling when no products are found."""
        ebay_service.ebay_repo.search_products.return_value = (
            EBayAPIFixtures.empty_search_response()
        )

        search_request = schemas.EBaySearchRequest(brand="NonExistentBrand")

        result = await ebay_service.search_golf_equipment(search_request)

        assert result.total_found == 0
        assert len(result.products) == 0
        assert result.search_query == "NonExistentBrand"

    def test_extract_brand_and_model_handles_taylormade_variations(self, ebay_service):
        """Test brand extraction handles TaylorMade name variations."""
        test_cases = [
            ("TaylorMade Stealth Driver", "TaylorMade", "Stealth"),
            ("TAYLORMADE SIM2 Max Iron", "TaylorMade", "SIM2 Max"),
            ("Taylor Made M6 Woods", "TaylorMade", "M6 Woods"),
        ]

        for title, expected_brand, expected_model_start in test_cases:
            brand, model = ebay_service._extract_brand_and_model(title)
            assert brand == expected_brand, f"Failed for title: {title}"
            assert model and model.startswith(
                expected_model_start
            ), f"Model mismatch for title: {title}"

    def test_extract_brand_and_model_handles_multiple_brands(self, ebay_service):
        """Test brand extraction for various golf brands."""
        test_cases = [
            ("Callaway Rogue Driver", "Callaway", "Rogue Driver"),
            ("Titleist Pro V1 Golf Balls", "Titleist", "Pro V1 Golf"),
            ("Ping G425 Max Driver", "Ping", "G425 Max Driver"),
            ("Mizuno JPX 921 Hot Metal Irons", "Mizuno", "JPX 921 Hot"),
        ]

        for title, expected_brand, expected_model_start in test_cases:
            brand, model = ebay_service._extract_brand_and_model(title)
            assert brand == expected_brand, f"Brand mismatch for: {title}"
            assert model and model.startswith(
                expected_model_start
            ), f"Model mismatch for: {title}"

    def test_categorize_golf_item_identifies_categories_correctly(self, ebay_service):
        """Test golf equipment categorization logic."""
        test_cases = [
            ("TaylorMade Stealth Driver 10.5°", "Driver"),
            ("Callaway Rogue 3 Wood", "Wood"),
            ("Titleist 716 AP1 Irons 5-PW", "Iron"),
            ("Vokey SM9 Sand Wedge 56°", "Wedge"),
            ("Scotty Cameron Newport Putter", "Putter"),
            ("Pro V1 Golf Balls Dozen", "Ball"),
            ("TaylorMade M4 Hybrid 22°", "Hybrid"),
            ("Generic Golf Accessory", "Golf Equipment"),
        ]

        for title, expected_category in test_cases:
            category = ebay_service._categorize_golf_item(title)
            assert category == expected_category, f"Category mismatch for: {title}"

    def test_is_relevant_golf_item_filters_correctly(self, ebay_service):
        """Test relevance filtering for golf equipment."""
        # Create mock product
        golf_product = schemas.EBayProduct(
            product_id="123",
            title="TaylorMade Stealth Driver Golf Club",
            brand="TaylorMade",
            model="Stealth",
            price_info=schemas.EBayPriceInfo(
                current_price=399.99, currency="USD", condition="New"
            ),
            listing_url="https://ebay.com/123",
            listing_type="FixedPrice",
        )

        # Test matching search request
        matching_request = schemas.EBaySearchRequest(
            brand="TaylorMade", model="Stealth"
        )
        assert ebay_service._is_relevant_golf_item(golf_product, matching_request)

        # Test non-matching brand
        non_matching_request = schemas.EBaySearchRequest(
            brand="Callaway", model="Stealth"
        )
        assert not ebay_service._is_relevant_golf_item(
            golf_product, non_matching_request
        )

        # Test non-golf item
        non_golf_product = schemas.EBayProduct(
            product_id="456",
            title="Baseball Bat Wilson A2000",
            brand="Wilson",
            model="A2000",
            price_info=schemas.EBayPriceInfo(
                current_price=199.99, currency="USD", condition="New"
            ),
            listing_url="https://ebay.com/456",
            listing_type="FixedPrice",
        )
        assert not ebay_service._is_relevant_golf_item(
            non_golf_product, matching_request
        )

    def test_fuzzy_model_match_handles_variations(self, ebay_service):
        """Test fuzzy matching for golf equipment model names."""
        test_cases = [
            ("Stealth", "TaylorMade Stealth Driver", True),
            ("M6", "TaylorMade M6 Max Driver", True),
            ("JPX 921", "Mizuno JPX 921 Hot Metal", True),
            ("Pro V1", "Titleist Pro V1x", False),  # Different model
            ("Stealth", "TaylorMade SIM2", False),  # Completely different
            ("G425 Max", "Ping G425 Max Driver", True),  # Exact match
        ]

        for search_model, product_model, expected_match in test_cases:
            result = ebay_service._fuzzy_model_match(search_model, product_model)
            assert (
                result == expected_match
            ), f"Fuzzy match failed for {search_model} vs {product_model}"

    def test_extract_price_info_handles_missing_fields(self, ebay_service):
        """Test price extraction with missing or malformed data."""
        # Valid price data
        valid_item = {
            "price": {"value": "399.99", "currency": "USD"},
            "condition": "New",
        }
        price_info = ebay_service._extract_price_info(valid_item)
        assert price_info.current_price == 399.99
        assert price_info.currency == "USD"
        assert price_info.condition == "New"

        # Missing price
        missing_price_item = {"condition": "New"}
        assert ebay_service._extract_price_info(missing_price_item) is None

        # Invalid price value
        invalid_price_item = {
            "price": {"value": "invalid", "currency": "USD"},
            "condition": "New",
        }
        assert ebay_service._extract_price_info(invalid_price_item) is None

        # Complex condition object
        complex_condition_item = {
            "price": {"value": "199.99", "currency": "USD"},
            "condition": {"conditionDisplayName": "Used - Excellent"},
        }
        price_info = ebay_service._extract_price_info(complex_condition_item)
        assert price_info.current_price == 199.99
        assert price_info.condition == "Used - Excellent"

    def test_transform_ebay_item_to_product_handles_malformed_items(self, ebay_service):
        """Test product transformation with malformed eBay API responses."""
        # Valid item
        valid_item = EBayAPIFixtures.valid_search_response()["itemSummaries"][0]
        product = ebay_service._transform_ebay_item_to_product(valid_item)
        assert product is not None
        assert product.product_id == "334567890123"

        # Missing required field
        malformed_item = {"title": "Test Item"}  # Missing itemId and price
        assert ebay_service._transform_ebay_item_to_product(malformed_item) is None

        # Item with no price
        no_price_item = {
            "itemId": "123456789",
            "title": "Test Golf Club",
            "itemWebUrl": "https://ebay.com/123",
        }
        assert ebay_service._transform_ebay_item_to_product(no_price_item) is None

    @pytest.mark.asyncio
    async def test_get_product_details_calls_repository_correctly(self, ebay_service):
        """Test get_product_details calls repository with correct parameters."""
        ebay_service.ebay_repo.get_product_details.return_value = (
            EBayAPIFixtures.valid_product_details_response()
        )

        product_id = "334567890123"
        result = await ebay_service.get_product_details(product_id)

        ebay_service.ebay_repo.get_product_details.assert_called_once()
        assert isinstance(result, schemas.EBayProduct)
        assert result.product_id == product_id

    def test_get_best_image_url_extracts_correctly(self, ebay_service):
        """Test image URL extraction from eBay item data."""
        # Item with image
        item_with_image = {
            "image": {"imageUrl": "https://i.ebayimg.com/images/g/abc123/s-l1600.jpg"}
        }
        assert (
            ebay_service._get_best_image_url(item_with_image)
            == "https://i.ebayimg.com/images/g/abc123/s-l1600.jpg"
        )

        # Item without image
        item_without_image = {"title": "Test Item"}
        assert ebay_service._get_best_image_url(item_without_image) is None

        # Item with empty image object
        item_empty_image = {"image": {}}
        assert ebay_service._get_best_image_url(item_empty_image) is None

    def test_extract_seller_info_handles_variations(self, ebay_service):
        """Test seller information extraction."""
        # Complete seller info
        item_with_seller = {
            "seller": {
                "username": "golf_pro_shop",
                "feedbackPercentage": 99.5,
                "feedbackScore": 15420,
            }
        }
        seller_info = ebay_service._extract_seller_info(item_with_seller)
        assert seller_info["username"] == "golf_pro_shop"
        assert seller_info["feedback_percentage"] == 99.5
        assert seller_info["feedback_score"] == 15420

        # No seller info
        item_no_seller = {"title": "Test Item"}
        assert ebay_service._extract_seller_info(item_no_seller) is None

        # Partial seller info
        item_partial_seller = {"seller": {"username": "test_seller"}}
        seller_info = ebay_service._extract_seller_info(item_partial_seller)
        assert seller_info["username"] == "test_seller"
        assert seller_info.get("feedback_percentage") is None
