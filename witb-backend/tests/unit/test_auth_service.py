"""Unit tests for AuthService following CLAUDE.md testing guidelines."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import pytest

import models
import schemas
from auth.service import AuthService
from custom_types import SupabaseUserId


class TestAuthService:
    """Unit tests for AuthService following CLAUDE.md T-7."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def auth_service(self, mock_db):
        """AuthService instance with mocked dependencies."""
        with patch("auth.service.get_supabase_config") as mock_config:
            mock_config.return_value.service_role_key = "test-key"
            mock_config.return_value.jwt_secret = "test-jwt-secret-key-for-testing"
            return AuthService(mock_db)

    @pytest.mark.asyncio
    async def test_get_or_create_user_creates_new_user(self, auth_service, mock_db):
        """Test that get_or_create_user creates new user when none exists."""
        # Arrange
        supabase_user_id = SupabaseUserId(uuid4())
        user_data = {"email": "test@example.com", "phone": "+1234567890"}

        # Mock no existing user found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Mock new user creation
        new_user_id = uuid4()
        created_at = datetime.now()
        
        # Mock the User model instance that will be created
        with patch("auth.service.models.User") as MockUserClass:
            mock_user_instance = MagicMock()
            mock_user_instance.id = new_user_id
            mock_user_instance.supabase_user_id = supabase_user_id
            mock_user_instance.email = user_data["email"]
            mock_user_instance.phone = user_data["phone"]
            mock_user_instance.created_at = created_at
            mock_user_instance.updated_at = created_at
            
            MockUserClass.return_value = mock_user_instance
            mock_db.refresh = AsyncMock()

            # Act
            result = await auth_service.get_or_create_user(supabase_user_id, user_data)

            # Assert
            MockUserClass.assert_called_once_with(
                supabase_user_id=supabase_user_id,
                email=user_data["email"],
                phone=user_data["phone"],
            )
            mock_db.add.assert_called_once_with(mock_user_instance)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_user_instance)
            assert isinstance(result, schemas.User)
            assert str(result.id) == str(new_user_id)
            assert result.email == user_data["email"]

    @pytest.mark.asyncio
    async def test_get_or_create_user_updates_existing_user(
        self, auth_service, mock_db
    ):
        """Test that get_or_create_user updates existing user email."""
        # Arrange
        supabase_user_id = SupabaseUserId(uuid4())
        user_data = {"email": "new@example.com", "phone": "+1234567890"}

        existing_user = MagicMock()
        existing_user.id = uuid4()
        existing_user.supabase_user_id = supabase_user_id
        existing_user.email = "old@example.com"
        existing_user.phone = "+1234567890"
        existing_user.created_at = datetime.now()
        existing_user.updated_at = datetime.now()

        # Mock existing user found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_user
        mock_db.execute.return_value = mock_result
        mock_db.refresh = AsyncMock()

        # Act
        result = await auth_service.get_or_create_user(supabase_user_id, user_data)

        # Assert
        assert existing_user.email == user_data["email"]
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(existing_user)
        assert isinstance(result, schemas.User)

    def test_verify_jwt_token_valid_token(self, auth_service):
        """Test that verify_jwt_token successfully decodes valid token."""
        # Arrange
        test_payload = {
            "sub": str(uuid4()),
            "email": "test@example.com",
            "phone": "+1234567890",
            "exp": 1234567890,
            "iat": 1234567800,
        }

        # Act
        with patch("jose.jwt.decode", return_value=test_payload) as mock_decode:
            result = auth_service.verify_jwt_token("test-token")

        # Assert
        assert isinstance(result, schemas.AuthUser)
        assert str(result.supabase_user_id) == test_payload["sub"]
        assert result.email == test_payload["email"]
        assert result.phone == test_payload["phone"]
        assert result.exp == test_payload["exp"]
        assert result.iat == test_payload["iat"]

    def test_verify_jwt_token_invalid_token(self, auth_service):
        """Test that verify_jwt_token raises ValueError for invalid token."""
        # Act & Assert
        with patch("jose.jwt.decode", side_effect=Exception("Invalid token")):
            with pytest.raises(ValueError, match="Token verification failed"):
                auth_service.verify_jwt_token("invalid-token")

    def test_verify_jwt_token_missing_sub_field(self, auth_service):
        """Test that verify_jwt_token raises ValueError when sub field is missing."""
        # Arrange
        test_payload = {
            "email": "test@example.com",
            "exp": 1234567890,
            "iat": 1234567800,
            # Missing 'sub' field
        }

        # Act & Assert
        with patch("jose.jwt.decode", return_value=test_payload):
            with pytest.raises(ValueError, match="Missing 'sub' field in JWT payload"):
                auth_service.verify_jwt_token("test-token")

    def test_verify_jwt_token_empty_sub_field(self, auth_service):
        """Test that verify_jwt_token raises ValueError when sub field is empty."""
        # Arrange
        test_payload = {
            "sub": "",  # Empty sub field
            "email": "test@example.com",
            "exp": 1234567890,
            "iat": 1234567800,
        }

        # Act & Assert
        with patch("jose.jwt.decode", return_value=test_payload):
            with pytest.raises(ValueError, match="Missing 'sub' field in JWT payload"):
                auth_service.verify_jwt_token("test-token")

    def test_verify_jwt_token_with_signature_verification_enabled(self, auth_service):
        """Test that JWT verification uses proper secret and signature verification."""
        # Arrange
        test_token = "test-jwt-token"
        test_payload = {
            "sub": str(uuid4()),
            "email": "test@example.com",
            "exp": 1234567890,
            "iat": 1234567800,
        }

        # Act
        with patch("jose.jwt.decode", return_value=test_payload) as mock_decode:
            result = auth_service.verify_jwt_token(test_token)

        # Assert - Verify JWT decode called with correct parameters
        mock_decode.assert_called_once_with(
            test_token,
            "test-jwt-secret-key-for-testing",  # Our test JWT secret
            algorithms=["HS256"],
            options={
                "verify_aud": False,
                "verify_exp": True,
            },
        )
        # Note: verify_signature should be True by default (not explicitly disabled)
        assert isinstance(result, schemas.AuthUser)

    @pytest.mark.parametrize("invalid_payload", [
        {"sub": "invalid-uuid", "email": "test@example.com"},  # Invalid UUID
        {"sub": None, "email": "test@example.com"},  # None sub
        {},  # Empty payload
    ])
    def test_verify_jwt_token_invalid_payload_formats(self, auth_service, invalid_payload):
        """Test JWT verification with various invalid payload formats."""
        # Act & Assert
        with patch("jose.jwt.decode", return_value=invalid_payload):
            with pytest.raises(ValueError):
                auth_service.verify_jwt_token("test-token")

    def test_verify_jwt_token_jwt_error_handling(self, auth_service):
        """Test that JWTError is properly caught and converted to ValueError."""
        from jose import JWTError
        
        # Act & Assert
        with patch("jose.jwt.decode", side_effect=JWTError("Invalid signature")):
            with pytest.raises(ValueError, match="Invalid JWT token: Invalid signature"):
                auth_service.verify_jwt_token("test-token")

    def test_verify_jwt_token_uses_correct_jwt_secret(self, mock_db):
        """Test that AuthService uses jwt_secret from config, not service_role_key."""
        # Arrange
        test_jwt_secret = "correct-jwt-secret"
        test_service_role_key = "different-service-role-key"
        
        with patch("auth.service.get_supabase_config") as mock_config:
            mock_config.return_value.jwt_secret = test_jwt_secret
            mock_config.return_value.service_role_key = test_service_role_key
            auth_service = AuthService(mock_db)

        test_payload = {
            "sub": str(uuid4()),
            "email": "test@example.com",
            "exp": 1234567890,
        }

        # Act
        with patch("jose.jwt.decode", return_value=test_payload) as mock_decode:
            auth_service.verify_jwt_token("test-token")

        # Assert - Should use jwt_secret, not service_role_key
        mock_decode.assert_called_once()
        call_args = mock_decode.call_args
        assert call_args[0][1] == test_jwt_secret  # Second argument is the secret
        assert call_args[0][1] != test_service_role_key
