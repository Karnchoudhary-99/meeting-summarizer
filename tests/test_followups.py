from datetime import date

from meeting_summarizer.actions import ActionItem
from meeting_summarizer.followups import group_by_owner, sort_by_due

REFERENCE = date(2026, 10, 19)  # Monday


def _action(task, owner=None, due=None):
    return ActionItem(task=task, owner=owner, due=due, speaker="Priya")


def test_group_by_owner_alphabetical_unassigned_last():
    actions = [
        _action("b task", owner="Sara"),
        _action("a task"),
        _action("c task", owner="Arjun"),
    ]
    groups = group_by_owner(actions)
    assert [name for name, _ in groups] == ["Arjun", "Sara", "Unassigned"]


def test_sort_by_due_dated_first_undated_last():
    actions = [
        _action("undated"),
        _action("friday task", due="friday"),
        _action("tomorrow task", due="tomorrow"),
    ]
    ordered = sort_by_due(actions, REFERENCE)
    assert [a.task for a in ordered] == [
        "tomorrow task",
        "friday task",
        "undated",
    ]
