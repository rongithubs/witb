"""Tests for EBay service following CLAUDE.md T-3 pattern."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from services.ebay_service import EBayService


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock(spec=AsyncSession)


@pytest.fixture
def ebay_service(mock_db):
    """Create EBayService instance with mocked dependencies."""
    return EBayService(mock_db)


@pytest.fixture
def sample_product():
    """Create sample EBayProduct for testing."""
    return schemas.EBayProduct(
        product_id="test-123",
        title="TaylorMade Qi10 Driver 9° Stiff Flex",
        brand="TaylorMade",
        model="Qi10",
        category="Driver",
        price_info=schemas.EBayPriceInfo(
            current_price=499.99, currency="USD", condition="New"
        ),
        listing_url="https://example.com",
        listing_type="FixedPrice",
    )


class TestCategoryMatching:
    """Test category matching functionality."""

    def test_driver_matches_driver_category(self, ebay_service, sample_product):
        """Driver products should match driver category."""
        result = ebay_service._category_matches(sample_product, "Driver")
        assert result is True

    def test_driver_excludes_hybrid_in_title(self, ebay_service):
        """Driver search should exclude products with hybrid keywords."""
        hybrid_product = schemas.EBayProduct(
            product_id="test-hybrid",
            title="TaylorMade Qi10 Hybrid Rescue Club",
            brand="TaylorMade",
            model="Qi10",
            category="Hybrid",
            price_info=schemas.EBayPriceInfo(
                current_price=299.99, currency="USD", condition="New"
            ),
            listing_url="https://example.com",
            listing_type="FixedPrice",
        )

        result = ebay_service._category_matches(hybrid_product, "Driver")
        assert result is False

    def test_driver_excludes_wood_in_title(self, ebay_service):
        """Driver search should exclude products with wood keywords."""
        wood_product = schemas.EBayProduct(
            product_id="test-wood",
            title="TaylorMade Qi10 3 Wood Fairway",
            brand="TaylorMade",
            model="Qi10",
            category="Wood",
            price_info=schemas.EBayPriceInfo(
                current_price=349.99, currency="USD", condition="New"
            ),
            listing_url="https://example.com",
            listing_type="FixedPrice",
        )

        result = ebay_service._category_matches(wood_product, "Driver")
        assert result is False

    def test_putter_matches_putter_category(self, ebay_service):
        """Putter products should match putter category."""
        putter_product = schemas.EBayProduct(
            product_id="test-putter",
            title="Scotty Cameron Newport Putter",
            brand="Scotty Cameron",
            model="Newport",
            category="Putter",
            price_info=schemas.EBayPriceInfo(
                current_price=399.99, currency="USD", condition="Used"
            ),
            listing_url="https://example.com",
            listing_type="FixedPrice",
        )

        result = ebay_service._category_matches(putter_product, "Putter")
        assert result is True

    def test_no_category_returns_false(self, ebay_service):
        """Products without category should return False."""
        no_category_product = schemas.EBayProduct(
            product_id="test-no-cat",
            title="Golf Club",
            brand="Generic",
            model="Club",
            category=None,
            price_info=schemas.EBayPriceInfo(
                current_price=99.99, currency="USD", condition="Used"
            ),
            listing_url="https://example.com",
            listing_type="FixedPrice",
        )

        result = ebay_service._category_matches(no_category_product, "Driver")
        assert result is False

    def test_has_category_keywords_driver(self, ebay_service):
        """Test _has_category_keywords for driver."""
        result = ebay_service._has_category_keywords(
            "TAYLORMADE QI10 DRIVER 9 DEGREES", "DRIVER", "DRIVER"
        )
        assert result is True

    def test_has_category_keywords_wood_fairway(self, ebay_service):
        """Test _has_category_keywords for wood with fairway keyword."""
        result = ebay_service._has_category_keywords(
            "TAYLORMADE QI10 3 FAIRWAY WOOD", "WOOD", "WOOD"
        )
        assert result is True

    def test_has_exclusion_keywords_driver_excludes_hybrid(self, ebay_service):
        """Test _has_exclusion_keywords excludes hybrid from driver search."""
        result = ebay_service._has_exclusion_keywords(
            "TAYLORMADE QI10 HYBRID RESCUE", "DRIVER"
        )
        assert result is True

    def test_has_exclusion_keywords_no_exclusions_for_putter(self, ebay_service):
        """Test _has_exclusion_keywords has no exclusions for putter."""
        result = ebay_service._has_exclusion_keywords(
            "SCOTTY CAMERON NEWPORT PUTTER", "PUTTER"
        )
        assert result is False

    def test_golf_ball_matches_ball_category(self, ebay_service):
        """Golf ball products should match ball category."""
        ball_product = schemas.EBayProduct(
            product_id="test-ball",
            title="Titleist Pro V1 Golf Balls Dozen",
            brand="Titleist",
            model="Pro V1",
            category="Ball",
            price_info=schemas.EBayPriceInfo(
                current_price=54.99, currency="USD", condition="New"
            ),
            listing_url="https://example.com",
            listing_type="FixedPrice",
        )

        result = ebay_service._category_matches(ball_product, "Ball")
        assert result is True

    def test_case_insensitive_matching(self, ebay_service):
        """Category matching should be case insensitive."""
        result = ebay_service._has_category_keywords(
            "TAYLORMADE QI10 DRIVER",  # Title is uppercase
            "DRIVER",  # Category is uppercase
            "DRIVER",  # Requested is uppercase
        )
        assert result is True

        # Test mixed case
        result = ebay_service._has_category_keywords(
            "taylormade qi10 driver",  # Title is lowercase
            "driver",  # Category is lowercase
            "DRIVER",  # Requested is uppercase
        )
        assert result is True
