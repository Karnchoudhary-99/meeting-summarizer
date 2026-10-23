"""Follow-up lists: action items grouped by owner.

Grouping order is alphabetical by owner, with "Unassigned" last, so a
minutes document reads as a clean per-person checklist. Within a group
items keep meeting order (callers may pre-sort by due date first).
"""

from __future__ import annotations

from datetime import date

from .actions import ActionItem
from .dates import resolve_due

_UNASSIGNED = "Unassigned"


def sort_by_due(
    actions: list[ActionItem], reference: date
) -> list[ActionItem]:
    """Sort dated actions first (earliest due first), undated last.

    Stable: actions sharing a due date keep meeting order, as do
    undated actions among themselves.
    """
    dated: list[tuple[date, int, ActionItem]] = []
    undated: list[ActionItem] = []
    for index, action in enumerate(actions):
        resolved = resolve_due(action.due, reference)
        if resolved is None:
            undated.append(action)
        else:
            dated.append((resolved, index, action))
    dated.sort(key=lambda item: (item[0], item[1]))
    return [action for _, _, action in dated] + undated


def group_by_owner(actions: list[ActionItem]) -> list[tuple[str, list[ActionItem]]]:
    """Group actions by owner; unassigned items form the last group."""
    groups: dict[str, list[ActionItem]] = {}
    for action in actions:
        groups.setdefault(action.owner or _UNASSIGNED, []).append(action)
    ordered = sorted((name for name in groups if name != _UNASSIGNED))
    if _UNASSIGNED in groups:
        ordered.append(_UNASSIGNED)
    return [(name, groups[name]) for name in ordered]
