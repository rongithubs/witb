"""Tournament scraper service following CLAUDE.md O-4."""

from datetime import datetime, timedelta

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
    # Cache settings
    CACHE_DURATION_MINUTES = 30  # Cache for 30 minutes

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
        """Walk back up to 21 days to find the most recently completed PGA Tour event."""
        import asyncio

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Cache-Control": "no-cache",
        }

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15)
            ) as session:
                for days_back in range(0, 22):
                    date_str = (datetime.now() - timedelta(days=days_back)).strftime(
                        "%Y%m%d"
                    )
                    url = f"{self.ESPN_SCOREBOARD_URL}?dates={date_str}"
                    await asyncio.sleep(0.3)
                    async with session.get(url, headers=headers) as response:
                        if response.status != 200:
                            continue
                        data = await response.json()
                        winner_data = self._extract_winner_from_scoreboard(data)
                        if winner_data.get("winner") != "Not found":
                            print(
                                f"✅ Found winner (dates={date_str}): {winner_data['winner']} - {winner_data['tournament']}"
                            )
                            return winner_data

            print("⚠️ No completed tournament found in past 21 days, falling back to DB")
            return {"winner": "Not found", "tournament": "", "date": "", "score": ""}

        except Exception as e:
            print(f"❌ Error fetching from ESPN API: {e}")
            return {"winner": "Not found", "tournament": "", "date": "", "score": ""}

    def _extract_winner_from_scoreboard(self, data: dict) -> dict[str, str]:
        """Extract most recently completed tournament winner from ESPN scoreboard API response"""
        try:
            for event in data.get("events", []):
                tournament_name = event.get("name", "Unknown Tournament")
                event_date = event.get("date", datetime.now().strftime("%Y-%m-%d"))

                competitions = event.get("competitions", [])
                if not competitions:
                    continue

                status_name = (
                    competitions[0].get("status", {}).get("type", {}).get("name", "")
                )
                if status_name not in ["STATUS_FINAL", "Final"]:
                    continue

                # Format date
                try:
                    parsed_date = datetime.strptime(event_date[:10], "%Y-%m-%d")
                    formatted_date = parsed_date.strftime("%B %d, %Y")
                except Exception:
                    formatted_date = datetime.now().strftime("%B %d, %Y")

                competitors = competitions[0].get("competitors", [])
                if not competitors:
                    continue

                def get_numeric_score(competitor: dict) -> int:
                    score = competitor.get("score", "999")
                    try:
                        return int(score) if score != "" else 999
                    except (ValueError, TypeError):
                        return 999

                winner = sorted(competitors, key=get_numeric_score)[0]
                winner_name = winner.get("athlete", {}).get("displayName", "Unknown")
                winner_score = winner.get("score", 0)

                if isinstance(winner_score, (int, float)):
                    score_display = (
                        f"{int(winner_score):+d}" if winner_score != 0 else "E"
                    )
                else:
                    try:
                        numeric_score = int(winner_score)
                        score_display = (
                            f"{numeric_score:+d}" if numeric_score != 0 else "E"
                        )
                    except (ValueError, TypeError):
                        score_display = str(winner_score) if winner_score else ""

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
        """Store tournament winner in database, replacing any stale entries."""
        try:
            async with engine.begin() as conn:
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

                result = await conn.execute(
                    text(
                        """
                    SELECT COUNT(*) FROM tournament_winners
                    WHERE winner = :winner AND tournament = :tournament
                """
                    ),
                    winner_data,
                )
                already_current = result.scalar() > 0

                if already_current:
                    await conn.execute(
                        text(
                            """
                        UPDATE tournament_winners
                        SET updated_at = CURRENT_TIMESTAMP
                        WHERE winner = :winner AND tournament = :tournament
                    """
                        ),
                        winner_data,
                    )
                    print(
                        f"Refreshed timestamp for existing winner: {winner_data['winner']} - {winner_data['tournament']}"
                    )
                else:
                    # New winner confirmed — remove stale entries then insert
                    await conn.execute(text("DELETE FROM tournament_winners"))
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
            "winner": "Collin Morikawa",
            "tournament": "AT&T Pebble Beach Pro-Am",
            "date": "February 09, 2026",
            "score": "",
            "witb_items": [],
        }


# Global instance
simple_tournament_scraper = SimpleTournamentScraper()
