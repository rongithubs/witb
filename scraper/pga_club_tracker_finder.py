#!/usr/bin/env python3
"""
PGA Club Tracker WITB URL Finder
Generates and validates WITB URLs using PGA Club Tracker format.
URL format: https://www.pgaclubtracker.com/players/{player-name-witb-whats-in-the-bag}
"""

import sqlite3
import re
import requests
from typing import List, Dict, Optional
import time

class PGAClubTrackerFinder:
    def __init__(self, db_path: str = "../witb-backend/dev.db"):
        self.db_path = db_path
        self.base_url = "https://www.pgaclubtracker.com/players"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_top_players(self, limit: int = 5) -> List[Dict]:
        """Get top players from database ordered by ranking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, country, tour, ranking 
            FROM players 
            WHERE ranking IS NOT NULL 
            ORDER BY ranking ASC 
            LIMIT ?
        """, (limit,))
        
        players = cursor.fetchall()
        conn.close()
        
        player_list = []
        for player in players:
            player_dict = {
                'id': player[0],
                'name': player[1],
                'country': player[2],
                'tour': player[3],
                'ranking': player[4]
            }
            player_list.append(player_dict)
            
        return player_list
    
    def generate_url_slug(self, player_name: str) -> str:
        """Generate URL slug from player name following PGA Club Tracker format."""
        # Convert to lowercase
        slug = player_name.lower()
        
        # Remove periods and other punctuation
        slug = re.sub(r'[^\w\s-]', '', slug)
        
        # Replace spaces with hyphens
        slug = re.sub(r'\s+', '-', slug)
        
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        # Add the WITB suffix
        slug = f"{slug}-witb-whats-in-the-bag"
        
        return slug
    
    def generate_witb_url(self, player_name: str) -> str:
        """Generate full WITB URL for a player."""
        slug = self.generate_url_slug(player_name)
        return f"{self.base_url}/{slug}"
    
    def check_url_exists(self, url: str) -> bool:
        """Check if the URL exists and returns valid content."""
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except requests.RequestException:
            try:
                # Try GET request if HEAD fails
                response = self.session.get(url, timeout=10)
                return response.status_code == 200
            except requests.RequestException:
                return False
    
    def find_witb_urls(self, limit: int = 5) -> List[Dict]:
        """Find WITB URLs for top players."""
        players = self.get_top_players(limit)
        results = []
        
        print(f"Finding WITB URLs for top {limit} players using PGA Club Tracker...")
        print("=" * 70)
        
        for i, player in enumerate(players, 1):
            name = player['name']
            witb_url = self.generate_witb_url(name)
            
            print(f"\n{i}. {name} (Rank: {player['ranking']}) - {player['country']}")
            print(f"   Generated URL: {witb_url}")
            
            # Check if URL exists
            print("   Checking URL validity...")
            url_exists = self.check_url_exists(witb_url)
            
            status = "✓ Valid" if url_exists else "✗ Invalid"
            print(f"   Status: {status}")
            
            result = {
                'ranking': player['ranking'],
                'name': name,
                'country': player['country'],
                'tour': player['tour'],
                'witb_url': witb_url,
                'url_exists': url_exists,
                'url_slug': self.generate_url_slug(name)
            }
            results.append(result)
            
            # Be respectful to the server
            time.sleep(1)
        
        return results
    
    def save_results(self, results: List[Dict], filename: str = "pga_club_tracker_urls.txt"):
        """Save results to a text file."""
        with open(filename, 'w') as f:
            f.write("PGA Club Tracker WITB URL Results\n")
            f.write("=" * 40 + "\n\n")
            
            valid_count = 0
            for result in results:
                f.write(f"Player: {result['name']}\n")
                f.write(f"Ranking: {result['ranking']}\n")
                f.write(f"Country: {result['country']}\n")
                f.write(f"Tour: {result['tour']}\n")
                f.write(f"URL Slug: {result['url_slug']}\n")
                f.write(f"WITB URL: {result['witb_url']}\n")
                f.write(f"URL Valid: {'Yes' if result['url_exists'] else 'No'}\n")
                f.write("-" * 50 + "\n\n")
                
                if result['url_exists']:
                    valid_count += 1
            
            f.write(f"Summary:\n")
            f.write(f"Total players: {len(results)}\n")
            f.write(f"Valid URLs: {valid_count}\n")
            f.write(f"Invalid URLs: {len(results) - valid_count}\n")
        
        print(f"\nResults saved to {filename}")
    
    def print_summary(self, results: List[Dict]):
        """Print summary of results."""
        valid_urls = [r for r in results if r['url_exists']]
        invalid_urls = [r for r in results if not r['url_exists']]
        
        print(f"\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(f"Total players processed: {len(results)}")
        print(f"Valid URLs found: {len(valid_urls)}")
        print(f"Invalid URLs: {len(invalid_urls)}")
        
        if valid_urls:
            print(f"\nValid URLs:")
            for result in valid_urls:
                print(f"  • {result['name']}: {result['witb_url']}")
        
        if invalid_urls:
            print(f"\nInvalid URLs (may need manual checking):")
            for result in invalid_urls:
                print(f"  • {result['name']}: {result['witb_url']}")


def main():
    """Main function to run the PGA Club Tracker URL finder."""
    finder = PGAClubTrackerFinder()
    
    # Find URLs for top 5 players
    results = finder.find_witb_urls(limit=5)
    
    # Save results to file
    finder.save_results(results)
    
    # Print summary
    finder.print_summary(results)


if __name__ == "__main__":
    main()