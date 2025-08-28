"""Integration tests for favorite player routes following CLAUDE.md T-2."""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from unittest.mock import patch

import models
import schemas


class TestFavoritePlayerRoutes:
    """Integration tests for favorite player API endpoints."""

    @pytest.fixture
    async def test_user(self, db_session):
        """Create a test user."""
        user = models.User(
            id=uuid4(), supabase_user_id=uuid4(), email="test@example.com"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def test_player(self, db_session):
        """Create a test player with WITB items."""
        player = models.Player(
            id=uuid4(), name="Tiger Woods", country="USA", tour="PGA Tour", ranking=1
        )
        db_session.add(player)
        await db_session.flush()  # Get player ID for WITB item

        # Add WITB item to test complete data loading
        witb_item = models.WITBItem(
            player_id=player.id,
            category="Driver",
            brand="TaylorMade",
            model="Stealth 2 Plus",
            loft="9°",
        )
        db_session.add(witb_item)
        await db_session.commit()
        await db_session.refresh(player)
        return player

    def test_get_favorites_empty_list(self, client: TestClient, test_user):
        """Test getting favorites returns empty list when user has no favorites."""
        # Mock authentication
        mock_auth_user = schemas.AuthUser(
            user_id=test_user.id,
            supabase_user_id=test_user.supabase_user_id,
            email=test_user.email,
            phone=None,
            exp=1234567890,
            iat=1234567800,
        )

        mock_user = schemas.User(
            id=test_user.id,
            supabase_user_id=test_user.supabase_user_id,
            email=test_user.email,
            phone=None,
            created_at=test_user.created_at,
            updated_at=test_user.updated_at,
        )

        with patch("auth.dependencies.AuthService") as MockAuthService:
            mock_service = MockAuthService.return_value
            mock_service.verify_jwt_token.return_value = mock_auth_user
            mock_service.get_or_create_user.return_value = mock_user

            response = client.get(
                "/auth/me/favorites", headers={"Authorization": "Bearer test-token"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["favorites"] == []

    def test_add_favorite_player_success(
        self, client: TestClient, test_user, test_player
    ):
        """Test adding a player to favorites succeeds."""
        # Mock authentication
        mock_user = schemas.User(
            id=test_user.id,
            supabase_user_id=test_user.supabase_user_id,
            email=test_user.email,
            phone=None,
            created_at=test_user.created_at,
            updated_at=test_user.updated_at,
        )

        with patch(
            "auth.dependencies.get_current_user_from_db", return_value=mock_user
        ):
            response = client.post(
                "/auth/me/favorites",
                json={"player_id": str(test_player.id)},
                headers={"Authorization": "Bearer test-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["player"]["id"] == str(test_player.id)
        assert data["player"]["name"] == test_player.name

    def test_add_favorite_player_invalid_player_id(self, client: TestClient, test_user):
        """Test adding non-existent player returns 404."""
        # Mock authentication
        mock_user = schemas.User(
            id=test_user.id,
            supabase_user_id=test_user.supabase_user_id,
            email=test_user.email,
            phone=None,
            created_at=test_user.created_at,
            updated_at=test_user.updated_at,
        )

        fake_player_id = str(uuid4())
        with patch(
            "auth.dependencies.get_current_user_from_db", return_value=mock_user
        ):
            response = client.post(
                "/auth/me/favorites",
                json={"player_id": fake_player_id},
                headers={"Authorization": "Bearer test-token"},
            )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_add_favorite_player_duplicate_returns_existing(
        self, client: TestClient, test_user, test_player
    ):
        """Test adding duplicate favorite returns existing favorite."""
        # Mock authentication
        mock_user = schemas.User(
            id=test_user.id,
            supabase_user_id=test_user.supabase_user_id,
            email=test_user.email,
            phone=None,
            created_at=test_user.created_at,
            updated_at=test_user.updated_at,
        )

        with patch(
            "auth.dependencies.get_current_user_from_db", return_value=mock_user
        ):
            # Add favorite first time
            response1 = client.post(
                "/auth/me/favorites",
                json={"player_id": str(test_player.id)},
                headers={"Authorization": "Bearer test-token"},
            )
            assert response1.status_code == 200

            # Add same favorite again
            response2 = client.post(
                "/auth/me/favorites",
                json={"player_id": str(test_player.id)},
                headers={"Authorization": "Bearer test-token"},
            )
            assert response2.status_code == 200
            # Should return the existing favorite
            assert response1.json()["id"] == response2.json()["id"]

    def test_get_favorites_with_data(self, client: TestClient, test_user, test_player):
        """Test getting favorites returns player data after adding favorite."""
        # Mock authentication
        mock_user = schemas.User(
            id=test_user.id,
            supabase_user_id=test_user.supabase_user_id,
            email=test_user.email,
            phone=None,
            created_at=test_user.created_at,
            updated_at=test_user.updated_at,
        )

        with patch(
            "auth.dependencies.get_current_user_from_db", return_value=mock_user
        ):
            # Add favorite
            client.post(
                "/auth/me/favorites",
                json={"player_id": str(test_player.id)},
                headers={"Authorization": "Bearer test-token"},
            )

            # Get favorites
            response = client.get(
                "/auth/me/favorites", headers={"Authorization": "Bearer test-token"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["favorites"]) == 1
        favorite_player = data["favorites"][0]["player"]
        assert favorite_player["name"] == test_player.name

        # Verify WITB data is loaded
        assert "witb_items" in favorite_player
        assert len(favorite_player["witb_items"]) == 1
        witb_item = favorite_player["witb_items"][0]
        assert witb_item["category"] == "Driver"
        assert witb_item["brand"] == "TaylorMade"
        assert witb_item["model"] == "Stealth 2 Plus"

    def test_remove_favorite_player_success(
        self, client: TestClient, test_user, test_player
    ):
        """Test removing favorite player succeeds."""
        # Mock authentication
        mock_user = schemas.User(
            id=test_user.id,
            supabase_user_id=test_user.supabase_user_id,
            email=test_user.email,
            phone=None,
            created_at=test_user.created_at,
            updated_at=test_user.updated_at,
        )

        with patch(
            "auth.dependencies.get_current_user_from_db", return_value=mock_user
        ):
            # Add favorite first
            client.post(
                "/auth/me/favorites",
                json={"player_id": str(test_player.id)},
                headers={"Authorization": "Bearer test-token"},
            )

            # Remove favorite
            response = client.delete(
                f"/auth/me/favorites/{test_player.id}",
                headers={"Authorization": "Bearer test-token"},
            )

        assert response.status_code == 200
        assert "removed from favorites" in response.json()["message"]

    def test_remove_favorite_player_not_found(self, client: TestClient, test_user):
        """Test removing non-existent favorite returns 404."""
        # Mock authentication
        mock_user = schemas.User(
            id=test_user.id,
            supabase_user_id=test_user.supabase_user_id,
            email=test_user.email,
            phone=None,
            created_at=test_user.created_at,
            updated_at=test_user.updated_at,
        )

        fake_player_id = str(uuid4())
        with patch(
            "auth.dependencies.get_current_user_from_db", return_value=mock_user
        ):
            response = client.delete(
                f"/auth/me/favorites/{fake_player_id}",
                headers={"Authorization": "Bearer test-token"},
            )

        assert response.status_code == 404
        assert "not found in favorites" in response.json()["detail"]

    def test_remove_favorite_player_invalid_uuid(self, client: TestClient, test_user):
        """Test removing favorite with invalid UUID returns 400."""
        # Mock authentication
        mock_user = schemas.User(
            id=test_user.id,
            supabase_user_id=test_user.supabase_user_id,
            email=test_user.email,
            phone=None,
            created_at=test_user.created_at,
            updated_at=test_user.updated_at,
        )

        with patch(
            "auth.dependencies.get_current_user_from_db", return_value=mock_user
        ):
            response = client.delete(
                "/auth/me/favorites/invalid-uuid",
                headers={"Authorization": "Bearer test-token"},
            )

        assert response.status_code == 400
        assert "Invalid player ID format" in response.json()["detail"]

    def test_favorites_endpoints_require_authentication(self, client: TestClient):
        """Test that favorite endpoints require authentication."""
        # Test GET without auth
        response = client.get("/auth/me/favorites")
        assert response.status_code == 401

        # Test POST without auth
        response = client.post("/auth/me/favorites", json={"player_id": str(uuid4())})
        assert response.status_code == 401

        # Test DELETE without auth
        response = client.delete(f"/auth/me/favorites/{uuid4()}")
        assert response.status_code == 401
