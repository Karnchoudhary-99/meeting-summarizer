"""Follow-up lists: action items grouped by owner.

Grouping order is alphabetical by owner, with "Unassigned" last, so a
minutes document reads as a clean per-person checklist. Within a group
items keep meeting order (callers may pre-sort by due date first).
"""

from __future__ import annotations

from .actions import ActionItem

_UNASSIGNED = "Unassigned"


def group_by_owner(actions: list[ActionItem]) -> list[tuple[str, list[ActionItem]]]:
    """Group actions by owner; unassigned items form the last group."""
    groups: dict[str, list[ActionItem]] = {}
    for action in actions:
        groups.setdefault(action.owner or _UNASSIGNED, []).append(action)
    ordered = sorted((name for name in groups if name != _UNASSIGNED))
    if _UNASSIGNED in groups:
        ordered.append(_UNASSIGNED)
    return [(name, groups[name]) for name in ordered]
