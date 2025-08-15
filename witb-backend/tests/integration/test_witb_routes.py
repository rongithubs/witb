"""Integration tests for WITB routes following CLAUDE.md T-2."""

from httpx import AsyncClient

from main import app


class TestWitbRoutes:
    """Integration tests for WITB routes."""

    async def test_get_club_leaderboard_returns_valid_response(self):
        """Test GET /witb/leaderboard returns structured data."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.get("/witb/leaderboard")

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

    async def test_get_club_leaderboard_with_category_filter(self):
        """Test GET /witb/leaderboard with category filter."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Act
            response = await client.get("/witb/leaderboard?category=Driver&limit=5")

            # Assert
            assert response.status_code == 200
            data = response.json()

            # If any data exists, verify structure
            if data["total_categories"] > 0:
                for category, items in data["categories"].items():
                    assert isinstance(items, list)
                    if items:  # If category has items
                        item = items[0]
                        assert "brand" in item
                        assert "model" in item
                        assert "count" in item
                        assert "percentage" in item
                        assert "rank" in item
                        assert isinstance(item["count"], int)
                        assert isinstance(item["percentage"], float)
                        assert isinstance(item["rank"], int)

    async def test_get_club_leaderboard_validates_limit_parameter(self):
        """Test leaderboard endpoint validates limit parameter bounds."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test invalid limit (too high)
            response = await client.get("/witb/leaderboard?limit=100")
            assert response.status_code == 422  # Validation error

            # Test invalid limit (too low)
            response = await client.get("/witb/leaderboard?limit=0")
            assert response.status_code == 422  # Validation error

            # Test valid limit
            response = await client.get("/witb/leaderboard?limit=10")
            assert response.status_code == 200
