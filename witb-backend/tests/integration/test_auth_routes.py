"""Integration tests for auth routes following CLAUDE.md testing guidelines."""

from unittest.mock import patch, MagicMock
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

import schemas
from custom_types import SupabaseUserId


class TestAuthRoutes:
    """Integration tests for auth routes following CLAUDE.md T-2."""

    def test_auth_health_check(self, client: TestClient):
        """Test auth health check endpoint returns success."""
        # Act
        response = client.get("/auth/health")

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "status": "auth_healthy",
            "message": "Authentication system is running",
        }

    def test_get_current_user_info_without_token(self, client: TestClient):
        """Test /auth/me endpoint returns 401 without authentication."""
        # Act
        response = client.get("/auth/me")

        # Assert
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

    def test_get_current_user_info_with_valid_token(
        self, client: TestClient
    ):
        """Test /auth/me endpoint returns user info with valid token."""
        # Arrange
        mock_auth_user = schemas.AuthUser(
            user_id=uuid4(),
            supabase_user_id=uuid4(),
            email="test@example.com",
            phone="+1234567890",
            exp=1234567890,
            iat=1234567800,
        )

        mock_user = schemas.User(
            id=mock_auth_user.user_id,
            supabase_user_id=mock_auth_user.supabase_user_id,
            email=mock_auth_user.email,
            phone=mock_auth_user.phone,
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )

        # Act
        with patch("auth.dependencies.AuthService") as MockAuthService:
            mock_service = MockAuthService.return_value
            mock_service.verify_jwt_token.return_value = mock_auth_user
            mock_service.get_or_create_user.return_value = mock_user

            response = client.get(
                "/auth/me", headers={"Authorization": "Bearer test-token"}
            )

        # Assert
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == mock_user.email
        assert user_data["phone"] == mock_user.phone

    def test_verify_token_with_valid_token(self, client: TestClient):
        """Test /auth/verify-token endpoint with valid token."""
        # Arrange
        user_id = uuid4()
        supabase_user_id = uuid4()

        mock_auth_user = schemas.AuthUser(
            user_id=user_id,
            supabase_user_id=supabase_user_id,
            email="test@example.com",
            phone="+1234567890",
            exp=1234567890,
            iat=1234567800,
        )

        mock_user = schemas.User(
            id=user_id,
            supabase_user_id=supabase_user_id,
            email="test@example.com",
            phone="+1234567890",
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )

        # Act
        with patch("auth.dependencies.AuthService") as MockAuthService:
            mock_service = MockAuthService.return_value
            mock_service.verify_jwt_token.return_value = mock_auth_user
            mock_service.get_or_create_user.return_value = mock_user

            response = client.post(
                "/auth/verify-token", headers={"Authorization": "Bearer test-token"}
            )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["user_id"] == str(user_id)
        assert data["supabase_user_id"] == str(supabase_user_id)

    def test_verify_token_with_invalid_token(self, client: TestClient):
        """Test /auth/verify-token endpoint with invalid token."""
        # Act
        with patch("auth.dependencies.AuthService") as MockAuthService:
            mock_service = MockAuthService.return_value
            mock_service.verify_jwt_token.side_effect = ValueError("Invalid token")

            response = client.post(
                "/auth/verify-token", headers={"Authorization": "Bearer invalid-token"}
            )

        # Assert
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]
