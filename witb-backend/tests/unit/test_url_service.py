"""Unit tests for URL generation service following CLAUDE.md T-1."""

import pytest

from services.url_service import generate_pga_tracker_url


class TestGeneratePGATrackerURL:
    """Unit tests for PGA Club Tracker URL generation."""

    def test_simple_name_url_generation(self):
        """Test URL generation for simple first and last names."""
        result = generate_pga_tracker_url("Scottie", "Scheffler")
        expected = "https://www.pgaclubtracker.com/players/scottie-scheffler-witb-whats-in-the-bag"
        assert result == expected

    def test_name_with_dots_url_generation(self):
        """Test URL generation for names with dots like 'J.J Spaun'."""
        result = generate_pga_tracker_url("J.J", "Spaun")
        expected = (
            "https://www.pgaclubtracker.com/players/j-j-spaun-witb-whats-in-the-bag"
        )
        assert result == expected

    def test_name_with_apostrophe_url_generation(self):
        """Test URL generation for names with apostrophes."""
        result = generate_pga_tracker_url("Brian", "O'Malley")
        expected = (
            "https://www.pgaclubtracker.com/players/brian-omalley-witb-whats-in-the-bag"
        )
        assert result == expected

    def test_name_with_spaces_url_generation(self):
        """Test URL generation for names with multiple words."""
        result = generate_pga_tracker_url("Tiger", "Woods Jr")
        expected = "https://www.pgaclubtracker.com/players/tiger-woods-jr-witb-whats-in-the-bag"
        assert result == expected

    def test_name_with_numbers_url_generation(self):
        """Test URL generation for names with numbers."""
        result = generate_pga_tracker_url("John", "Daly II")
        expected = (
            "https://www.pgaclubtracker.com/players/john-daly-ii-witb-whats-in-the-bag"
        )
        assert result == expected

    def test_empty_name_raises_error(self):
        """Test that empty names raise appropriate error."""
        with pytest.raises(
            ValueError, match="First name and last name cannot be empty"
        ):
            generate_pga_tracker_url("", "Smith")

        with pytest.raises(
            ValueError, match="First name and last name cannot be empty"
        ):
            generate_pga_tracker_url("John", "")

    def test_none_name_raises_error(self):
        """Test that None names raise appropriate error."""
        with pytest.raises(
            ValueError, match="First name and last name cannot be empty"
        ):
            generate_pga_tracker_url(None, "Smith")

        with pytest.raises(
            ValueError, match="First name and last name cannot be empty"
        ):
            generate_pga_tracker_url("John", None)
