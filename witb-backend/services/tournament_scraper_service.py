"""Tournament scraper service following CLAUDE.md O-4."""

from datetime import datetime

import aiohttp
from sqlalchemy import text

from brand_urls import get_brand_url
from database import engine


class SimpleTournamentScraper:
    """ESPN API tournament scraper with caching and fallback."""

    # ESPN Golf API endpoints
    ESPN_SCOREBOARD_URL = (
        "https://site.api.espn.com/apis/site/v2/sports/golf/pga/scoreboard"
    )
    ESPN_EVENTS_URL = "https://site.api.espn.com/apis/site/v2/sports/golf/pga/events"

    # Cache settings
    CACHE_DURATION_MINUTES = 30  # Cache for 30 minutes

    # Fallback winners in case API fails
    FALLBACK_WINNERS = [
        ("Justin Rose", "FedEx St. Jude Championship"),
        ("Scottie Scheffler", "Memorial Tournament"),
        ("Xander Schauffele", "PGA Championship"),
    ]

    def __init__(self):
        self._cache = {}
        self._cache_timestamp = None

    async def scrape_and_store_winner(self) -> dict[str, str]:
        """Get the most recent tournament winner and their WITB data"""
        try:
            # Check cache first
            if self._is_cache_valid():
                print("🎯 Using cached tournament data")
                return self._cache

            # Try to find current winner from ESPN API
            winner_data = await self._get_current_winner_from_api()

            if winner_data and winner_data.get("winner") != "Not found":
                # Get WITB data from our database
                witb_data = await self._get_winner_witb(winner_data["winner"])
                winner_data["witb_items"] = witb_data

                # Store in database
                await self._store_winner_in_db(winner_data)

                # Cache the result
                self._cache = winner_data
                self._cache_timestamp = datetime.now()
                print(
                    f"💾 Cached tournament data for {self.CACHE_DURATION_MINUTES} minutes"
                )

                return winner_data

            # Fallback to database
            return await self._get_winner_from_db()

        except Exception as e:
            print(f"Error in scrape_and_store_winner: {e}")
            return await self._get_winner_from_db()

    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self._cache or not self._cache_timestamp:
            return False

        cache_age = (datetime.now() - self._cache_timestamp).total_seconds() / 60
        return cache_age < self.CACHE_DURATION_MINUTES

    async def _get_current_winner_from_api(self) -> dict[str, str]:
        """Get current tournament winner from ESPN Golf API"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Cache-Control": "no-cache",
            }

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15)
            ) as session:
                # Rate limiting - small delay between requests
                import asyncio

                await asyncio.sleep(1)
                # Try scoreboard endpoint first
                async with session.get(
                    self.ESPN_SCOREBOARD_URL, headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        winner_data = self._extract_winner_from_scoreboard(data)
                        if winner_data.get("winner") != "Not found":
                            print(
                                f"✅ Found winner from ESPN API: {winner_data['winner']} - {winner_data['tournament']}"
                            )
                            return winner_data

                # Fallback to events endpoint
                async with session.get(
                    self.ESPN_EVENTS_URL, headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        winner_data = self._extract_winner_from_events(data)
                        if winner_data.get("winner") != "Not found":
                            print(
                                f"✅ Found winner from ESPN Events API: {winner_data['winner']} - {winner_data['tournament']}"
                            )
                            return winner_data

            print("⚠️ No current winner found in ESPN API, using fallback")
            return self._get_fallback_winner()

        except Exception as e:
            print(f"❌ Error fetching from ESPN API: {e}")
            return self._get_fallback_winner()

    def _extract_winner_from_scoreboard(self, data: dict) -> dict[str, str]:
        """Extract tournament winner from ESPN scoreboard API response"""
        try:
            if "events" in data and data["events"]:
                event = data["events"][0]  # Most recent tournament

                # Get tournament info
                tournament_name = event.get("name", "Unknown Tournament")
                event_date = event.get("date", datetime.now().strftime("%Y-%m-%d"))

                # Format date
                try:
                    parsed_date = datetime.strptime(event_date[:10], "%Y-%m-%d")
                    formatted_date = parsed_date.strftime("%B %d, %Y")
                except:
                    formatted_date = datetime.now().strftime("%B %d, %Y")

                # Check if tournament is completed
                competitions = event.get("competitions", [])
                if competitions and competitions[0].get("status", {}).get(
                    "type", {}
                ).get("name") in ["STATUS_FINAL", "Final"]:
                    # Get competitors and find winner (lowest score)
                    competitors = competitions[0].get("competitors", [])
                    if competitors:
                        # Sort by score (lowest wins in golf) - handle string scores
                        def get_numeric_score(competitor):
                            score = competitor.get("score", "999")
                            try:
                                # Convert score string to integer (e.g. "-18" -> -18)
                                return int(score) if score != "" else 999
                            except (ValueError, TypeError):
                                return 999

                        sorted_competitors = sorted(competitors, key=get_numeric_score)
                        winner = sorted_competitors[0]

                        winner_name = winner.get("athlete", {}).get(
                            "displayName", "Unknown"
                        )
                        winner_score = winner.get("score", 0)
                        # Handle score formatting safely
                        if isinstance(winner_score, (int, float)):
                            score_display = (
                                f"{int(winner_score):+d}" if winner_score != 0 else "E"
                            )
                        else:
                            # Handle string scores or other formats
                            try:
                                numeric_score = int(winner_score)
                                score_display = (
                                    f"{numeric_score:+d}" if numeric_score != 0 else "E"
                                )
                            except (ValueError, TypeError):
                                score_display = (
                                    str(winner_score) if winner_score else ""
                                )

                        return {
                            "winner": winner_name,
                            "tournament": tournament_name,
                            "date": formatted_date,
                            "score": score_display,
                        }

            return {"winner": "Not found", "tournament": "", "date": "", "score": ""}

        except Exception as e:
            print(f"Error parsing scoreboard data: {e}")
            return {"winner": "Not found", "tournament": "", "date": "", "score": ""}

    def _extract_winner_from_events(self, data: dict) -> dict[str, str]:
        """Extract tournament winner from ESPN events API response"""
        try:
            if "items" in data and data["items"]:
                # Find most recent completed tournament
                for event in data["items"]:
                    if event.get("status", {}).get("type", {}).get("name") in [
                        "STATUS_FINAL",
                        "Final",
                    ]:
                        tournament_name = event.get("name", "Unknown Tournament")
                        event_date = event.get(
                            "date", datetime.now().strftime("%Y-%m-%d")
                        )

                        # Format date
                        try:
                            parsed_date = datetime.strptime(event_date[:10], "%Y-%m-%d")
                            formatted_date = parsed_date.strftime("%B %d, %Y")
                        except:
                            formatted_date = datetime.now().strftime("%B %d, %Y")

                        # Get winner from competitions
                        competitions = event.get("competitions", [])
                        if competitions:
                            competitors = competitions[0].get("competitors", [])
                            if competitors:
                                # Find winner (position 1 or lowest score)
                                winner = None
                                for comp in competitors:
                                    if (
                                        comp.get("statistics", [{}])[0].get(
                                            "value", 999
                                        )
                                        == 1
                                    ):  # Position 1
                                        winner = comp
                                        break

                                # Fallback to first competitor if no position found
                                if not winner and competitors:
                                    winner = competitors[0]

                                if winner:
                                    winner_name = winner.get("athlete", {}).get(
                                        "displayName", "Unknown"
                                    )
                                    return {
                                        "winner": winner_name,
                                        "tournament": tournament_name,
                                        "date": formatted_date,
                                        "score": "",
                                    }

            return {"winner": "Not found", "tournament": "", "date": "", "score": ""}

        except Exception as e:
            print(f"Error parsing events data: {e}")
            return {"winner": "Not found", "tournament": "", "date": "", "score": ""}

    def _get_fallback_winner(self) -> dict[str, str]:
        """Return fallback winner when API fails"""
        winner, tournament = self.FALLBACK_WINNERS[0]
        return {
            "winner": winner,
            "tournament": tournament,
            "date": datetime.now().strftime("%B %d, %Y"),
            "score": "",
        }

    async def _get_winner_witb(self, winner_name: str) -> list[dict[str, str]]:
        """Get WITB data for the tournament winner from our database"""
        try:
            async with engine.begin() as conn:
                result = await conn.execute(
                    text(
                        """
                    SELECT p.id, p.name, w.category, w.brand, w.model, w.loft, w.shaft
                    FROM players p
                    LEFT JOIN witb_items w ON p.id = w.player_id
                    WHERE LOWER(p.name) LIKE LOWER(:name)
                    OR LOWER(p.name) LIKE LOWER(:fuzzy_name)
                    ORDER BY w.category
                """
                    ),
                    {
                        "name": f"%{winner_name}%",
                        "fuzzy_name": f"%{winner_name.split()[0]}%{winner_name.split()[-1]}%",
                    },
                )

                rows = result.fetchall()

                if rows:
                    witb_items = []
                    for row in rows:
                        if row[2]:  # If there's equipment data
                            brand = row[3]
                            witb_item = {
                                "category": row[2],
                                "brand": brand,
                                "model": row[4],
                                "loft": row[5] or "",
                                "shaft": row[6] or "",
                                "product_url": get_brand_url(brand) if brand else None,
                            }
                            witb_items.append(witb_item)

                    print(f"Found WITB data for {winner_name}: {len(witb_items)} items")
                    return witb_items
                else:
                    print(f"No WITB data found for {winner_name}")
                    return []

        except Exception as e:
            print(f"Error getting WITB data for {winner_name}: {e}")
            return []

    async def _store_winner_in_db(self, winner_data: dict[str, str]) -> None:
        """Store tournament winner in database"""
        try:
            async with engine.begin() as conn:
                # Create table if needed
                await conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS tournament_winners (
                        id SERIAL PRIMARY KEY,
                        winner VARCHAR(255) NOT NULL,
                        tournament VARCHAR(255) NOT NULL,
                        date VARCHAR(100),
                        score VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Check if already exists
                result = await conn.execute(
                    text(
                        """
                    SELECT COUNT(*) FROM tournament_winners 
                    WHERE winner = :winner AND tournament = :tournament
                """
                    ),
                    winner_data,
                )

                count = result.scalar()

                if count == 0:
                    # Insert new winner
                    await conn.execute(
                        text(
                            """
                        INSERT INTO tournament_winners (winner, tournament, date, score)
                        VALUES (:winner, :tournament, :date, :score)
                    """
                        ),
                        winner_data,
                    )
                    print(
                        f"Stored new tournament winner: {winner_data['winner']} - {winner_data['tournament']}"
                    )

        except Exception as e:
            print(f"Error storing winner in database: {e}")

    async def _get_winner_from_db(self) -> dict[str, str]:
        """Get the most recent tournament winner from database"""
        try:
            async with engine.begin() as conn:
                result = await conn.execute(
                    text(
                        """
                    SELECT winner, tournament, date, score 
                    FROM tournament_winners 
                    ORDER BY updated_at DESC 
                    LIMIT 1
                """
                    )
                )

                row = result.fetchone()
                if row:
                    return {
                        "winner": row[0],
                        "tournament": row[1],
                        "date": row[2] or datetime.now().strftime("%B %d, %Y"),
                        "score": row[3] or "",
                        "witb_items": [],
                    }

        except Exception as e:
            print(f"Error getting winner from database: {e}")

        # Final fallback
        return {
            "winner": "Aldrich Potgieter",
            "tournament": "Rocket Classic",
            "date": "July 04, 2025",
            "score": "",
            "witb_items": [],
        }


# Global instance
simple_tournament_scraper = SimpleTournamentScraper()
