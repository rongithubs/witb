#!/usr/bin/env python3
"""
URL Finder Module
Discovers and validates PGA Club Tracker URLs for players.
"""

import sqlite3
import requests
import re
import time
import random
from typing import List
from witb_models import PlayerInfo

class URLFinder:
    def __init__(self, db_path: str = "../witb-backend/dev.db"):
        self.db_path = db_path
        self.base_url = "https://www.pgaclubtracker.com/players"
        self.session = requests.Session()
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        ]
        
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_all_players_from_db(self, limit: int = 50) -> List[PlayerInfo]:
        """Get all players from the database."""
        try:
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
                player_info = PlayerInfo(
                    id=player[0],
                    name=player[1],
                    country=player[2],
                    tour=player[3],
                    ranking=player[4]
                )
                player_list.append(player_info)
            
            return player_list
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def generate_url_slug(self, player_name: str) -> str:
        """Generate URL slug from player name."""
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
    
    def rotate_user_agent(self):
        """Rotate User-Agent for best practices."""
        self.session.headers['User-Agent'] = random.choice(self.user_agents)
    
    def check_url_exists(self, url: str) -> bool:
        """Check if the URL exists and returns valid content."""
        try:
            self.rotate_user_agent()
            response = self.session.head(url, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except requests.RequestException:
            try:
                # Try GET request if HEAD fails
                response = self.session.get(url, timeout=10)
                return response.status_code == 200
            except requests.RequestException:
                return False
    
    def find_valid_urls(self, players: List[PlayerInfo], verbose: bool = True) -> List[PlayerInfo]:
        """Find valid URLs for all players."""
        valid_players = []
        
        if verbose:
            print(f"Checking URLs for {len(players)} players...")
            print("=" * 60)
        
        for i, player in enumerate(players, 1):
            witb_url = self.generate_witb_url(player.name)
            
            if verbose:
                print(f"{i:2d}. {player.name:<25} ", end="", flush=True)
            
            # Check if URL exists
            url_exists = self.check_url_exists(witb_url)
            
            if url_exists:
                if verbose:
                    print("✓ Valid URL found")
                player.url = witb_url
                valid_players.append(player)
            else:
                if verbose:
                    print("✗ No valid URL")
            
            # Be respectful - small delay between requests
            if i % 10 == 0:
                if verbose:
                    print(f"  Processed {i}/{len(players)} players...")
                time.sleep(2)
            else:
                time.sleep(0.5)
        
        if verbose:
            print(f"\nFound valid URLs for {len(valid_players)}/{len(players)} players")
        
        return valid_players