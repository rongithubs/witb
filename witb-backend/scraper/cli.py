#!/usr/bin/env python3
"""CLI interface for PGA Club Tracker scraper following CLAUDE.md standards."""
import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import SessionLocal
from scraper.pga_tracker_scraper import PGATrackerScraper


async def run_scraper(players_count: int, delay: float, dry_run: bool) -> None:
    """
    Run the PGA Club Tracker scraper.

    Args:
        players_count: Number of top players to scrape
        delay: Delay between requests in seconds
        dry_run: If True, only show what would be scraped without making changes
    """
    if dry_run:
        print(f"[DRY RUN] Would scrape top {players_count} players with {delay}s delay")
        return

    async with SessionLocal() as db:
        scraper = PGATrackerScraper(db, request_delay=delay)

        try:
            report = await scraper.scrape_top_players(players_count)

            # Print summary
            print(f"\n{'='*60}")
            print("SCRAPING SUMMARY")
            print(f"{'='*60}")
            print(f"Total players: {report.total_players}")
            print(f"Successfully updated: {report.successful_players}")
            print(f"Skipped (no new data): {report.skipped_players}")
            print(f"Failed: {report.failed_players}")

            duration = (report.end_time - report.start_time).total_seconds()
            print(f"Duration: {duration:.1f} seconds")

            if report.failed_players > 0:
                print(f"\nFailed players:")
                for result in report.player_results:
                    if result.status.value == "error":
                        print(f"  - {result.player_name}: {result.message}")

            return report

        except KeyboardInterrupt:
            print("\n\nScraping interrupted by user")
            return
        except Exception as e:
            print(f"\nScraping failed with error: {e}")
            raise


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Scrape WITB data from PGA Club Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scraper/cli.py --players 10 --delay 2.0
  python scraper/cli.py --players 50 --delay 1.5 --dry-run
        """,
    )

    parser.add_argument(
        "--players",
        type=int,
        default=50,
        help="Number of top players to scrape (default: 50)",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay between requests in seconds (default: 2.0)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be scraped without making changes",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.players <= 0:
        print("Error: --players must be positive")
        sys.exit(1)

    if args.delay < 0:
        print("Error: --delay must be non-negative")
        sys.exit(1)

    # Run scraper
    try:
        asyncio.run(run_scraper(args.players, args.delay, args.dry_run))
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
