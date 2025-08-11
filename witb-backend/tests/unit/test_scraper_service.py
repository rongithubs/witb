"""Unit tests for HTML scraper service following CLAUDE.md T-1."""

from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import pytest

from services.scraper_service import PGAClubTrackerScraper, WITBData, EquipmentItem


class TestPGAClubTrackerScraper:
    """Unit tests for PGA Club Tracker scraper service."""

    def test_parse_last_updated_from_html(self):
        """Test extracting last updated date from HTML."""
        scraper = PGAClubTrackerScraper()
        sample_html = """
        <div class="content">
            <h1>What's in Scottie Scheffler's bag?</h1>
            <p>Last updated: May 18, 2025</p>
            <table>...</table>
        </div>
        """

        result = scraper._parse_last_updated(sample_html)
        expected = datetime(2025, 5, 18)
        assert result == expected

    def test_parse_equipment_table_from_html(self):
        """Test extracting equipment data from HTML table."""
        scraper = PGAClubTrackerScraper()
        sample_html = """
        <table>
            <thead>
                <tr><th>Club</th><th>Brand</th><th>Model</th><th>Loft/No.</th><th>Shaft</th></tr>
            </thead>
            <tbody>
                <tr>
                    <td>Driver</td>
                    <td>TaylorMade</td>
                    <td>Stealth 2</td>
                    <td>9°</td>
                    <td>Fujikura Ventus Blue</td>
                </tr>
                <tr>
                    <td>Putter</td>
                    <td>Scotty Cameron</td>
                    <td>Newport 2</td>
                    <td></td>
                    <td></td>
                </tr>
            </tbody>
        </table>
        """

        result = scraper._parse_equipment_table(sample_html)

        assert len(result) == 2

        # First item - Driver
        assert result[0].category == "Driver"
        assert result[0].brand == "TaylorMade"
        assert result[0].model == "Stealth 2"
        assert result[0].loft == "9°"
        assert result[0].shaft == "Fujikura Ventus Blue"

        # Second item - Putter with empty fields
        assert result[1].category == "Putter"
        assert result[1].brand == "Scotty Cameron"
        assert result[1].model == "Newport 2"
        assert result[1].loft is None
        assert result[1].shaft is None

    def test_parse_last_updated_various_formats(self):
        """Test parsing different date formats from HTML."""
        scraper = PGAClubTrackerScraper()

        test_cases = [
            ("May 18, 2025", datetime(2025, 5, 18)),
            ("January 1, 2024", datetime(2024, 1, 1)),
            ("Dec 25, 2023", datetime(2023, 12, 25)),
        ]

        for date_text, expected in test_cases:
            html = f"<p>Last updated: {date_text}</p>"
            result = scraper._parse_last_updated(html)
            assert result == expected, f"Failed for date: {date_text}"

    def test_parse_last_updated_no_date_returns_none(self):
        """Test that missing date returns None."""
        scraper = PGAClubTrackerScraper()
        html = "<p>Some content without date</p>"

        result = scraper._parse_last_updated(html)
        assert result is None

    def test_clean_text_removes_whitespace_and_empties(self):
        """Test that _clean_text helper function works properly."""
        scraper = PGAClubTrackerScraper()

        test_cases = [
            ("  TaylorMade  ", "TaylorMade"),
            ("", None),
            ("   ", None),
            ("Valid Text", "Valid Text"),
            ("Text\nwith\nnewlines", "Text with newlines"),
        ]

        for input_text, expected in test_cases:
            result = scraper._clean_text(input_text)
            assert result == expected, f"Failed for input: '{input_text}'"

    @pytest.mark.asyncio
    async def test_scrape_player_witb_integration(self):
        """Test full scraping workflow with mocked HTTP response."""
        scraper = PGAClubTrackerScraper()
        test_url = "https://www.pgaclubtracker.com/players/test-player-witb"

        mock_html = """
        <div>
            <h1>What's in Test Player's bag?</h1>
            <p>Last updated: May 18, 2025</p>
            <table>
                <thead>
                    <tr><th>Club</th><th>Brand</th><th>Model</th><th>Loft/No.</th><th>Shaft</th></tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Driver</td>
                        <td>TaylorMade</td>
                        <td>Stealth 2</td>
                        <td>9°</td>
                        <td>Fujikura Ventus Blue</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = Mock()
            mock_response.text = AsyncMock(return_value=mock_html)
            mock_response.status = 200
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await scraper.scrape_player_witb(test_url)

            assert isinstance(result, WITBData)
            assert result.last_updated == datetime(2025, 5, 18)
            assert len(result.equipment) == 1
            assert result.equipment[0].category == "Driver"
            assert result.source_url == test_url
