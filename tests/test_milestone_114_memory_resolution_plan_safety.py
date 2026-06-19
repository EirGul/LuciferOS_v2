from lucifer_os.memory import (
    MemoryCommandType,
    MemoryItem,
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


def make_candidate(memory=None):
    return MemoryTargetCandidate(
        memory=memory or make_memory(),
        reason="test match",
        score=1.0,
    )


def test_no_match_never_prepares_pending_action_for_correct_or_delete():
    planner = MemoryResolutionPlanner()
    resolution = MemoryTargetResolutionResult(
        outcome=MemoryTargetResolutionOutcome.NO_MATCH,
        explanation="no match",
    )

    for command_type in (MemoryCommandType.CORRECT, MemoryCommandType.DELETE):
        plan = planner.plan(command_type, resolution)

        assert plan.action == MemoryResolutionPlanAction.REJECT
        assert plan.selected_memory_id is None


def test_multiple_candidates_never_prepare_pending_action():
    planner = MemoryResolutionPlanner()
    candidate = make_candidate()
    resolution = MemoryTargetResolutionResult(
        outcome=MemoryTargetResolutionOutcome.MULTIPLE_CANDIDATES,
        explanation="multiple",
        candidates=(candidate,),
    )

    plan = planner.plan(MemoryCommandType.DELETE, resolution)

    assert plan.action == MemoryResolutionPlanAction.ASK_USER_TO_CHOOSE
    assert plan.selected_memory_id is None
    assert plan.candidates == (candidate,)


def test_unsafe_ambiguous_match_never_prepares_pending_action():
    planner = MemoryResolutionPlanner()
    candidate = make_candidate()
    resolution = MemoryTargetResolutionResult(
        outcome=MemoryTargetResolutionOutcome.UNSAFE_AMBIGUOUS_MATCH,
        explanation="unsafe",
        candidates=(candidate,),
    )

    plan = planner.plan(MemoryCommandType.CORRECT, resolution)

    assert plan.action == MemoryResolutionPlanAction.ASK_USER_TO_CHOOSE
    assert plan.selected_memory_id is None
    assert plan.candidates == (candidate,)


def test_only_correct_and_delete_can_use_resolution_planner():
    planner = MemoryResolutionPlanner()
    candidate = make_candidate()
    resolution = MemoryTargetResolutionResult(
        outcome=MemoryTargetResolutionOutcome.SINGLE_SAFE_MATCH,
        explanation="single",
        candidates=(candidate,),
        selected_memory_id=candidate.memory.id,
        safe_for_confirmation=True,
    )

    disallowed = [
        MemoryCommandType.REMEMBER,
        MemoryCommandType.LIST,
        MemoryCommandType.SEARCH,
        MemoryCommandType.EXPLAIN_POLICY,
        MemoryCommandType.CONFIRM_PENDING,
        MemoryCommandType.CANCEL_PENDING,
        MemoryCommandType.NOT_MEMORY_COMMAND,
    ]

    for command_type in disallowed:
        plan = planner.plan(command_type, resolution)

        assert plan.action == MemoryResolutionPlanAction.REJECT
        assert plan.selected_memory_id is None


def test_safe_outcome_without_selected_memory_id_is_rejected_by_result_invariant():
    try:
        MemoryTargetResolutionResult(
            outcome=MemoryTargetResolutionOutcome.SINGLE_SAFE_MATCH,
            explanation="invalid",
            safe_for_confirmation=True,
        )
    except ValueError as exc:
        assert "selected_memory_id" in str(exc)
    else:
        raise AssertionError("Expected result invariant to reject missing selected_memory_id.")


def test_single_safe_match_not_marked_safe_is_rejected_by_planner():
    planner = MemoryResolutionPlanner()
    candidate = make_candidate()
    resolution = MemoryTargetResolutionResult(
        outcome=MemoryTargetResolutionOutcome.SINGLE_SAFE_MATCH,
        explanation="single but unsafe",
        candidates=(candidate,),
        selected_memory_id=candidate.memory.id,
        safe_for_confirmation=False,
    )

    plan = planner.plan(MemoryCommandType.DELETE, resolution)

    assert plan.action == MemoryResolutionPlanAction.REJECT
    assert plan.selected_memory_id is None


def test_planner_preserves_candidates_without_mutation():
    planner = MemoryResolutionPlanner()
    memory = make_memory(id="memory-1", content="LuciferOS bruker SQLite")
    candidate = make_candidate(memory)
    resolution = MemoryTargetResolutionResult(
        outcome=MemoryTargetResolutionOutcome.MULTIPLE_CANDIDATES,
        explanation="multiple",
        candidates=(candidate,),
    )

    before_memory = memory
    before_candidate = candidate

    plan = planner.plan(MemoryCommandType.DELETE, resolution)

    assert plan.candidates == (before_candidate,)
    assert plan.candidates[0].memory == before_memory
    assert memory == before_memory


def test_prepare_pending_action_plan_contains_no_operation_side_effects():
    planner = MemoryResolutionPlanner()
    candidate = make_candidate()
    resolution = MemoryTargetResolutionResult(
        outcome=MemoryTargetResolutionOutcome.EXPLICIT_ID_MATCH,
        explanation="explicit",
        candidates=(candidate,),
        selected_memory_id=candidate.memory.id,
        safe_for_confirmation=True,
    )

    plan = planner.plan(MemoryCommandType.CORRECT, resolution)

    assert plan.action == MemoryResolutionPlanAction.PREPARE_PENDING_ACTION
    assert plan.selected_memory_id == candidate.memory.id
    assert not hasattr(plan, "operation_result")
    assert not hasattr(plan, "pending_action")
