"""Tournament service for business logic following CLAUDE.md O-4."""

import sys
import os

# Add scraper to path for import
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "scraper"))


class TournamentService:
    """Service for tournament-related business logic."""

    async def get_tournament_winner(self) -> dict:
        """Get the latest PGA tournament winner using scraping."""
        try:
            from tournament_scraper import simple_tournament_scraper

            winner_data = await simple_tournament_scraper.scrape_and_store_winner()
            return winner_data
        except Exception as e:
            print(f"Error fetching tournament winner: {e}")
            return {
                "winner": "Tournament data unavailable",
                "tournament": "Please try again later",
                "date": "",
                "score": "",
            }

    async def debug_tournament_winner(self) -> dict:
        """Debug endpoint to see raw scraped data."""
        try:
            from scrapingbee import ScrapingBeeClient

            # Get API key
            api_key = os.getenv("SCRAPINGBEE_API_KEY", "")
            if not api_key:
                scraper_env_path = os.path.join(
                    os.path.dirname(__file__), "..", "..", "scraper", ".env"
                )
                if os.path.exists(scraper_env_path):
                    with open(scraper_env_path, "r") as f:
                        for line in f:
                            if line.startswith("SCRAPINGBEE_API_KEY="):
                                api_key = line.split("=", 1)[1].strip()
                                break

            if not api_key:
                return {"error": "No API key found"}

            client = ScrapingBeeClient(api_key=api_key)

            # Try ESPN PGA page
            response = client.get(
                "https://www.espn.com/golf/leaderboard",
                params={"render_js": True, "wait": 3000},
            )

            if response.status_code == 200:
                html_snippet = response.content.decode("utf-8")[:2000]
                return {
                    "status": "success",
                    "url": "https://www.espn.com/golf/leaderboard",
                    "status_code": response.status_code,
                    "html_preview": html_snippet,
                }
            else:
                return {
                    "status": "failed",
                    "status_code": response.status_code,
                    "error": "Could not fetch data",
                }

        except Exception as e:
            return {"error": str(e)}
