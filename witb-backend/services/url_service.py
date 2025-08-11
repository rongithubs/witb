"""URL generation service for PGA Club Tracker following CLAUDE.md C-4."""

import re
from typing import Optional

# Manual mappings for players whose database names don't match PGA Club Tracker URLs
NAME_MAPPINGS = {
    "Matt Fitzpatrick": "Matthew Fitzpatrick",
    "Ludvig Åberg": "Ludwig Aberg",  # Ludvig -> Ludwig, remove accent from å
    # Add more mappings as needed
}


def generate_pga_tracker_url(
    first_name: Optional[str], last_name: Optional[str]
) -> str:
    """
    Generate PGA Club Tracker WITB URL from player names.

    Args:
        first_name: Player's first name (e.g., "Scottie", "J.J")
        last_name: Player's last name (e.g., "Scheffler", "Spaun")

    Returns:
        Complete URL for player's WITB page

    Raises:
        ValueError: If first_name or last_name is empty or None

    Examples:
        >>> generate_pga_tracker_url("Scottie", "Scheffler")
        "https://www.pgaclubtracker.com/players/scottie-scheffler-witb-whats-in-the-bag"

        >>> generate_pga_tracker_url("J.J", "Spaun")
        "https://www.pgaclubtracker.com/players/j-j-spaun-witb-whats-in-the-bag"
    """
    if not first_name or not last_name:
        raise ValueError("First name and last name cannot be empty")

    # Check for manual name mappings
    full_name = f"{first_name} {last_name}"
    if full_name in NAME_MAPPINGS:
        full_name = NAME_MAPPINGS[full_name]

    # Replace dots with hyphens (J.J -> J-J)
    slug = full_name.replace(".", "-")

    # Remove apostrophes (O'Malley -> OMalley)
    slug = slug.replace("'", "")

    # Replace spaces and special characters with hyphens
    slug = re.sub(
        r"[^\w\s-]", "", slug
    )  # Remove non-alphanumeric except spaces/hyphens
    slug = re.sub(r"\s+", "-", slug)  # Replace spaces with hyphens
    slug = re.sub(r"-+", "-", slug)  # Replace multiple hyphens with single hyphen
    slug = slug.lower().strip("-")  # Lowercase and remove trailing hyphens

    base_url = "https://www.pgaclubtracker.com/players"
    return f"{base_url}/{slug}-witb-whats-in-the-bag"
