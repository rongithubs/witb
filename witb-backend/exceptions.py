"""Custom exceptions following CLAUDE.md FA-4."""

from fastapi import HTTPException, status


class PlayerNotFoundError(HTTPException):
    """Exception raised when player is not found."""

    def __init__(self, player_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found",
        )


class InvalidPlayerIdError(HTTPException):
    """Exception raised when player ID format is invalid."""

    def __init__(self, player_id: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid player ID format: {player_id}",
        )


class PlayerAlreadyExistsError(HTTPException):
    """Exception raised when trying to create a player that already exists."""

    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Player '{name}' already exists",
        )


class DatabaseOperationError(HTTPException):
    """Exception raised when database operation fails."""

    def __init__(self, operation: str, details: str = ""):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database operation '{operation}' failed: {details}",
        )
