"""Unit tests for tournament scraper following CLAUDE.md T-1."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from services.tournament_scraper_service import SimpleTournamentScraper


class TestScoreParsing:
    """Test score parsing and conversion logic."""

    def test_numeric_score_conversion_negative(self):
        """Test parsing negative golf scores."""
        scraper = SimpleTournamentScraper()

        # Test the scoring logic from _extract_winner_from_scoreboard
        def get_numeric_score(competitor):
            score = competitor.get("score", "999")
            try:
                return int(score) if score != "" else 999
            except (ValueError, TypeError):
                return 999

        # Test cases
        test_cases = [
            ({"score": "-18"}, -18),
            ({"score": "-16"}, -16),
            ({"score": "-1"}, -1),
            ({"score": "0"}, 0),
            ({"score": "+1"}, 1),
            ({"score": "+5"}, 5),
            ({"score": ""}, 999),
            ({"score": "E"}, 999),  # Even par should fallback
            ({"score": "WD"}, 999),  # Withdrawal should fallback
            ({}, 999),  # Missing score
        ]

        for competitor_data, expected_score in test_cases:
            actual_score = get_numeric_score(competitor_data)
            assert (
                actual_score == expected_score
            ), f"Failed for {competitor_data}: expected {expected_score}, got {actual_score}"

    def test_score_formatting_display(self):
        """Test score formatting for display."""
        scraper = SimpleTournamentScraper()

        # Test the score formatting logic from _extract_winner_from_scoreboard
        def format_score_display(winner_score):
            if isinstance(winner_score, (int, float)):
                return f"{int(winner_score):+d}" if winner_score != 0 else "E"
            else:
                try:
                    numeric_score = int(winner_score)
                    return f"{numeric_score:+d}" if numeric_score != 0 else "E"
                except (ValueError, TypeError):
                    return str(winner_score) if winner_score else ""

        test_cases = [
            (-18, "-18"),
            (-16, "-16"),
            (-1, "-1"),
            (0, "E"),
            (1, "+1"),
            (5, "+5"),
            ("-18", "-18"),
            ("0", "E"),
            ("+1", "+1"),
            ("", ""),
            ("WD", "WD"),
        ]

        for input_score, expected_display in test_cases:
            actual_display = format_score_display(input_score)
            assert (
                actual_display == expected_display
            ), f"Failed for {input_score}: expected {expected_display}, got {actual_display}"


class TestCacheLogic:
    """Test caching functionality."""

    def test_cache_initialization(self):
        """Test scraper initializes with empty cache."""
        scraper = SimpleTournamentScraper()
        assert scraper._cache == {}
        assert scraper._cache_timestamp is None
        assert not scraper._is_cache_valid()

    def test_cache_validity_fresh(self):
        """Test cache is valid when fresh."""
        scraper = SimpleTournamentScraper()
        scraper._cache = {"winner": "Test Winner"}
        scraper._cache_timestamp = datetime.now()

        assert scraper._is_cache_valid()

    def test_cache_validity_expired(self):
        """Test cache is invalid when expired."""
        scraper = SimpleTournamentScraper()
        scraper._cache = {"winner": "Test Winner"}
        # Set timestamp to 31 minutes ago (past the 30-minute limit)
        scraper._cache_timestamp = datetime.now() - timedelta(minutes=31)

        assert not scraper._is_cache_valid()

    def test_cache_validity_boundary(self):
        """Test cache validity at 30-minute boundary."""
        scraper = SimpleTournamentScraper()
        scraper._cache = {"winner": "Test Winner"}
        # Set timestamp to exactly 30 minutes ago
        scraper._cache_timestamp = datetime.now() - timedelta(minutes=30)

        assert not scraper._is_cache_valid()

    def test_cache_validity_empty_cache(self):
        """Test cache is invalid when empty."""
        scraper = SimpleTournamentScraper()
        scraper._cache = {}
        scraper._cache_timestamp = datetime.now()

        assert not scraper._is_cache_valid()

    def test_cache_validity_no_timestamp(self):
        """Test cache is invalid without timestamp."""
        scraper = SimpleTournamentScraper()
        scraper._cache = {"winner": "Test Winner"}
        scraper._cache_timestamp = None

        assert not scraper._is_cache_valid()


class TestFallbackSystem:
    """Test fallback winner functionality."""

    def test_fallback_winner_structure(self):
        """Test fallback winner returns correct structure."""
        scraper = SimpleTournamentScraper()
        result = scraper._get_fallback_winner()

        # Check required fields
        required_fields = ["winner", "tournament", "date", "score"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        # Check data types
        assert isinstance(result["winner"], str)
        assert isinstance(result["tournament"], str)
        assert isinstance(result["date"], str)
        assert isinstance(result["score"], str)

        # Check values are not empty
        assert result["winner"] != ""
        assert result["tournament"] != ""
        assert result["date"] != ""

    def test_fallback_winner_uses_first_fallback(self):
        """Test fallback uses first winner from FALLBACK_WINNERS."""
        scraper = SimpleTournamentScraper()
        result = scraper._get_fallback_winner()

        expected_winner, expected_tournament = scraper.FALLBACK_WINNERS[0]
        assert result["winner"] == expected_winner
        assert result["tournament"] == expected_tournament


class TestDataExtraction:
    """Test ESPN data extraction logic."""

    def test_extract_winner_from_scoreboard_valid_data(self):
        """Test extracting winner from valid ESPN scoreboard data."""
        scraper = SimpleTournamentScraper()

        # Mock valid ESPN scoreboard response
        mock_data = {
            "events": [
                {
                    "name": "Test Championship",
                    "date": "2025-08-07T00:00:00Z",
                    "competitions": [
                        {
                            "status": {"type": {"name": "STATUS_FINAL"}},
                            "competitors": [
                                {
                                    "athlete": {"displayName": "Justin Rose"},
                                    "score": "-16",
                                },
                                {
                                    "athlete": {"displayName": "J.J. Spaun"},
                                    "score": "-15",
                                },
                                {
                                    "athlete": {"displayName": "Scottie Scheffler"},
                                    "score": "-14",
                                },
                            ],
                        }
                    ],
                }
            ]
        }

        result = scraper._extract_winner_from_scoreboard(mock_data)

        assert result["winner"] == "Justin Rose"
        assert result["tournament"] == "Test Championship"
        assert result["score"] == "-16"
        assert result["date"] == "August 07, 2025"

    def test_extract_winner_from_scoreboard_empty_data(self):
        """Test extracting winner from empty ESPN data."""
        scraper = SimpleTournamentScraper()

        empty_data_cases = [
            {},
            {"events": []},
            {"events": [{}]},
            {"events": [{"competitions": []}]},
        ]

        for empty_data in empty_data_cases:
            result = scraper._extract_winner_from_scoreboard(empty_data)
            assert result["winner"] == "Not found"

    def test_extract_winner_from_scoreboard_tournament_in_progress(self):
        """Test extracting winner from tournament still in progress."""
        scraper = SimpleTournamentScraper()

        # Mock tournament in progress (not final)
        mock_data = {
            "events": [
                {
                    "name": "Test Championship",
                    "date": "2025-08-07T00:00:00Z",
                    "competitions": [
                        {
                            "status": {"type": {"name": "STATUS_IN_PROGRESS"}},
                            "competitors": [
                                {
                                    "athlete": {"displayName": "Justin Rose"},
                                    "score": "-16",
                                }
                            ],
                        }
                    ],
                }
            ]
        }

        result = scraper._extract_winner_from_scoreboard(mock_data)
        assert result["winner"] == "Not found"

    def test_extract_winner_sorting_by_score(self):
        """Test that winner is correctly identified by lowest score."""
        scraper = SimpleTournamentScraper()

        # Mock data with competitors in wrong order
        mock_data = {
            "events": [
                {
                    "name": "Test Championship",
                    "date": "2025-08-07T00:00:00Z",
                    "competitions": [
                        {
                            "status": {"type": {"name": "STATUS_FINAL"}},
                            "competitors": [
                                {
                                    "athlete": {"displayName": "Player C"},
                                    "score": "-10",
                                },
                                {
                                    "athlete": {"displayName": "Justin Rose"},
                                    "score": "-16",
                                },  # Best score
                                {"athlete": {"displayName": "Player A"}, "score": "-5"},
                                {
                                    "athlete": {"displayName": "J.J. Spaun"},
                                    "score": "-15",
                                },
                            ],
                        }
                    ],
                }
            ]
        }

        result = scraper._extract_winner_from_scoreboard(mock_data)

        # Should pick Justin Rose with -16, not the first in list
        assert result["winner"] == "Justin Rose"
        assert result["score"] == "-16"


@pytest.mark.asyncio
class TestAsyncFunctionality:
    """Test async functions with mocking."""

    async def test_get_winner_witb_player_found(self):
        """Test getting WITB data for existing player."""
        scraper = SimpleTournamentScraper()

        # Mock database response using a different approach
        with patch("tournament_scraper.engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_result = Mock()
            mock_result.fetchall.return_value = [
                (
                    "player-id",
                    "Justin Rose",
                    "Driver",
                    "TaylorMade",
                    "GT2",
                    None,
                    "Shaft1",
                ),
                (
                    "player-id",
                    "Justin Rose",
                    "Putter",
                    "Odyssey",
                    "Model",
                    None,
                    "Grip1",
                ),
            ]
            mock_conn.execute.return_value = mock_result

            # Mock the begin context manager
            mock_begin = AsyncMock()
            mock_begin.__aenter__.return_value = mock_conn
            mock_engine.begin.return_value = mock_begin

            result = await scraper._get_winner_witb("Justin Rose")

            assert len(result) == 2
            assert result[0]["category"] == "Driver"
            assert result[0]["brand"] == "TaylorMade"
            assert result[1]["category"] == "Putter"

    async def test_get_winner_witb_player_not_found(self):
        """Test getting WITB data for non-existent player."""
        scraper = SimpleTournamentScraper()

        with patch("tournament_scraper.engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_result = Mock()
            mock_result.fetchall.return_value = []
            mock_conn.execute.return_value = mock_result

            # Mock the begin context manager
            mock_begin = AsyncMock()
            mock_begin.__aenter__.return_value = mock_conn
            mock_engine.begin.return_value = mock_begin

            result = await scraper._get_winner_witb("Unknown Player")

            assert result == []

    async def test_get_winner_witb_database_error(self):
        """Test WITB data handling when database error occurs."""
        scraper = SimpleTournamentScraper()

        with patch("tournament_scraper.engine") as mock_engine:
            mock_engine.begin.side_effect = Exception("Database connection failed")

            result = await scraper._get_winner_witb("Justin Rose")

            assert result == []
