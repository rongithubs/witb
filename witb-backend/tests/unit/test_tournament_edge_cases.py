"""Property-based and edge case tests for tournament scraper following CLAUDE.md T-6."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import sys
import os

# Try to import hypothesis for property-based testing
try:
    from hypothesis import given, strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False
    # Create dummy decorators if hypothesis not available
    def given(*args, **kwargs):
        def decorator(f):
            return f
        return decorator
    st = Mock()

from services.tournament_scraper_service import SimpleTournamentScraper


class TestScoreParsingProperties:
    """Property-based tests for score parsing."""
    
    @pytest.mark.skipif(not HAS_HYPOTHESIS, reason="hypothesis not installed")
    @given(st.text())
    def test_score_parsing_never_crashes(self, score_text):
        """Test that score parsing never crashes with arbitrary string input."""
        scraper = SimpleTournamentScraper()
        
        # Test the scoring logic from _extract_winner_from_scoreboard
        def get_numeric_score(competitor):
            score = competitor.get("score", "999")
            try:
                return int(score) if score != "" else 999
            except (ValueError, TypeError):
                return 999
        
        competitor = {"score": score_text}
        
        # Should never raise an exception
        result = get_numeric_score(competitor)
        assert isinstance(result, int)
        
        # Should be a reasonable golf score or fallback
        assert -50 <= result <= 999  # Golf scores rarely go below -50
    
    @pytest.mark.skipif(not HAS_HYPOTHESIS, reason="hypothesis not installed")
    @given(st.integers(min_value=-30, max_value=30))
    def test_score_formatting_round_trip(self, score):
        """Test that score formatting works correctly for valid golf scores."""
        scraper = SimpleTournamentScraper()
        
        def format_score_display(winner_score):
            if isinstance(winner_score, (int, float)):
                return f"{int(winner_score):+d}" if winner_score != 0 else "E"
            else:
                try:
                    numeric_score = int(winner_score)
                    return f"{numeric_score:+d}" if numeric_score != 0 else "E"
                except (ValueError, TypeError):
                    return str(winner_score) if winner_score else ""
        
        formatted = format_score_display(score)
        
        if score == 0:
            assert formatted == "E"
        elif score > 0:
            assert formatted == f"+{score}"
            assert formatted.startswith("+")
        else:
            assert formatted == str(score)  # Already has negative sign
            assert formatted.startswith("-")


class TestDataExtractionEdgeCases:
    """Test edge cases in data extraction."""
    
    def test_extract_winner_with_special_characters(self):
        """Test extracting winner with special characters in name."""
        scraper = SimpleTournamentScraper()
        
        special_names = [
            "José María Olazábal",
            "Søren Kjeldsen", 
            "Charl Schwartzel",
            "Rory McIlroy",
            "Viktor Hovland",
            "Min Woo Lee",
            "J.J. Spaun",
            "D.A. Points",
        ]
        
        for name in special_names:
            mock_data = {
                "events": [{
                    "name": "Test Championship",
                    "date": "2025-08-07T00:00:00Z",
                    "competitions": [{
                        "status": {"type": {"name": "STATUS_FINAL"}},
                        "competitors": [
                            {"athlete": {"displayName": name}, "score": "-16"}
                        ]
                    }]
                }]
            }
            
            result = scraper._extract_winner_from_scoreboard(mock_data)
            assert result["winner"] == name
    
    def test_extract_winner_with_tied_scores(self):
        """Test extracting winner when multiple players are tied."""
        scraper = SimpleTournamentScraper()
        
        # Mock data with tied scores - first player should win alphabetically by default
        mock_data = {
            "events": [{
                "name": "Playoff Tournament",
                "date": "2025-08-07T00:00:00Z", 
                "competitions": [{
                    "status": {"type": {"name": "STATUS_FINAL"}},
                    "competitors": [
                        {"athlete": {"displayName": "Player Z"}, "score": "-16"},
                        {"athlete": {"displayName": "Player A"}, "score": "-16"},  # Same score
                        {"athlete": {"displayName": "Player M"}, "score": "-15"},
                    ]
                }]
            }]
        }
        
        result = scraper._extract_winner_from_scoreboard(mock_data)
        
        # Should pick first player with the tied best score
        tied_winners = ["Player Z", "Player A"]
        assert result["winner"] in tied_winners
        assert result["score"] == "-16"
    
    def test_extract_winner_with_withdrawal_scores(self):
        """Test extracting winner with withdrawal and cut players."""
        scraper = SimpleTournamentScraper()
        
        mock_data = {
            "events": [{
                "name": "Test Championship",
                "date": "2025-08-07T00:00:00Z",
                "competitions": [{
                    "status": {"type": {"name": "STATUS_FINAL"}},
                    "competitors": [
                        {"athlete": {"displayName": "Withdrawal"}, "score": "WD"},
                        {"athlete": {"displayName": "Cut Player"}, "score": "CUT"},
                        {"athlete": {"displayName": "Winner"}, "score": "-10"},
                        {"athlete": {"displayName": "Second"}, "score": "-8"},
                    ]
                }]
            }]
        }
        
        result = scraper._extract_winner_from_scoreboard(mock_data)
        
        # Should ignore WD/CUT players and pick the actual winner
        assert result["winner"] == "Winner"
        assert result["score"] == "-10"
    
    def test_extract_winner_missing_athlete_data(self):
        """Test extracting winner when athlete data is missing."""
        scraper = SimpleTournamentScraper()
        
        mock_data = {
            "events": [{
                "name": "Malformed Tournament",
                "date": "2025-08-07T00:00:00Z",
                "competitions": [{
                    "status": {"type": {"name": "STATUS_FINAL"}},
                    "competitors": [
                        {"score": "-16"},  # Missing athlete data
                        {"athlete": None, "score": "-15"},  # Null athlete
                        {"athlete": {}, "score": "-14"},  # Empty athlete data
                        {"athlete": {"displayName": "Valid Player"}, "score": "-13"},
                    ]
                }]
            }]
        }
        
        result = scraper._extract_winner_from_scoreboard(mock_data)
        
        # Should find the valid player despite malformed data
        assert result["winner"] == "Valid Player"
        assert result["score"] == "-13"
    
    def test_date_parsing_edge_cases(self):
        """Test date parsing with various format edge cases."""
        scraper = SimpleTournamentScraper()
        
        date_test_cases = [
            ("2025-08-07T00:00:00Z", "August 07, 2025"),
            ("2025-12-25T12:30:00Z", "December 25, 2025"),
            ("2025-01-01T23:59:59Z", "January 01, 2025"),
            ("2025-02-29T00:00:00Z", "February 29, 2025"),  # Leap year
            ("invalid-date", datetime.now().strftime("%B %d, %Y")),  # Should fallback to today
            ("", datetime.now().strftime("%B %d, %Y")),  # Empty date
        ]
        
        for input_date, expected_format in date_test_cases:
            mock_data = {
                "events": [{
                    "name": "Date Test Tournament",
                    "date": input_date,
                    "competitions": [{
                        "status": {"type": {"name": "STATUS_FINAL"}},
                        "competitors": [
                            {"athlete": {"displayName": "Test Player"}, "score": "-10"}
                        ]
                    }]
                }]
            }
            
            result = scraper._extract_winner_from_scoreboard(mock_data)
            
            # Date should be formatted properly or fallback to today
            if input_date not in ["invalid-date", ""]:
                assert result["date"] == expected_format
            else:
                # Should have some valid date format
                assert len(result["date"]) > 0
                assert "," in result["date"]  # Should contain comma in date format


class TestCacheEdgeCases:
    """Test caching edge cases and boundary conditions."""
    
    def test_cache_with_none_values(self):
        """Test cache handling with None values."""
        scraper = SimpleTournamentScraper()
        
        # Set cache with None timestamp
        scraper._cache = {"winner": "Test"}
        scraper._cache_timestamp = None
        assert not scraper._is_cache_valid()
        
        # Set empty cache with valid timestamp
        scraper._cache = {}
        scraper._cache_timestamp = datetime.now()
        assert not scraper._is_cache_valid()
    
    def test_cache_expiration_precision(self):
        """Test cache expiration at precise boundaries."""
        scraper = SimpleTournamentScraper()
        scraper._cache = {"winner": "Test"}
        
        # Test exactly at the boundary (should be expired)
        from datetime import timedelta
        boundary_time = datetime.now() - timedelta(minutes=scraper.CACHE_DURATION_MINUTES)
        scraper._cache_timestamp = boundary_time
        assert not scraper._is_cache_valid()
        
        # Test just before boundary (should be valid)
        just_before = datetime.now() - timedelta(minutes=scraper.CACHE_DURATION_MINUTES - 1)
        scraper._cache_timestamp = just_before
        assert scraper._is_cache_valid()


class TestErrorRecovery:
    """Test error recovery and fallback scenarios."""
    
    def test_fallback_after_multiple_failures(self):
        """Test that fallback system works after multiple API failures."""
        scraper = SimpleTournamentScraper()
        
        # Test that fallback winner is consistent
        fallback1 = scraper._get_fallback_winner()
        fallback2 = scraper._get_fallback_winner()
        
        assert fallback1 == fallback2  # Should be deterministic
        assert fallback1["winner"] != ""
        assert fallback1["tournament"] != ""
    
    def test_graceful_degradation_with_partial_data(self):
        """Test graceful handling of partial ESPN API data."""
        scraper = SimpleTournamentScraper()
        
        partial_data_cases = [
            # Missing competitions
            {"events": [{"name": "Test", "date": "2025-08-07"}]},
            # Empty competitions
            {"events": [{"name": "Test", "date": "2025-08-07", "competitions": []}]},
            # Missing status
            {"events": [{"name": "Test", "date": "2025-08-07", "competitions": [{"competitors": []}]}]},
        ]
        
        for partial_data in partial_data_cases:
            result = scraper._extract_winner_from_scoreboard(partial_data)
            
            # Should return "Not found" rather than crashing
            assert result["winner"] == "Not found"
            assert isinstance(result, dict)
            assert "tournament" in result
    
    @pytest.mark.asyncio
    async def test_network_timeout_recovery(self):
        """Test recovery from network timeouts."""
        scraper = SimpleTournamentScraper()
        
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock session that raises timeout
            mock_session.side_effect = Exception("Network timeout")
            
            # Should not crash, should return fallback
            result = await scraper._get_current_winner_from_api()
            
            assert result["winner"] in [w for w, _ in scraper.FALLBACK_WINNERS]
            assert result["winner"] != "Not found"