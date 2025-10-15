"""Integration tests for WITB routes following CLAUDE.md T-2."""

import pytest
from fastapi.testclient import TestClient


class TestWitbRoutes:
    """Integration tests for WITB routes."""

    def test_get_club_leaderboard_returns_valid_response(self, client: TestClient):
        """Test GET /witb/leaderboard returns structured data."""
        # Act
        response = client.get("/witb/leaderboard")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "categories" in data
        assert "total_categories" in data
        assert "total_unique_combinations" in data
        assert isinstance(data["categories"], dict)
        assert isinstance(data["total_categories"], int)
        assert isinstance(data["total_unique_combinations"], int)

        # With empty test database, should return empty categories
        assert data["total_categories"] == 0
        assert data["total_unique_combinations"] == 0

    def test_get_club_leaderboard_with_category_filter(self, client: TestClient):
        """Test GET /witb/leaderboard with category filter."""
        # Act
        response = client.get("/witb/leaderboard?category=Driver&limit=5")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "categories" in data
        assert "total_categories" in data
        assert "total_unique_combinations" in data

        # With empty test database, should return empty results
        assert data["total_categories"] == 0

    def test_get_club_leaderboard_validates_limit_parameter(self, client: TestClient):
        """Test leaderboard endpoint validates limit parameter bounds."""
        # Test invalid limit (too high)
        response = client.get("/witb/leaderboard?limit=100")
        assert response.status_code == 422  # Validation error

        # Test invalid limit (too low)
        response = client.get("/witb/leaderboard?limit=0")
        assert response.status_code == 422  # Validation error

        # Test valid limit
        response = client.get("/witb/leaderboard?limit=10")
        assert response.status_code == 200

    def test_get_brands_returns_valid_response(self, client: TestClient):
        """Test GET /witb/brands returns brand list with static brands."""
        # Act
        response = client.get("/witb/brands")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "brands" in data
        assert "total" in data
        assert isinstance(data["brands"], list)
        assert isinstance(data["total"], int)

        # Should have at least static brands from BRAND_URLS
        assert data["total"] > 0
        assert len(data["brands"]) == data["total"]

        # Check for some known static brands
        assert "TaylorMade" in data["brands"]
        assert "Callaway" in data["brands"]
        assert "Titleist" in data["brands"]

    def test_get_brands_returns_sorted_alphabetically(self, client: TestClient):
        """Test GET /witb/brands returns brands sorted alphabetically."""
        # Act
        response = client.get("/witb/brands")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Check brands are sorted
        brands = data["brands"]
        assert brands == sorted(brands)
