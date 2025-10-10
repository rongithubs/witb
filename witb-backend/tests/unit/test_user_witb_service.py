"""Unit tests for UserWITBService following CLAUDE.md T-6."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import schemas
from custom_types import UserId, UserWITBItemId
from services.user_witb_service import UserWITBService


class TestUserWITBService:
    """Unit tests for UserWITBService."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def user_witb_service(self, mock_db):
        """UserWITBService instance with mocked dependencies."""
        service = UserWITBService(mock_db)
        service.user_witb_repo = AsyncMock()
        return service

    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID for testing."""
        return UserId(uuid4())

    @pytest.fixture
    def sample_user_witb_item_data(self):
        """Sample user WITB item data for testing."""
        return schemas.UserWITBItemCreate(
            category="Driver",
            brand="TaylorMade",
            model="Qi10",
            loft="9°",
            shaft="Fujikura Ventus Blue",
            carry_distance=280,
            notes="Great distance and forgiveness",
        )

    @pytest.fixture
    def sample_user_witb_item(self):
        """Sample user WITB item for testing."""
        return MagicMock(
            id=uuid4(),
            user_id=uuid4(),
            category="Driver",
            brand="TaylorMade",
            model="Qi10",
            loft="9°",
            shaft="Fujikura Ventus Blue",
            carry_distance=280,
            notes="Great distance and forgiveness",
        )

    async def test_create_user_witb_item_success(
        self, user_witb_service, sample_user_id, sample_user_witb_item_data, sample_user_witb_item
    ):
        """Test successful creation of user WITB item."""
        # Arrange
        user_witb_service.user_witb_repo.create_user_witb_item.return_value = sample_user_witb_item

        # Act
        result = await user_witb_service.create_user_witb_item(
            sample_user_id, sample_user_witb_item_data
        )

        # Assert
        user_witb_service.user_witb_repo.create_user_witb_item.assert_called_once_with(
            sample_user_id, sample_user_witb_item_data.model_dump()
        )
        assert isinstance(result, schemas.UserWITBItem)

    async def test_get_user_bag_with_items(
        self, user_witb_service, sample_user_id, sample_user_witb_item
    ):
        """Test getting user bag with equipment items."""
        # Arrange
        mock_items = [sample_user_witb_item]
        user_witb_service.user_witb_repo.get_user_bag.return_value = mock_items

        # Act
        result = await user_witb_service.get_user_bag(sample_user_id)

        # Assert
        user_witb_service.user_witb_repo.get_user_bag.assert_called_once_with(sample_user_id)
        assert isinstance(result, schemas.UserBagResponse)
        assert result.total == 1
        assert len(result.items) == 1

    async def test_get_user_bag_empty(self, user_witb_service, sample_user_id):
        """Test getting empty user bag."""
        # Arrange
        user_witb_service.user_witb_repo.get_user_bag.return_value = []

        # Act
        result = await user_witb_service.get_user_bag(sample_user_id)

        # Assert
        assert isinstance(result, schemas.UserBagResponse)
        assert result.total == 0
        assert len(result.items) == 0

    async def test_update_user_witb_item_success(
        self, user_witb_service, sample_user_id, sample_user_witb_item
    ):
        """Test successful update of user WITB item."""
        # Arrange
        item_id = UserWITBItemId(uuid4())
        update_data = schemas.UserWITBItemUpdate(carry_distance=290, notes="Updated notes")
        user_witb_service.user_witb_repo.update_user_witb_item.return_value = sample_user_witb_item

        # Act
        result = await user_witb_service.update_user_witb_item(
            item_id, sample_user_id, update_data
        )

        # Assert
        expected_update_dict = {"carry_distance": 290, "notes": "Updated notes"}
        user_witb_service.user_witb_repo.update_user_witb_item.assert_called_once_with(
            item_id, sample_user_id, expected_update_dict
        )
        assert isinstance(result, schemas.UserWITBItem)

    async def test_delete_user_witb_item_success(
        self, user_witb_service, sample_user_id
    ):
        """Test successful deletion of user WITB item."""
        # Arrange
        item_id = UserWITBItemId(uuid4())
        user_witb_service.user_witb_repo.delete_user_witb_item.return_value = True

        # Act
        result = await user_witb_service.delete_user_witb_item(item_id, sample_user_id)

        # Assert
        user_witb_service.user_witb_repo.delete_user_witb_item.assert_called_once_with(
            item_id, sample_user_id
        )
        assert result is True

    def test_enrich_witb_items_with_urls_adds_brand_urls(self, user_witb_service):
        """Test that brand URLs are added to user WITB items."""
        # Arrange
        mock_item = MagicMock()
        mock_item.brand = "TaylorMade"
        items = [mock_item]

        # Act
        enriched_items = user_witb_service._enrich_witb_items_with_urls(items)

        # Assert
        assert len(enriched_items) == 1
        assert hasattr(enriched_items[0], 'product_url')
        assert enriched_items[0].product_url is not None