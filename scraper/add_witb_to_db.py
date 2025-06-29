#!/usr/bin/env python3
"""
Add WITB Data to Database
Reads the scraped WITB data and adds it to the dev.db database.
Matches players by name and inserts WITB items.
"""

import sqlite3
import json
import uuid
from typing import List, Dict, Optional

class WITBDatabaseUpdater:
    def __init__(self, db_path: str = "../witb-backend/dev.db", witb_file: str = "current_witb_data.json"):
        self.db_path = db_path
        self.witb_file = witb_file
    
    def load_witb_data(self) -> List[Dict]:
        """Load the scraped WITB data from JSON file."""
        try:
            with open(self.witb_file, 'r') as f:
                data = json.load(f)
            print(f"Loaded WITB data for {len(data)} players")
            return data
        except FileNotFoundError:
            print(f"Error: {self.witb_file} not found. Run the scraper first.")
            return []
        except json.JSONDecodeError as e:
            print(f"Error reading JSON file: {e}")
            return []
    
    def get_player_by_name(self, conn: sqlite3.Connection, player_name: str) -> Optional[str]:
        """Find a player in the database by name and return their ID."""
        cursor = conn.cursor()
        
        # Try exact match first
        cursor.execute("SELECT id FROM players WHERE name = ?", (player_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Try case-insensitive match
        cursor.execute("SELECT id, name FROM players WHERE LOWER(name) = LOWER(?)", (player_name,))
        result = cursor.fetchone()
        
        if result:
            print(f"  Found player with case difference: '{result[1]}' -> '{player_name}'")
            return result[0]
        
        # Try partial match (last name)
        last_name = player_name.split()[-1] if ' ' in player_name else player_name
        cursor.execute("SELECT id, name FROM players WHERE name LIKE ?", (f"%{last_name}%",))
        results = cursor.fetchall()
        
        if len(results) == 1:
            print(f"  Found player by last name match: '{results[0][1]}' -> '{player_name}'")
            return results[0][0]
        elif len(results) > 1:
            print(f"  Multiple players found for '{last_name}': {[r[1] for r in results]}")
            # Try to find exact match within results
            for player_id, name in results:
                if player_name.lower() in name.lower() or name.lower() in player_name.lower():
                    print(f"  Selected best match: '{name}' -> '{player_name}'")
                    return player_id
        
        return None
    
    def clear_existing_witb_items(self, conn: sqlite3.Connection, player_id: str):
        """Clear existing WITB items for a player."""
        cursor = conn.cursor()
        cursor.execute("DELETE FROM witb_items WHERE player_id = ?", (player_id,))
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            print(f"    Cleared {deleted_count} existing WITB items")
    
    def add_witb_item(self, conn: sqlite3.Connection, player_id: str, item: Dict) -> bool:
        """Add a single WITB item to the database."""
        try:
            cursor = conn.cursor()
            
            # Generate new UUID for the item
            item_id = str(uuid.uuid4())
            
            # Insert the WITB item
            cursor.execute("""
                INSERT INTO witb_items (id, player_id, category, brand, model, loft, shaft)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                item_id,
                player_id,
                item.get('category'),
                item.get('brand'),
                item.get('model'),
                item.get('loft'),
                item.get('shaft')
            ))
            
            return True
            
        except sqlite3.Error as e:
            print(f"    Error adding WITB item: {e}")
            print(f"    Item data: {item}")
            return False
    
    def update_player_witb(self, conn: sqlite3.Connection, player_data: Dict) -> bool:
        """Update WITB data for a single player."""
        player_name = player_data['name']
        witb_items = player_data.get('witb_items', [])
        
        print(f"\nProcessing {player_name}...")
        
        # Find player in database
        player_id = self.get_player_by_name(conn, player_name)
        
        if not player_id:
            print(f"  ✗ Player '{player_name}' not found in database")
            return False
        
        print(f"  ✓ Found player ID: {player_id}")
        
        # Clear existing WITB items
        self.clear_existing_witb_items(conn, player_id)
        
        # Add new WITB items
        added_count = 0
        for item in witb_items:
            if self.add_witb_item(conn, player_id, item):
                added_count += 1
        
        print(f"  ✓ Added {added_count}/{len(witb_items)} WITB items")
        
        return added_count > 0
    
    def update_database(self) -> bool:
        """Update the database with all scraped WITB data."""
        # Load WITB data
        witb_data = self.load_witb_data()
        if not witb_data:
            return False
        
        # Connect to database
        try:
            conn = sqlite3.connect(self.db_path)
            print(f"Connected to database: {self.db_path}")
            
            # Process each player
            success_count = 0
            for player_data in witb_data:
                if self.update_player_witb(conn, player_data):
                    success_count += 1
            
            # Commit changes
            conn.commit()
            print(f"\nDatabase updated successfully!")
            print(f"Players processed: {success_count}/{len(witb_data)}")
            
            # Show summary
            self.show_database_summary(conn)
            
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def show_database_summary(self, conn: sqlite3.Connection):
        """Show summary of players and their WITB items."""
        cursor = conn.cursor()
        
        # Get players with WITB items
        cursor.execute("""
            SELECT p.name, p.ranking, COUNT(w.id) as witb_count
            FROM players p
            LEFT JOIN witb_items w ON p.id = w.player_id
            WHERE p.ranking <= 10
            GROUP BY p.id, p.name, p.ranking
            ORDER BY p.ranking
        """)
        
        results = cursor.fetchall()
        
        print(f"\nDatabase Summary (Top 10 Players):")
        print("=" * 50)
        for name, ranking, witb_count in results:
            print(f"{ranking:2d}. {name:<25} - {witb_count} WITB items")
    
    def verify_witb_data(self) -> bool:
        """Verify the WITB data was added correctly."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check specific players we just added
            test_players = ['Scottie Scheffler', 'Rory McIlroy', 'Sepp Straka']
            
            print(f"\nVerifying WITB data...")
            print("=" * 40)
            
            for player_name in test_players:
                cursor.execute("""
                    SELECT p.name, w.category, w.brand, w.model
                    FROM players p
                    JOIN witb_items w ON p.id = w.player_id
                    WHERE p.name = ?
                    ORDER BY w.category
                """, (player_name,))
                
                items = cursor.fetchall()
                print(f"\n{player_name}: {len(items)} items")
                
                for name, category, brand, model in items[:3]:  # Show first 3 items
                    print(f"  • {category}: {brand} {model}")
                
                if len(items) > 3:
                    print(f"  ... and {len(items) - 3} more items")
            
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Verification error: {e}")
            return False


def main():
    """Main function to update the database with WITB data."""
    updater = WITBDatabaseUpdater()
    
    print("WITB Database Updater")
    print("=" * 30)
    
    # Update database
    if updater.update_database():
        # Verify the data
        updater.verify_witb_data()
        print(f"\n✓ Database update completed successfully!")
        print(f"The frontend should now display the WITB data.")
    else:
        print(f"\n✗ Database update failed!")


if __name__ == "__main__":
    main()