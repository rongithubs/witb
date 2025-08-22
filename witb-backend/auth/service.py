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
from custom_types import UserId, SupabaseUserId, PlayerId
from supabase_client import get_supabase_config
from exceptions import DatabaseOperationError, PlayerNotFoundError
from repositories.favorite_player_repository import FavoritePlayerRepository
from services.player_service import PlayerService


class AuthService:
    """Service for authentication business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.config = get_supabase_config()
        self.favorite_repo = FavoritePlayerRepository(db)

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
                    "verify_exp": True,  # Keep expiration verification
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

    async def add_favorite_player(
        self, user_id: UserId, player_id: PlayerId
    ) -> schemas.FavoritePlayerResponse:
        """Add player to user's favorites."""
        try:
            # Verify player exists
            player_service = PlayerService(self.db)
            await player_service.get_player_by_id(
                str(player_id)
            )  # Will raise PlayerNotFoundError if not found

            # Add to favorites
            favorite = await self.favorite_repo.add_favorite_player(user_id, player_id)

            # Return with enriched player data
            player_service._enrich_witb_items_with_urls(favorite.player.witb_items)
            return schemas.FavoritePlayerResponse.model_validate(favorite)

        except IntegrityError:
            # Player already in favorites - return existing favorite
            favorites = await self.favorite_repo.get_user_favorites(user_id)
            for fav in favorites:
                if fav.player_id == player_id:
                    player_service = PlayerService(self.db)
                    player_service._enrich_witb_items_with_urls(fav.player.witb_items)
                    return schemas.FavoritePlayerResponse.model_validate(fav)
            raise DatabaseOperationError("add_favorite_player", "Unexpected state")
        except Exception as e:
            await self.db.rollback()
            raise DatabaseOperationError("add_favorite_player", str(e))

    async def remove_favorite_player(
        self, user_id: UserId, player_id: PlayerId
    ) -> bool:
        """Remove player from user's favorites."""
        try:
            return await self.favorite_repo.remove_favorite_player(user_id, player_id)
        except Exception as e:
            await self.db.rollback()
            raise DatabaseOperationError("remove_favorite_player", str(e))

    async def get_user_favorites(
        self, user_id: UserId
    ) -> schemas.UserFavoritesResponse:
        """Get user's favorite players with enriched data."""
        try:
            favorites = await self.favorite_repo.get_user_favorites(user_id)

            # Enrich player data with brand URLs
            player_service = PlayerService(self.db)
            for favorite in favorites:
                player_service._enrich_witb_items_with_urls(favorite.player.witb_items)

            return schemas.UserFavoritesResponse(
                favorites=[
                    schemas.FavoritePlayerResponse.model_validate(fav)
                    for fav in favorites
                ],
                total=len(favorites),
            )
        except Exception as e:
            raise DatabaseOperationError("get_user_favorites", str(e))
