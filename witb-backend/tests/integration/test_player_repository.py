"""Integration tests for PlayerRepository.get_top_ranked_players (CLAUDE.md T-2, T-3)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import models
from repositories.player_repository import PlayerRepository


class TestGetTopRankedPlayers:
    """DB-touching tests for tour filtering and ranking order."""

    @pytest.mark.asyncio
    async def test_tour_filter_returns_only_matching_tour_in_rank_order(
        self, db_session: AsyncSession
    ):
        """With a tour filter, only that tour's players are returned, by rank."""
        db_session.add_all(
            [
                models.Player(name="PGA Two", tour="OGWR", ranking=2),
                models.Player(name="LPGA One", tour="LPGA", ranking=1),
                models.Player(name="PGA One", tour="OGWR", ranking=1),
            ]
        )
        await db_session.commit()
        repo = PlayerRepository(db_session)

        result = await repo.get_top_ranked_players(limit=10, tour="OGWR")

        assert [p.name for p in result] == ["PGA One", "PGA Two"]

    @pytest.mark.asyncio
    async def test_without_tour_filter_returns_all_tours_by_rank(
        self, db_session: AsyncSession
    ):
        """Without a filter, players from every tour are returned, by rank."""
        db_session.add_all(
            [
                models.Player(name="LPGA One", tour="LPGA", ranking=1),
                models.Player(name="PGA Two", tour="OGWR", ranking=2),
            ]
        )
        await db_session.commit()
        repo = PlayerRepository(db_session)

        result = await repo.get_top_ranked_players(limit=10)

        assert [p.name for p in result] == ["LPGA One", "PGA Two"]
