#!/usr/bin/env python3
"""
WITB Data Models
Shared data structures for WITB scraping system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class WITBItem:
    """WITB Item following the schema structure from models.py"""
    category: str
    brand: str
    model: str
    loft: Optional[str] = None
    shaft: Optional[str] = None

@dataclass
class PlayerWITB:
    """Player with current WITB items."""
    name: str
    country: str
    tour: str
    ranking: int
    witb_items: List[WITBItem]
    source_url: str
    player_id: str
    last_updated: Optional[datetime] = None

@dataclass
class PlayerInfo:
    """Basic player information from database."""
    id: str
    name: str
    country: str
    tour: str
    ranking: int
    url: Optional[str] = None