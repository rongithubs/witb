"""Unit tests for OWGR player sync helpers following CLAUDE.md T-1 and T-3."""

import pytest

from populate_ogwr_players import normalize_player_name

# The sync matches DB rows against scraped names. Any name the scraper re-cases
# differently from what is already stored would otherwise look like a brand new
# player *and* make the stored row look like it dropped out of the top 50 --
# which deletes that player's WITB items. Normalising both sides prevents it.
CASE_VARIANTS = [
    ("Bryson Dechambeau", "Bryson DeChambeau"),
    ("rory mcilroy", "Rory McIlroy"),
    ("SCOTTIE SCHEFFLER", "Scottie Scheffler"),
]


class TestNormalizePlayerName:
    """Test the key used to match scraped players against stored players."""

    @pytest.mark.parametrize("stored,scraped", CASE_VARIANTS)
    def test_case_variants_share_a_key(self, stored: str, scraped: str):
        assert normalize_player_name(stored) == normalize_player_name(scraped)

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("  Jon Rahm  ", "jon rahm"),
            ("Min  Woo   Lee", "min woo lee"),
            ("J.T. Poston", "j.t. poston"),
        ],
    )
    def test_collapses_whitespace_and_lowercases(self, raw: str, expected: str):
        assert normalize_player_name(raw) == expected

    def test_accents_are_significant(self):
        """Åberg and Aberg are different keys - never silently merge players."""
        assert normalize_player_name("Ludvig Åberg") != normalize_player_name(
            "Ludvig Aberg"
        )

    @pytest.mark.parametrize("raw", ["Tommy Fleetwood", "tommy fleetwood"])
    def test_is_idempotent(self, raw: str):
        once = normalize_player_name(raw)
        assert normalize_player_name(once) == once

    def test_distinct_players_keep_distinct_keys(self):
        assert normalize_player_name("Tom Kim") != normalize_player_name("Si Woo Kim")
