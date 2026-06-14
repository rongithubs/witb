"""Pure diff algorithm for weekly WITB bag changes following CLAUDE.md C-4.

This module is intentionally free of database/ORM dependencies so the diff core
can be unit-tested in isolation (CLAUDE.md T-3, T-5). Callers map the resulting
``BagChange`` values onto persisted change records.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

# Categories that hold exactly one club; an add+remove within one of these is
# really a single swap and is coalesced into a SWITCHED event.
SINGLE_SLOT_CATEGORIES = frozenset({"driver", "putter", "ball"})


def normalize_category(category: str) -> str:
    """Canonicalize a club category for diffing: lowercased, trimmed, de-pluralized.

    The current scraper emits singular categories (Iron, Wedge, Grip) while
    historical stored data used plurals (Irons, Wedges, Grips). Collapsing a
    trailing "s" keeps a re-scrape from surfacing phantom add/remove pairs.
    No real golf category is singular and ends in "s", so this is safe here.
    """
    normalized = category.strip().lower()
    return normalized[:-1] if normalized.endswith("s") else normalized


class ChangeType(str, Enum):
    """Kind of bag change detected between two scrapes."""

    ADDED = "added"
    REMOVED = "removed"
    SWITCHED = "switched"


@dataclass(frozen=True)
class BagItem:
    """A single club/ball in a player's bag, used as diff input.

    Equality is structural (frozen dataclass), which lets tests compare results
    directly and lets us derive set membership from the identity key.
    """

    category: str
    brand: str
    model: str
    loft: str | None = None
    shaft: str | None = None

    def identity(self) -> tuple[str, str, str]:
        """v1 identity key: category/brand/model, normalized for case and plurality."""
        return (
            normalize_category(self.category),
            self.brand.strip().lower(),
            self.model.strip().lower(),
        )


@dataclass(frozen=True)
class BagChange:
    """A single detected change between an old and new bag."""

    change_type: ChangeType
    old: BagItem | None
    new: BagItem | None

    @property
    def category(self) -> str:
        """Category the change belongs to, taken from whichever side is present."""
        item = self.new or self.old
        assert item is not None, "BagChange must have an old or new item"
        return item.category


def _is_single_slot(category: str) -> bool:
    return normalize_category(category) in SINGLE_SLOT_CATEGORIES


def compute_bag_changes(
    old_items: Sequence[BagItem], new_items: Sequence[BagItem]
) -> list[BagChange]:
    """Diff two bags into a list of add/remove/switch events.

    v1 keys items by (category, brand, model): an item only in ``new_items`` is
    ADDED, one only in ``old_items`` is REMOVED, and an add+remove sharing a
    single-slot category (Driver/Putter/Ball) is coalesced into one SWITCHED
    event. Order is deterministic: switched/added in ``new_items`` order, then
    any remaining removed in ``old_items`` order.
    """
    old_by_key = {item.identity(): item for item in old_items}
    new_by_key = {item.identity(): item for item in new_items}

    added = [item for item in new_items if item.identity() not in old_by_key]
    removed = [item for item in old_items if item.identity() not in new_by_key]

    changes: list[BagChange] = []
    unmatched_removed = list(removed)

    for new_item in added:
        swap_target = _find_single_slot_swap(new_item, unmatched_removed)
        if swap_target is not None:
            unmatched_removed.remove(swap_target)
            changes.append(
                BagChange(ChangeType.SWITCHED, old=swap_target, new=new_item)
            )
        else:
            changes.append(BagChange(ChangeType.ADDED, old=None, new=new_item))

    changes.extend(
        BagChange(ChangeType.REMOVED, old=item, new=None) for item in unmatched_removed
    )

    return changes


def _find_single_slot_swap(
    new_item: BagItem, candidates: list[BagItem]
) -> BagItem | None:
    """Return a removed item that pairs with ``new_item`` as a single-slot swap."""
    if not _is_single_slot(new_item.category):
        return None
    new_category = normalize_category(new_item.category)
    return next(
        (
            item
            for item in candidates
            if normalize_category(item.category) == new_category
        ),
        None,
    )
