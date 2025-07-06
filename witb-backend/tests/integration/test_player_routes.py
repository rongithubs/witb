"""Integration tests for player routes following CLAUDE.md T-2."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from services.player_service import PlayerService
import schemas


class TestPlayerRoutes:
    """Integration tests for player endpoints following CLAUDE.md T-7."""

    async def test_create_player_success(self, client: TestClient, db_session: AsyncSession):
        """Test successful player creation through API."""
        # Arrange
        player_data = {
            "name": "Test Player",
            "country": "USA",
            "tour": "PGA Tour",
            "age": 25,
            "ranking": 1
        }
        
        # Act
        response = client.post("/players/", json=player_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Player"
        assert data["country"] == "USA"
        assert "id" in data

    async def test_get_players_returns_paginated_response(self, client: TestClient, db_session: AsyncSession):
        """Test that get_players returns proper paginated structure."""
        # Act
        response = client.get("/players?page=1&per_page=10")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verify pagination structure
        required_fields = ["items", "total", "page", "per_page", "total_pages"]
        for field in required_fields:
            assert field in data
        
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert data["page"] == 1
        assert data["per_page"] == 10

    async def test_search_player_returns_exists_field(self, client: TestClient, db_session: AsyncSession):
        """Test that search endpoint returns exists boolean."""
        # Act
        response = client.get("/players/search?name=NonexistentPlayer")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "exists" in data
        assert isinstance(data["exists"], bool)

    async def test_get_player_invalid_id_returns_400(self, client: TestClient):
        """Test that invalid player ID returns 400 status."""
        # Act
        response = client.get("/players/invalid-uuid")
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Invalid player ID format" in data["detail"]

    async def test_get_nonexistent_player_returns_404(self, client: TestClient):
        """Test that nonexistent player returns 404 status."""
        # Arrange
        nonexistent_id = "12345678-1234-5678-9abc-123456789012"
        
        # Act
        response = client.get(f"/players/{nonexistent_id}")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Player not found" in data["detail"]