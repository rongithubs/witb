"""Main PGA Club Tracker scraper engine following CLAUDE.md C-4."""

import asyncio
from datetime import datetime
from enum import Enum
from typing import List, Tuple
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

import models
from custom_types import PlayerId
from repositories.player_repository import PlayerRepository
from services.scraper_service import PGAClubTrackerScraper as HTMLScraper
from services.witb_sync_service import WITBSyncService, SyncAction
from services.url_service import generate_pga_tracker_url


class ScrapingStatus(Enum):
    """Status of individual player scraping."""

    SUCCESS = "success"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class PlayerScrapingResult:
    """Result of scraping a single player."""

    player_name: str
    status: ScrapingStatus
    items_scraped: int
    message: str
    url: str


@dataclass
class ScrapingReport:
    """Complete report of scraping session."""

    total_players: int
    successful_players: int
    failed_players: int
    skipped_players: int
    start_time: datetime
    end_time: datetime
    player_results: List[PlayerScrapingResult]


class PGATrackerScraper:
    """Main scraper for PGA Club Tracker WITB data."""

    def __init__(self, db: AsyncSession, request_delay: float = 2.0):
        """
        Initialize main scraper.

        Args:
            db: Database session
            request_delay: Seconds between requests (default: 2.0)
        """
        self.db = db
        self.request_delay = request_delay

        # Initialize repositories and services
        self.player_repo = PlayerRepository(db)
        self.html_scraper = HTMLScraper(request_delay=request_delay)
        self.sync_service = WITBSyncService(db)

    async def scrape_top_players(self, limit: int = 50) -> ScrapingReport:
        """
        Scrape WITB data for top ranked players.

        Args:
            limit: Number of top players to scrape (default: 50)

        Returns:
            ScrapingReport with results for all players
        """
        start_time = datetime.now()

        print(f"Starting scrape of top {limit} players...")

        # Get top players from database
        players = await self._get_top_players(limit)

        if not players:
            print("No players found in database")
            return ScrapingReport(
                total_players=0,
                successful_players=0,
                failed_players=0,
                skipped_players=0,
                start_time=start_time,
                end_time=datetime.now(),
                player_results=[],
            )

        print(f"Found {len(players)} players to scrape")

        # Scrape each player
        player_results = []
        successful_count = 0
        failed_count = 0
        skipped_count = 0

        for i, player in enumerate(players, 1):
            print(f"[{i}/{len(players)}] Scraping {player.name}...")

            result = await self._scrape_single_player(player)
            player_results.append(result)

            if result.status == ScrapingStatus.SUCCESS:
                successful_count += 1
                print(f"  ✅ {result.message}")
            elif result.status == ScrapingStatus.SKIPPED:
                skipped_count += 1
                print(f"  ⏭️  {result.message}")
            else:
                failed_count += 1
                print(f"  ❌ {result.message}")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\nScraping completed in {duration:.1f} seconds")
        print(
            f"Results: {successful_count} updated, {skipped_count} skipped, {failed_count} failed"
        )

        return ScrapingReport(
            total_players=len(players),
            successful_players=successful_count,
            failed_players=failed_count,
            skipped_players=skipped_count,
            start_time=start_time,
            end_time=end_time,
            player_results=player_results,
        )

    async def _get_top_players(self, limit: int) -> List[models.Player]:
        """Get top ranked players from database."""
        return await self.player_repo.get_top_ranked_players(limit)

    async def _scrape_single_player(
        self, player: models.Player
    ) -> PlayerScrapingResult:
        """
        Scrape WITB data for a single player.

        Args:
            player: Player model from database

        Returns:
            PlayerScrapingResult with scraping outcome
        """
        try:
            # Generate URL for player
            first_name, last_name = self._extract_player_names(player.name)
            url = generate_pga_tracker_url(first_name, last_name)

            # Scrape HTML data
            witb_data = await self.html_scraper.scrape_player_witb(url)

            # Sync with database
            sync_result = await self.sync_service.sync_player_equipment(
                PlayerId(player.id), witb_data
            )

            # Map sync result to scraping status
            if sync_result.action == SyncAction.UPDATED:
                status = ScrapingStatus.SUCCESS
            elif sync_result.action == SyncAction.SKIPPED:
                status = ScrapingStatus.SKIPPED
            else:
                status = ScrapingStatus.ERROR

            return PlayerScrapingResult(
                player_name=player.name,
                status=status,
                items_scraped=sync_result.items_count,
                message=sync_result.message,
                url=url,
            )

        except Exception as e:
            return PlayerScrapingResult(
                player_name=player.name,
                status=ScrapingStatus.ERROR,
                items_scraped=0,
                message=f"Scraping failed: {str(e)}",
                url=self._generate_player_url(player),
            )

    def _extract_player_names(self, full_name: str) -> Tuple[str, str]:
        """
        Extract first and last names from full name.

        Args:
            full_name: Complete player name (e.g., "Scottie Scheffler")

        Returns:
            Tuple of (first_name, last_name)

        Raises:
            ValueError: If name format is invalid
        """
        name_parts = full_name.strip().split()

        if len(name_parts) < 2:
            raise ValueError(f"Invalid player name format: {full_name}")

        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:])  # Handle multiple last name parts

        return first_name, last_name

    def _generate_player_url(self, player: models.Player) -> str:
        """Generate PGA Club Tracker URL for player."""
        try:
            first_name, last_name = self._extract_player_names(player.name)
            return generate_pga_tracker_url(first_name, last_name)
        except ValueError:
            return f"https://www.pgaclubtracker.com/players/{player.name.lower().replace(' ', '-')}-witb"
