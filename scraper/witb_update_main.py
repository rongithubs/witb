#!/usr/bin/env python3
"""
WITB Main Orchestrator
Coordinates URL finding, scraping, and database updates for WITB data.
"""

import argparse
from url_finder import URLFinder
from witb_scraper import WITBScraper
from database_updater import DatabaseUpdater

def main():
    """Main function to orchestrate the WITB scraping process."""
    parser = argparse.ArgumentParser(description='WITB Scraper for PGA Club Tracker')
    parser.add_argument('--limit', type=int, default=50, help='Number of players to process (default: 50)')
    parser.add_argument('--find-urls-only', action='store_true', help='Only find URLs, don\'t scrape')
    parser.add_argument('--scrape-only', action='store_true', help='Skip URL finding, use existing data')
    parser.add_argument('--no-db-update', action='store_true', help='Don\'t update database')
    parser.add_argument('--output', default='witb_data.json', help='Output JSON filename')
    parser.add_argument('--quiet', action='store_true', help='Minimize output')
    
    args = parser.parse_args()
    
    verbose = not args.quiet
    
    if verbose:
        print("WITB Scraper for All Players")
        print("=" * 40)
    
    # Initialize components
    url_finder = URLFinder()
    scraper = WITBScraper()
    db_updater = DatabaseUpdater()
    
    # Step 1: Get players from database
    if verbose:
        print(f"Loading {args.limit} players from database...")
    
    players = url_finder.get_all_players_from_db(limit=args.limit)
    if not players:
        print("No players found in database!")
        return
    
    if verbose:
        print(f"Loaded {len(players)} players")
    
    # Step 2: Find valid URLs (unless skipping)
    if not args.scrape_only:
        if verbose:
            print("\nFinding valid WITB URLs...")
        
        valid_players = url_finder.find_valid_urls(players, verbose=verbose)
        
        if not valid_players:
            print("No valid URLs found!")
            return
        
        if args.find_urls_only:
            if verbose:
                print(f"\nURL finding complete. Found {len(valid_players)} valid URLs.")
            return
    else:
        # For scrape-only mode, assume all players have URLs
        valid_players = [p for p in players if p.url]
        if not valid_players:
            print("No players with URLs found! Run URL finding first.")
            return
    
    # Step 3: Scrape WITB data
    if verbose:
        print(f"\nScraping WITB data for {len(valid_players)} players...")
    
    scraped_data = scraper.scrape_multiple_players(valid_players, verbose=verbose)
    
    if not scraped_data:
        print("No WITB data was scraped!")
        return
    
    # Step 4: Save results to JSON
    if verbose:
        print(f"\nSaving results...")
    
    db_updater.save_to_json(scraped_data, args.output)
    
    # Step 5: Update database (unless skipping)
    if not args.no_db_update:
        if verbose:
            print(f"\nUpdating database...")
        
        success_count = db_updater.update_all_players(scraped_data, verbose=verbose)
        
        if success_count > 0:
            # Show database summary
            db_updater.get_database_summary(verbose=verbose)
    
    # Step 6: Print final summary
    if verbose:
        db_updater.print_summary(scraped_data)
        print(f"\n✓ WITB scraping completed successfully!")
        print(f"Processed {len(scraped_data)} players with WITB data")
        
        if not args.no_db_update:
            print(f"Database updated. Check the frontend for new WITB data!")

def quick_update(limit: int = 10):
    """Quick function to update a few players (for testing)."""
    print(f"Quick WITB update for top {limit} players")
    print("=" * 40)
    
    url_finder = URLFinder()
    scraper = WITBScraper()
    db_updater = DatabaseUpdater()
    
    # Get players
    players = url_finder.get_all_players_from_db(limit=limit)
    if not players:
        print("No players found!")
        return
    
    # Find URLs
    valid_players = url_finder.find_valid_urls(players, verbose=False)
    if not valid_players:
        print("No valid URLs found!")
        return
    
    print(f"Found {len(valid_players)} valid URLs")
    
    # Scrape data
    scraped_data = scraper.scrape_multiple_players(valid_players, verbose=False)
    if not scraped_data:
        print("No data scraped!")
        return
    
    print(f"Scraped {len(scraped_data)} players")
    
    # Update database
    success_count = db_updater.update_all_players(scraped_data, verbose=False)
    print(f"Updated {success_count} players in database")
    
    # Show summary
    db_updater.get_database_summary(verbose=True)

if __name__ == "__main__":
    main()