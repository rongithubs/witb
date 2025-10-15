"""Tests for WITB service following CLAUDE.md T-1."""

from unittest.mock import AsyncMock

import pytest

import schemas
from repositories.witb_repository import WITBRepository
from services.witb_service import WitbService


class TestWitbService:
    """Unit tests for WitbService."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_witb_repo(self):
        """Mock WITB repository."""
        return AsyncMock(spec=WITBRepository)

    @pytest.fixture
    def witb_service(self, mock_db, mock_witb_repo):
        """WITB service with mocked dependencies."""
        service = WitbService(mock_db)
        service.witb_repo = mock_witb_repo
        return service

    async def test_get_club_usage_leaderboard_returns_structured_response(
        self, witb_service, mock_witb_repo
    ):
        """Test leaderboard returns properly structured response with enriched URLs."""
        # Arrange
        mock_repo_data = {
            "Driver": [
                {
                    "brand": "TaylorMade",
                    "model": "Qi10",
                    "count": 15,
                    "percentage": 45.5,
                    "rank": 1,
                },
                {
                    "brand": "Callaway",
                    "model": "Paradym",
                    "count": 12,
                    "percentage": 36.4,
                    "rank": 2,
                },
            ],
            "Putter": [
                {
                    "brand": "Scotty Cameron",
                    "model": "Special Select",
                    "count": 8,
                    "percentage": 50.0,
                    "rank": 1,
                }
            ],
        }
        mock_witb_repo.get_club_usage_leaderboard.return_value = mock_repo_data

        # Act
        result = await witb_service.get_club_usage_leaderboard(limit=10)

        # Assert
        assert isinstance(result, schemas.LeaderboardResponse)
        assert result.total_categories == 2
        assert result.total_unique_combinations == 3

        # Check Driver category
        driver_items = result.categories["Driver"]
        assert len(driver_items) == 2
        assert driver_items[0].brand == "TaylorMade"
        assert driver_items[0].model == "Qi10"
        assert driver_items[0].count == 15
        assert driver_items[0].percentage == 45.5
        assert driver_items[0].rank == 1
        assert driver_items[0].brand_url is not None  # URL enrichment

        # Check repository was called correctly
        mock_witb_repo.get_club_usage_leaderboard.assert_called_once_with(
            category_filter=None, limit=10
        )

    async def test_get_club_usage_leaderboard_with_category_filter(
        self, witb_service, mock_witb_repo
    ):
        """Test leaderboard with category filter."""
        # Arrange
        mock_repo_data = {
            "Driver": [
                {
                    "brand": "TaylorMade",
                    "model": "Qi10",
                    "count": 15,
                    "percentage": 100.0,
                    "rank": 1,
                }
            ]
        }
        mock_witb_repo.get_club_usage_leaderboard.return_value = mock_repo_data

        # Act
        result = await witb_service.get_club_usage_leaderboard(
            category_filter="Driver", limit=5
        )

        # Assert
        assert result.total_categories == 1
        assert "Driver" in result.categories

        # Check repository was called with correct parameters
        mock_witb_repo.get_club_usage_leaderboard.assert_called_once_with(
            category_filter="Driver", limit=5
        )

    async def test_get_club_usage_leaderboard_handles_empty_data(
        self, witb_service, mock_witb_repo
    ):
        """Test leaderboard handles empty repository response."""
        # Arrange
        mock_witb_repo.get_club_usage_leaderboard.return_value = {}

        # Act
        result = await witb_service.get_club_usage_leaderboard()

        # Assert
        assert isinstance(result, schemas.LeaderboardResponse)
        assert result.total_categories == 0
        assert result.total_unique_combinations == 0
        assert result.categories == {}

    async def test_get_brands_combines_database_and_static_brands(
        self, witb_service, mock_witb_repo
    ):
        """Test get_brands returns combined brands from database and static list."""
        # Arrange
        db_brands = ["Ping", "Mizuno", "Wilson"]
        mock_witb_repo.get_distinct_brands.return_value = db_brands

        # Act
        result = await witb_service.get_brands()

        # Assert
        assert isinstance(result, schemas.BrandResponse)
        assert result.total > 0
        assert "Ping" in result.brands
        assert "Mizuno" in result.brands
        assert "Wilson" in result.brands
        assert "TaylorMade" in result.brands  # From BRAND_URLS
        assert "Callaway" in result.brands  # From BRAND_URLS

        # Check repository was called
        mock_witb_repo.get_distinct_brands.assert_called_once()

    async def test_get_brands_deduplicates_case_insensitive(
        self, witb_service, mock_witb_repo
    ):
        """Test get_brands deduplicates brands case-insensitively."""
        # Arrange
        db_brands = ["taylormade", "CALLAWAY", "Ping"]
        mock_witb_repo.get_distinct_brands.return_value = db_brands

        # Act
        result = await witb_service.get_brands()

        # Assert
        brand_names_lower = [b.lower() for b in result.brands]
        assert brand_names_lower.count("taylormade") == 1
        assert brand_names_lower.count("callaway") == 1
        assert brand_names_lower.count("ping") == 1

    async def test_get_brands_returns_sorted_alphabetically(
        self, witb_service, mock_witb_repo
    ):
        """Test get_brands returns brands sorted alphabetically."""
        # Arrange
        db_brands = ["Zebra Golf", "Alpha Brand", "Mid Brand"]
        mock_witb_repo.get_distinct_brands.return_value = db_brands

        # Act
        result = await witb_service.get_brands()

        # Assert
        assert result.brands == sorted(result.brands)

    async def test_get_brands_handles_empty_database(
        self, witb_service, mock_witb_repo
    ):
        """Test get_brands handles empty database response."""
        # Arrange
        mock_witb_repo.get_distinct_brands.return_value = []

        # Act
        result = await witb_service.get_brands()

        # Assert
        assert isinstance(result, schemas.BrandResponse)
        assert result.total > 0  # Should still have static brands
        assert "TaylorMade" in result.brands  # From BRAND_URLS
