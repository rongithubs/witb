"""Unit tests for the OWGR top 50 scraper following CLAUDE.md T-1."""

import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "scraper"))

from scrape_ogwr_gemini import _clean_name, _clean_rank, _extract_country

# OWGR renders names in caps, so the scraper re-cases them. Intercapital
# surnames are the cases plain title-casing gets wrong, and a mis-cased name
# reads as a different player when rankings are synced by name.
INTERCAPITAL_NAMES = [
    ("RORY MCILROY", "Rory McIlroy"),
    ("ROBERT MACINTYRE", "Robert MacIntyre"),
    ("MAVERICK MCNEALY", "Maverick McNealy"),
    ("MATT MCCARTY", "Matt McCarty"),
    ("BRYSON DECHAMBEAU", "Bryson DeChambeau"),
]

ACCENTED_NAMES = [
    ("LUDVIG ABERG", "Ludvig Åberg"),
    ("NICOLAI HOJGAARD", "Nicolai Højgaard"),
    ("SAMI VALIMAKI", "Sami Välimäki"),
]

PLAIN_NAMES = [
    ("SCOTTIE SCHEFFLER", "Scottie Scheffler"),
    ("  TOMMY FLEETWOOD  ", "Tommy Fleetwood"),
    ("J.J. SPAUN", "J.J. Spaun"),
    ("SI WOO KIM", "Si Woo Kim"),
]


class TestCleanName:
    """Test re-casing of scraped OWGR player names."""

    @pytest.mark.parametrize("raw,expected", INTERCAPITAL_NAMES)
    def test_preserves_intercapital_surnames(self, raw: str, expected: str):
        assert _clean_name(raw) == expected

    @pytest.mark.parametrize("raw,expected", ACCENTED_NAMES)
    def test_restores_accented_characters(self, raw: str, expected: str):
        assert _clean_name(raw) == expected

    @pytest.mark.parametrize("raw,expected", PLAIN_NAMES)
    def test_title_cases_and_trims_plain_names(self, raw: str, expected: str):
        assert _clean_name(raw) == expected

    @pytest.mark.parametrize(
        "raw,expected", INTERCAPITAL_NAMES + ACCENTED_NAMES + PLAIN_NAMES
    )
    def test_is_idempotent(self, raw: str, expected: str):
        """Re-cleaning an already-clean name must not corrupt it."""
        assert _clean_name(_clean_name(raw)) == expected

    def test_returns_empty_for_blank_input(self):
        assert _clean_name("   ") == ""


class TestCleanRank:
    """Test rank parsing from OWGR rank cells."""

    @pytest.mark.parametrize(
        "raw,expected",
        [("1", 1), ("50", 50), ("12 (13)", 12), ("  7  ", 7)],
    )
    def test_extracts_leading_rank_number(self, raw: str, expected: int):
        assert _clean_rank(raw) == expected

    @pytest.mark.parametrize("raw", ["", "-", "N/A"])
    def test_returns_none_when_no_digits(self, raw: str):
        assert _clean_rank(raw) is None


class TestExtractCountry:
    """Test country resolution from OWGR flag image sources."""

    @pytest.mark.parametrize(
        "flag_src,expected",
        [
            ("/flags/us.svg", "USA"),
            ("https://cdn.owgr.com/flags/gb-nir.svg", "Northern Ireland"),
            ("/flags/kr.svg", "South Korea"),
            ("/flags/zz.svg", "Unknown"),
            ("", "Unknown"),
            ("/flags/us.png", "Unknown"),
        ],
    )
    def test_maps_flag_code_to_country(self, flag_src: str, expected: str):
        assert _extract_country(flag_src) == expected
