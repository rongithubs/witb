#!/usr/bin/env python3
"""
PGA-only WITB Update Script
Updates WITB data for PGA Tour players only.
"""

import sqlite3
from url_finder import URLFinder
from witb_scraper import WITBScraper
from database_updater import DatabaseUpdater
from witb_models import PlayerInfo

class PGAURLFinder(URLFinder):
    def get_pga_players_from_db(self, limit: int = 50):
        """Get only PGA Tour players from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, country, tour, ranking 
                FROM players 
                WHERE tour = 'PGA Tour' AND ranking IS NOT NULL 
                ORDER BY ranking ASC 
                LIMIT ?
            """, (limit,))
            
            players = cursor.fetchall()
            conn.close()
            
            player_list = []
            for player in players:
                player_info = PlayerInfo(
                    id=player[0],
                    name=player[1],
                    country=player[2],
                    tour=player[3],
                    ranking=player[4]
                )
                player_list.append(player_info)
            
            return player_list
            
        except Exception as e:
            print(f"Error getting PGA players from database: {e}")
            return []

def main():
    """Update WITB data for PGA Tour players only."""
    print("PGA Tour WITB Update")
    print("=" * 30)
    
    # Initialize components
    url_finder = PGAURLFinder()
    scraper = WITBScraper()
    db_updater = DatabaseUpdater()
    
    # Get PGA Tour players only
    print("Loading PGA Tour players from database...")
    players = url_finder.get_pga_players_from_db(limit=50)
    
    if not players:
        print("No PGA Tour players found!")
        return
    
    print(f"Loaded {len(players)} PGA Tour players")
    
    # Find valid URLs
    print("\nFinding valid WITB URLs...")
    valid_players = url_finder.find_valid_urls(players, verbose=True)
    
    if not valid_players:
        print("No valid URLs found!")
        return
    
    # Scrape WITB data
    print(f"\nScraping WITB data for {len(valid_players)} PGA players...")
    scraped_data = scraper.scrape_multiple_players(valid_players, verbose=True)
    
    if not scraped_data:
        print("No WITB data was scraped!")
        return
    
    # Save results
    print("\nSaving results...")
    db_updater.save_to_json(scraped_data, "pga_witb_data.json")
    
    # Update database
    print("\nUpdating database...")
    success_count = db_updater.update_all_players(scraped_data, verbose=True)
    
    if success_count > 0:
        db_updater.get_database_summary(verbose=True)
    
    # Print summary
    db_updater.print_summary(scraped_data)
    print(f"\n✓ PGA Tour WITB update completed!")
    print(f"Processed {len(scraped_data)} PGA players with WITB data")

if __name__ == "__main__":
    main()