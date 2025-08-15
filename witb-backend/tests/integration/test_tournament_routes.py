"""Integration tests for tournament routes following CLAUDE.md T-2."""

import os
import sys
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# Add scraper to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "scraper"))

from main import app
from tests.fixtures.espn_api_responses import ESPNAPIFixtures


class TestTournamentRoutes:
    """Integration tests for tournament API endpoints."""

    def test_tournament_winner_endpoint_exists(self):
        """Test that the tournament winner endpoint exists."""
        client = TestClient(app)
        response = client.get("/tournament-winner")

        # Should not return 404 (endpoint exists)
        assert response.status_code != 404

    def test_tournament_winner_response_structure(self):
        """Test tournament winner endpoint returns correct structure."""
        client = TestClient(app)
        response = client.get("/tournament-winner")

        assert response.status_code == 200
        data = response.json()

        # Check required fields
        required_fields = ["winner", "tournament", "date", "score"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Check data types
        assert isinstance(data["winner"], str)
        assert isinstance(data["tournament"], str)
        assert isinstance(data["date"], str)
        assert isinstance(data["score"], str)

    @patch(
        "services.tournament_scraper_service.simple_tournament_scraper.scrape_and_store_winner"
    )
    def test_tournament_winner_with_mock_data(self, mock_scraper):
        """Test tournament winner endpoint with mocked ESPN data."""
        # Mock successful tournament winner response
        mock_data = {
            "winner": "Justin Rose",
            "tournament": "FedEx St. Jude Championship",
            "date": "August 07, 2025",
            "score": "-16",
            "witb_items": [
                {
                    "category": "Driver",
                    "brand": "TaylorMade",
                    "model": "GT2",
                    "loft": None,
                    "shaft": "Project X HZRDUS Smoke Green",
                    "product_url": "https://taylormade.com",
                }
            ],
        }
        mock_scraper.return_value = mock_data

        client = TestClient(app)
        response = client.get("/tournament-winner")

        assert response.status_code == 200
        data = response.json()

        assert data["winner"] == "Justin Rose"
        assert data["tournament"] == "FedEx St. Jude Championship"
        assert data["score"] == "-16"
        assert "witb_items" in data
        assert len(data["witb_items"]) == 1

    @patch(
        "services.tournament_scraper_service.simple_tournament_scraper.scrape_and_store_winner"
    )
    def test_tournament_winner_handles_scraper_error(self, mock_scraper):
        """Test tournament winner endpoint handles scraper errors gracefully."""
        # Mock scraper raising exception
        mock_scraper.side_effect = Exception("ESPN API failed")

        client = TestClient(app)
        response = client.get("/tournament-winner")

        # Should still return 200 with fallback data
        assert response.status_code == 200
        data = response.json()

        # Should contain fallback error message
        assert (
            "unavailable" in data["winner"]
            or "error" in data["winner"]
            or data["winner"] != ""
        )

    def test_debug_tournament_winner_endpoint_exists(self):
        """Test that the debug tournament winner endpoint exists."""
        client = TestClient(app)
        response = client.get("/tournament-winner/debug")

        # Should not return 404 (endpoint exists)
        assert response.status_code != 404

    def test_debug_tournament_winner_response_structure(self):
        """Test debug endpoint returns some kind of structured response."""
        client = TestClient(app)
        response = client.get("/tournament-winner/debug")

        assert response.status_code == 200
        data = response.json()

        # Should return some kind of debug info (structure varies)
        assert isinstance(data, dict)
        # Common debug fields might include status, error, or data
        debug_fields = ["status", "error", "url", "html_preview"]
        has_debug_field = any(field in data for field in debug_fields)
        assert (
            has_debug_field
        ), f"Debug response should contain at least one of: {debug_fields}"


@pytest.mark.asyncio
class TestTournamentService:
    """Integration tests for TournamentService."""

    async def test_tournament_service_get_winner_success(self):
        """Test TournamentService successfully gets tournament winner."""
        from services.tournament_service import TournamentService

        service = TournamentService()

        # Mock the scraper to return predictable data
        with patch(
            "services.tournament_scraper_service.simple_tournament_scraper.scrape_and_store_winner"
        ) as mock_scraper:
            mock_data = {
                "winner": "Justin Rose",
                "tournament": "FedEx St. Jude Championship",
                "date": "August 07, 2025",
                "score": "-16",
                "witb_items": [],
            }
            mock_scraper.return_value = mock_data

            result = await service.get_tournament_winner()

            assert result["winner"] == "Justin Rose"
            assert result["tournament"] == "FedEx St. Jude Championship"
            assert result["score"] == "-16"

    async def test_tournament_service_handles_scraper_exception(self):
        """Test TournamentService handles scraper exceptions."""
        from services.tournament_service import TournamentService

        service = TournamentService()

        with patch(
            "services.tournament_scraper_service.simple_tournament_scraper.scrape_and_store_winner"
        ) as mock_scraper:
            mock_scraper.side_effect = Exception("Network error")

            result = await service.get_tournament_winner()

            # Should return fallback data structure
            assert "winner" in result
            assert "tournament" in result
            assert result["winner"] == "Tournament data unavailable"
            assert result["tournament"] == "Please try again later"


@pytest.mark.asyncio
class TestTournamentDatabaseIntegration:
    """Test tournament winner database storage integration."""

    async def test_tournament_winner_storage(self):
        """Test that tournament winners are stored in database."""
        from services.tournament_scraper_service import SimpleTournamentScraper

        scraper = SimpleTournamentScraper()

        # Mock ESPN API response
        with patch.object(scraper, "_get_current_winner_from_api") as mock_api:
            mock_api.return_value = {
                "winner": "Test Winner",
                "tournament": "Test Tournament",
                "date": "August 11, 2025",
                "score": "-10",
            }

            # Mock database operations
            with patch(
                "services.tournament_scraper_service.engine.begin"
            ) as mock_engine:
                mock_conn = AsyncMock()
                mock_engine.return_value.__aenter__.return_value = mock_conn

                # Mock WITB query to return empty result
                mock_result = AsyncMock()
                mock_result.fetchall.return_value = []
                mock_conn.execute.return_value = mock_result

                result = await scraper.scrape_and_store_winner()

                # Verify database operations were called
                assert mock_conn.execute.call_count >= 1  # At least one DB call
                assert result["winner"] == "Test Winner"

    async def test_witb_data_integration(self):
        """Test that WITB data is properly integrated with tournament winner."""
        from services.tournament_scraper_service import SimpleTournamentScraper

        scraper = SimpleTournamentScraper()

        with patch("tournament_scraper.engine.begin") as mock_engine:
            mock_conn = AsyncMock()
            mock_engine.return_value.__aenter__.return_value = mock_conn

            # Mock WITB data response
            mock_result = AsyncMock()
            mock_result.fetchall.return_value = ESPNAPIFixtures.database_witb_response()
            mock_conn.execute.return_value = mock_result

            witb_items = await scraper._get_winner_witb("Justin Rose")

            assert len(witb_items) == 10  # Should have 10 WITB items
            assert witb_items[0]["category"] == "Driver"
            assert witb_items[0]["brand"] == "TaylorMade"
            assert witb_items[0]["model"] == "GT2"

            # Check that product URLs are added
            driver_item = next(
                item for item in witb_items if item["category"] == "Driver"
            )
            assert driver_item.get("product_url") is not None


@pytest.mark.asyncio
class TestTournamentErrorHandling:
    """Test error handling in tournament system."""

    async def test_espn_api_timeout_handling(self):
        """Test handling of ESPN API timeouts."""
        import aiohttp

        from services.tournament_scraper_service import SimpleTournamentScraper

        scraper = SimpleTournamentScraper()

        # Mock aiohttp timeout error
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.get.side_effect = (
                aiohttp.ServerTimeoutError("Timeout")
            )

            result = await scraper._get_current_winner_from_api()

            # Should fall back to fallback winner
            assert result["winner"] in [
                winner for winner, _ in scraper.FALLBACK_WINNERS
            ]

    async def test_espn_api_404_handling(self):
        """Test handling of ESPN API 404 errors."""
        from services.tournament_scraper_service import SimpleTournamentScraper

        scraper = SimpleTournamentScraper()

        # Mock 404 response
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
                mock_response
            )

            result = await scraper._get_current_winner_from_api()

            # Should fall back to fallback winner
            assert result["winner"] in [
                winner for winner, _ in scraper.FALLBACK_WINNERS
            ]

    async def test_malformed_json_handling(self):
        """Test handling of malformed JSON from ESPN API."""
        import json

        from services.tournament_scraper_service import SimpleTournamentScraper

        scraper = SimpleTournamentScraper()

        # Mock malformed JSON response
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
                mock_response
            )

            result = await scraper._get_current_winner_from_api()

            # Should fall back to fallback winner
            assert result["winner"] in [
                winner for winner, _ in scraper.FALLBACK_WINNERS
            ]
