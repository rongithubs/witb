#!/usr/bin/env python3
"""
Database Updater Module
Handles updating the database with scraped WITB data.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List

from sqlalchemy import text

from db_session import SessionLocal
from witb_models import PlayerWITB


class DatabaseUpdater:
    def update_player_witb(self, player_witb: PlayerWITB) -> bool:
        try:
            with SessionLocal() as session:
                session.execute(
                    text("DELETE FROM witb_items WHERE player_id = :pid"),
                    {"pid": player_witb.player_id},
                )

                update_date = player_witb.last_updated or datetime.now()

                for item in player_witb.witb_items:
                    session.execute(
                        text("""
                            INSERT INTO witb_items
                                (id, player_id, category, brand, model, loft, shaft, last_updated)
                            VALUES
                                (:id, :pid, :category, :brand, :model, :loft, :shaft, :last_updated)
                        """),
                        {
                            "id": str(uuid.uuid4()),
                            "pid": player_witb.player_id,
                            "category": item.category,
                            "brand": item.brand,
                            "model": item.model,
                            "loft": item.loft,
                            "shaft": item.shaft,
                            "last_updated": update_date,
                        },
                    )

                session.execute(
                    text("UPDATE players SET last_updated = :ts WHERE id = :pid"),
                    {"ts": update_date, "pid": player_witb.player_id},
                )
                session.commit()
            return True
        except Exception as e:
            print(f"Database error for {player_witb.name}: {e}")
            return False

    def update_all_players(self, players_witb: List[PlayerWITB], verbose: bool = True) -> int:
        if not players_witb:
            return 0

        if verbose:
            print(f"Updating database with {len(players_witb)} players...")

        success_count = sum(
            1 for player_witb in players_witb if self.update_player_witb(player_witb)
        )

        if verbose:
            print(f"Successfully updated {success_count}/{len(players_witb)} players in database")

        return success_count

    def save_to_json(self, players_witb: List[PlayerWITB], filename: str = "witb_data.json") -> bool:
        try:
            output_data = [
                {
                    "name": player.name,
                    "country": player.country,
                    "tour": player.tour,
                    "ranking": player.ranking,
                    "player_id": player.player_id,
                    "source_url": player.source_url,
                    "witb_items": [
                        {
                            "category": item.category,
                            "brand": item.brand,
                            "model": item.model,
                            "loft": item.loft,
                            "shaft": item.shaft,
                        }
                        for item in player.witb_items
                    ],
                }
                for player in players_witb
            ]
            with open(filename, "w") as f:
                json.dump(output_data, f, indent=2)
            print(f"Results saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False

    def get_database_summary(self, verbose: bool = True) -> Dict:
        try:
            with SessionLocal() as session:
                result = session.execute(text("""
                    SELECT p.name, p.ranking, COUNT(w.id) as witb_count
                    FROM players p
                    LEFT JOIN witb_items w ON p.id = w.player_id
                    WHERE p.ranking <= 50
                    GROUP BY p.id, p.name, p.ranking
                    ORDER BY p.ranking
                """))
                rows = result.fetchall()

            total_players = len(rows)
            players_with_witb = sum(1 for r in rows if r.witb_count > 0)
            total_items = sum(r.witb_count for r in rows)

            summary = {
                "total_players": total_players,
                "players_with_witb": players_with_witb,
                "total_witb_items": total_items,
                "coverage_percentage": (players_with_witb / total_players * 100) if total_players > 0 else 0,
            }

            if verbose:
                print(f"\nDatabase Summary:")
                print("=" * 40)
                print(f"Total players in top 50: {total_players}")
                print(f"Players with WITB data: {players_with_witb}")
                print(f"Total WITB items: {total_items}")
                print(f"Coverage: {summary['coverage_percentage']:.1f}%")
                print(f"\nTop 10 Players:")
                for row in rows[:10]:
                    print(f"  {row.ranking:2d}. {row.name:<25} - {row.witb_count} items")

            return summary
        except Exception as e:
            print(f"Database error: {e}")
            return {}

    def print_summary(self, players_witb: List[PlayerWITB]):
        total_items = sum(len(p.witb_items) for p in players_witb)
        print(f"\n{'=' * 60}")
        print("SCRAPING SUMMARY")
        print("=" * 60)
        print(f"Players with WITB data: {len(players_witb)}")
        print(f"Total WITB items: {total_items}")
        if players_witb:
            print(f"Average items per player: {total_items / len(players_witb):.1f}")
        print(f"\nTop 10 Players:")
        for player in sorted(players_witb, key=lambda p: p.ranking)[:10]:
            print(f"  {player.ranking:2d}. {player.name:<25} - {len(player.witb_items)} items")
