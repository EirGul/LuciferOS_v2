import pytest

from lucifer_os.memory import (
    MemoryCommandType,
    MemoryItem,
    MemoryResolutionPlan,
    MemoryResolutionPlanAction,
    MemoryResolutionPlanner,
    MemoryScope,
    MemoryTargetCandidate,
    MemoryTargetResolutionOutcome,
    MemoryTargetResolutionResult,
    MemoryType,
)


def make_memory(id="memory-1", content="LuciferOS bruker SQLite"):
    return MemoryItem(
        id=id,
        content=content,
        type=MemoryType.PREFERENCE,
        scope=MemoryScope.PROJECT,
        source="test",
    )


def test_resolution_plan_requires_explanation():
    with pytest.raises(ValueError, match="explanation"):
        MemoryResolutionPlan(
            action=MemoryResolutionPlanAction.REJECT,
            command_type=MemoryCommandType.DELETE,
            explanation="   ",
        )


def test_prepare_pending_plan_requires_selected_memory_id():
    with pytest.raises(ValueError, match="selected_memory_id"):
        MemoryResolutionPlan(
            action=MemoryResolutionPlanAction.PREPARE_PENDING_ACTION,
            command_type=MemoryCommandType.DELETE,
            explanation="prepare",
        )


def test_planner_rejects_non_correction_or_delete_commands():
    planner = MemoryResolutionPlanner()
    result = MemoryTargetResolutionResult(
        outcome=MemoryTargetResolutionOutcome.NO_MATCH,
        explanation="no match",
    )

    plan = planner.plan(MemoryCommandType.REMEMBER, result)

    assert plan.action == MemoryResolutionPlanAction.REJECT
    assert plan.command_type == MemoryCommandType.REMEMBER


def test_planner_rejects_no_match():
    planner = MemoryResolutionPlanner()
    result = MemoryTargetResolutionResult(
        outcome=MemoryTargetResolutionOutcome.NO_MATCH,
        explanation="no match",
    )

    plan = planner.plan(MemoryCommandType.DELETE, result)

    assert plan.action == MemoryResolutionPlanAction.REJECT
    assert plan.selected_memory_id is None


def test_planner_asks_user_to_choose_for_multiple_candidates():
    planner = MemoryResolutionPlanner()
    memory = make_memory()
    candidate = MemoryTargetCandidate(memory=memory, reason="match")
    result = MemoryTargetResolutionResult(
        outcome=MemoryTargetResolutionOutcome.MULTIPLE_CANDIDATES,
        explanation="multiple",
        candidates=(candidate,),
    )

    plan = planner.plan(MemoryCommandType.DELETE, result)

    assert plan.action == MemoryResolutionPlanAction.ASK_USER_TO_CHOOSE
    assert plan.candidates == (candidate,)
    assert plan.selected_memory_id is None


def test_planner_asks_user_to_choose_for_unsafe_ambiguous_match():
    planner = MemoryResolutionPlanner()
    result = MemoryTargetResolutionResult(
        outcome=MemoryTargetResolutionOutcome.UNSAFE_AMBIGUOUS_MATCH,
        explanation="unsafe",
    )

    plan = planner.plan(MemoryCommandType.CORRECT, result)

    assert plan.action == MemoryResolutionPlanAction.ASK_USER_TO_CHOOSE


def test_planner_prepares_pending_action_for_single_safe_match():
    planner = MemoryResolutionPlanner()
    memory = make_memory(id="memory-1")
    candidate = MemoryTargetCandidate(memory=memory, reason="match")
    result = MemoryTargetResolutionResult(
        outcome=MemoryTargetResolutionOutcome.SINGLE_SAFE_MATCH,
        explanation="single",
        candidates=(candidate,),
        selected_memory_id="memory-1",
        safe_for_confirmation=True,
    )

    plan = planner.plan(MemoryCommandType.CORRECT, result)

    assert plan.action == MemoryResolutionPlanAction.PREPARE_PENDING_ACTION
    assert plan.selected_memory_id == "memory-1"


def test_planner_prepares_pending_action_for_explicit_id_match():
    planner = MemoryResolutionPlanner()
    memory = make_memory(id="memory-1")
    candidate = MemoryTargetCandidate(memory=memory, reason="explicit")
    result = MemoryTargetResolutionResult(
        outcome=MemoryTargetResolutionOutcome.EXPLICIT_ID_MATCH,
        explanation="explicit",
        candidates=(candidate,),
        selected_memory_id="memory-1",
        safe_for_confirmation=True,
    )

    plan = planner.plan(MemoryCommandType.DELETE, result)

    assert plan.action == MemoryResolutionPlanAction.PREPARE_PENDING_ACTION
    assert plan.selected_memory_id == "memory-1"


def test_planner_rejects_safe_outcome_without_safe_confirmation_flag():
    planner = MemoryResolutionPlanner()
    memory = make_memory(id="memory-1")
    candidate = MemoryTargetCandidate(memory=memory, reason="match")
    result = MemoryTargetResolutionResult(
        outcome=MemoryTargetResolutionOutcome.SINGLE_SAFE_MATCH,
        explanation="single",
        candidates=(candidate,),
        selected_memory_id="memory-1",
        safe_for_confirmation=False,
    )

    plan = planner.plan(MemoryCommandType.DELETE, result)

    assert plan.action == MemoryResolutionPlanAction.REJECT


def test_resolution_planner_exports_are_public():
    import lucifer_os.memory as memory

    assert memory.MemoryResolutionPlan is MemoryResolutionPlan
    assert memory.MemoryResolutionPlanAction is MemoryResolutionPlanAction
    assert memory.MemoryResolutionPlanner is MemoryResolutionPlanner
