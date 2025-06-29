#!/usr/bin/env python3
"""
Database Updater Module
Handles updating the database with scraped WITB data.
"""

import sqlite3
import uuid
import json
from typing import List, Dict
from witb_models import PlayerWITB

class DatabaseUpdater:
    def __init__(self, db_path: str = "../witb-backend/dev.db"):
        self.db_path = db_path
    
    def update_player_witb(self, player_witb: PlayerWITB) -> bool:
        """Update WITB data for a single player."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing WITB items
            cursor.execute("DELETE FROM witb_items WHERE player_id = ?", (player_witb.player_id,))
            
            # Add new WITB items
            for item in player_witb.witb_items:
                item_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO witb_items (id, player_id, category, brand, model, loft, shaft)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    item_id,
                    player_witb.player_id,
                    item.category,
                    item.brand,
                    item.model,
                    item.loft,
                    item.shaft
                ))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Database error for {player_witb.name}: {e}")
            return False
    
    def update_all_players(self, players_witb: List[PlayerWITB], verbose: bool = True) -> int:
        """Update database with all scraped WITB data."""
        if not players_witb:
            return 0
        
        success_count = 0
        
        if verbose:
            print(f"Updating database with {len(players_witb)} players...")
        
        for player_witb in players_witb:
            if self.update_player_witb(player_witb):
                success_count += 1
            else:
                if verbose:
                    print(f"Failed to update {player_witb.name}")
        
        if verbose:
            print(f"Successfully updated {success_count}/{len(players_witb)} players in database")
        
        return success_count
    
    def save_to_json(self, players_witb: List[PlayerWITB], filename: str = "witb_data.json") -> bool:
        """Save results to JSON file."""
        try:
            output_data = []
            
            for player in players_witb:
                player_data = {
                    'name': player.name,
                    'country': player.country,
                    'tour': player.tour,
                    'ranking': player.ranking,
                    'player_id': player.player_id,
                    'source_url': player.source_url,
                    'witb_items': []
                }
                
                for item in player.witb_items:
                    item_data = {
                        'category': item.category,
                        'brand': item.brand,
                        'model': item.model,
                        'loft': item.loft,
                        'shaft': item.shaft
                    }
                    player_data['witb_items'].append(item_data)
                
                output_data.append(player_data)
            
            with open(filename, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"Results saved to {filename}")
            return True
            
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False
    
    def get_database_summary(self, verbose: bool = True) -> Dict:
        """Get summary of WITB data in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get players with WITB items
            cursor.execute("""
                SELECT p.name, p.ranking, COUNT(w.id) as witb_count
                FROM players p
                LEFT JOIN witb_items w ON p.id = w.player_id
                WHERE p.ranking <= 50
                GROUP BY p.id, p.name, p.ranking
                ORDER BY p.ranking
            """)
            
            results = cursor.fetchall()
            
            # Calculate totals
            total_players = len(results)
            players_with_witb = sum(1 for _, _, count in results if count > 0)
            total_items = sum(count for _, _, count in results)
            
            summary = {
                'total_players': total_players,
                'players_with_witb': players_with_witb,
                'total_witb_items': total_items,
                'coverage_percentage': (players_with_witb / total_players * 100) if total_players > 0 else 0
            }
            
            if verbose:
                print(f"\nDatabase Summary:")
                print("=" * 40)
                print(f"Total players in top 50: {total_players}")
                print(f"Players with WITB data: {players_with_witb}")
                print(f"Total WITB items: {total_items}")
                print(f"Coverage: {summary['coverage_percentage']:.1f}%")
                
                print(f"\nTop 10 Players:")
                for name, ranking, witb_count in results[:10]:
                    print(f"  {ranking:2d}. {name:<25} - {witb_count} items")
            
            conn.close()
            return summary
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {}
    
    def print_summary(self, players_witb: List[PlayerWITB]):
        """Print summary of scraping results."""
        total_items = sum(len(player.witb_items) for player in players_witb)
        
        print(f"\n" + "=" * 60)
        print("SCRAPING SUMMARY")
        print("=" * 60)
        print(f"Players with WITB data: {len(players_witb)}")
        print(f"Total WITB items: {total_items}")
        print(f"Average items per player: {total_items/len(players_witb):.1f}" if players_witb else 0)
        
        # Show top players
        print(f"\nTop 10 Players:")
        for player in sorted(players_witb, key=lambda p: p.ranking)[:10]:
            print(f"  {player.ranking:2d}. {player.name:<25} - {len(player.witb_items)} items")