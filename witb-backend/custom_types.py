"""Branded types for type safety following CLAUDE.md C-5."""

from typing import NewType
from uuid import UUID

# Branded types for IDs
PlayerId = NewType("PlayerId", UUID)
WITBItemId = NewType("WITBItemId", UUID)
