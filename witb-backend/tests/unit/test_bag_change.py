"""Unit tests for the bag-change diff algorithm following CLAUDE.md T-1, T-5."""

from services.bag_change import (
    BagChange,
    BagItem,
    ChangeType,
    compute_bag_changes,
)


def _driver(
    model: str, *, loft: str | None = None, shaft: str | None = None
) -> BagItem:
    """Build a Driver BagItem with a fixed brand for switch/add/remove cases."""
    return BagItem(
        category="Driver", brand="TaylorMade", model=model, loft=loft, shaft=shaft
    )


class TestComputeBagChanges:
    """Unit tests for compute_bag_changes."""

    def test_identical_bags_produce_no_changes(self):
        """An unchanged bag yields an empty change list."""
        bag = [_driver("Qi10"), BagItem("Putter", "Scotty Cameron", "Newport 2")]

        result = compute_bag_changes(bag, bag)

        assert result == []

    def test_new_item_in_multislot_category_is_added(self):
        """An item present only in the new bag is reported as added."""
        wedge = BagItem("Wedge", "Titleist", "Vokey SM10", loft="56")
        old = [_driver("Qi10")]
        new = [_driver("Qi10"), wedge]

        result = compute_bag_changes(old, new)

        assert result == [BagChange(ChangeType.ADDED, old=None, new=wedge)]

    def test_missing_item_in_multislot_category_is_removed(self):
        """An item present only in the old bag is reported as removed."""
        wedge = BagItem("Wedge", "Titleist", "Vokey SM10", loft="56")
        old = [_driver("Qi10"), wedge]
        new = [_driver("Qi10")]

        result = compute_bag_changes(old, new)

        assert result == [BagChange(ChangeType.REMOVED, old=wedge, new=None)]

    def test_single_slot_replacement_coalesces_into_switched(self):
        """A driver swap in the single-slot Driver category becomes one switched event."""
        previous = _driver("Stealth 2", loft="9", shaft="Ventus Black")
        current = _driver("Qi10", loft="10.5", shaft="Ventus Blue")

        result = compute_bag_changes([previous], [current])

        assert result == [BagChange(ChangeType.SWITCHED, old=previous, new=current)]

    def test_multislot_add_and_remove_do_not_coalesce(self):
        """Add and remove across different multi-slot categories stay separate events."""
        removed_iron = BagItem("Iron", "Titleist", "T100")
        added_wedge = BagItem("Wedge", "Titleist", "Vokey SM10", loft="56")

        result = compute_bag_changes([removed_iron], [added_wedge])

        assert result == [
            BagChange(ChangeType.ADDED, old=None, new=added_wedge),
            BagChange(ChangeType.REMOVED, old=removed_iron, new=None),
        ]

    def test_first_scrape_reports_every_item_as_added(self):
        """With no prior bag, every new item is an add (caller decides to suppress)."""
        driver = _driver("Qi10")
        putter = BagItem("Putter", "Scotty Cameron", "Newport 2")

        result = compute_bag_changes([], [driver, putter])

        assert result == [
            BagChange(ChangeType.ADDED, old=None, new=driver),
            BagChange(ChangeType.ADDED, old=None, new=putter),
        ]

    def test_key_matching_ignores_case_and_surrounding_whitespace(self):
        """Same club with differing case/whitespace is treated as unchanged."""
        old = [BagItem("Driver", "TaylorMade", "Qi10")]
        new = [BagItem(" driver ", " TaylorMade ", " Qi10 ")]

        result = compute_bag_changes(old, new)

        assert result == []
