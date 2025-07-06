"""Tournament routes following CLAUDE.md O-4 (thin route handlers)."""
from fastapi import APIRouter

from services.tournament_service import TournamentService

router = APIRouter(prefix="/tournament-winner", tags=["tournaments"])


@router.get("")
async def get_tournament_winner():
    """Get the latest PGA tournament winner."""
    service = TournamentService()
    return await service.get_tournament_winner()


@router.get("/debug")
async def debug_tournament_winner():
    """Debug endpoint to see raw scraped data."""
    service = TournamentService()
    return await service.debug_tournament_winner()