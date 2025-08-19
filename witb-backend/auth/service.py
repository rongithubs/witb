"""Auth service for user authentication following CLAUDE.md O-4."""

import json
from uuid import UUID, uuid4
from typing import Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from jose import jwt, JWTError

import models
import schemas
from custom_types import UserId, SupabaseUserId
from supabase_client import get_supabase_config
from exceptions import DatabaseOperationError


class AuthService:
    """Service for authentication business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.config = get_supabase_config()

    async def get_or_create_user(
        self, supabase_user_id: SupabaseUserId, user_data: Dict[str, Any]
    ) -> schemas.User:
        """Get existing user or create new one from Supabase auth."""
        try:
            # Try to get existing user
            result = await self.db.execute(
                select(models.User).where(
                    models.User.supabase_user_id == supabase_user_id
                )
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                # Update user info if needed
                if user_data.get("email") and existing_user.email != user_data["email"]:
                    existing_user.email = user_data["email"]
                if user_data.get("phone") and existing_user.phone != user_data["phone"]:
                    existing_user.phone = user_data["phone"]

                await self.db.commit()
                await self.db.refresh(existing_user)
                return schemas.User.model_validate(existing_user)

            # Create new user
            new_user = models.User(
                supabase_user_id=supabase_user_id,
                email=user_data.get("email"),
                phone=user_data.get("phone"),
            )
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)

            return schemas.User.model_validate(new_user)

        except IntegrityError as e:
            await self.db.rollback()
            raise DatabaseOperationError("create_user", str(e))
        except Exception as e:
            await self.db.rollback()
            raise DatabaseOperationError("get_or_create_user", str(e))

    async def get_user_by_supabase_id(
        self, supabase_user_id: SupabaseUserId
    ) -> schemas.User | None:
        """Get user by Supabase user ID."""
        try:
            result = await self.db.execute(
                select(models.User).where(
                    models.User.supabase_user_id == supabase_user_id
                )
            )
            user = result.scalar_one_or_none()
            return schemas.User.model_validate(user) if user else None
        except Exception as e:
            raise DatabaseOperationError("get_user_by_supabase_id", str(e))

    def verify_jwt_token(self, token: str) -> schemas.AuthUser:
        """Verify and decode JWT token from Supabase."""
        try:
            jwt_secret = self.config.jwt_secret

            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=["HS256"],
                options={
                    "verify_aud": False,  # Disable audience verification
                    "verify_exp": True,   # Keep expiration verification
                },
            )

            # Extract and validate required fields
            sub = payload.get("sub")
            if not sub:
                raise ValueError("Missing 'sub' field in JWT payload")

            return schemas.AuthUser(
                user_id=UUID(sub),  # Supabase user ID
                supabase_user_id=UUID(sub),
                email=payload.get("email"),
                phone=payload.get("phone"),
                exp=payload.get("exp", 0),
                iat=payload.get("iat", 0),
            )
        except JWTError as e:
            raise ValueError(f"Invalid JWT token: {str(e)}")
        except Exception as e:
            raise ValueError(f"Token verification failed: {str(e)}")
