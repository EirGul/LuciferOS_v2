from lucifer_os.memory import (
    MemoryDeleteRequest,
    MemoryPolicy,
    MemoryScope,
    MemoryType,
    MemoryWriteRequest,
)


def test_memory_policy_rejects_empty_write_content():
    policy = MemoryPolicy()

    decision = policy.evaluate_write(
        MemoryWriteRequest(
            content='   ',
            type=MemoryType.FACT,
            scope=MemoryScope.PROJECT,
        )
    )

    assert decision.allowed is False
    assert decision.requires_confirmation is False
    assert 'empty content' in decision.audit_reason


def test_memory_policy_allows_low_impact_project_memory_without_confirmation():
    policy = MemoryPolicy()

    decision = policy.evaluate_write(
        MemoryWriteRequest(
            content='LuciferOS has stable API and HUD foundations.',
            type=MemoryType.PROJECT_STATE,
            scope=MemoryScope.PROJECT,
        )
    )

    assert decision.allowed is True
    assert decision.requires_confirmation is False
    assert decision.audit_reason == 'Memory write allowed.'


def test_memory_policy_requires_confirmation_for_global_memory():
    policy = MemoryPolicy()

    decision = policy.evaluate_write(
        MemoryWriteRequest(
            content='User prefers short technical instructions.',
            type=MemoryType.PREFERENCE,
            scope=MemoryScope.GLOBAL,
        )
    )

    assert decision.allowed is True
    assert decision.requires_confirmation is True
    assert 'requires confirmation' in decision.audit_reason


def test_memory_policy_requires_confirmation_for_user_instruction():
    policy = MemoryPolicy()

    decision = policy.evaluate_write(
        MemoryWriteRequest(
            content='Always keep LuciferOS local-first.',
            type=MemoryType.USER_INSTRUCTION,
            scope=MemoryScope.PROJECT,
        )
    )

    assert decision.allowed is True
    assert decision.requires_confirmation is True
    assert 'high-impact type or scope' in decision.audit_reason


def test_memory_policy_rejects_empty_delete_id():
    policy = MemoryPolicy()

    decision = policy.evaluate_delete(MemoryDeleteRequest(memory_id='   '))

    assert decision.allowed is False
    assert decision.requires_confirmation is False
    assert 'empty memory id' in decision.audit_reason


def test_memory_policy_requires_confirmation_for_delete():
    policy = MemoryPolicy()

    decision = policy.evaluate_delete(MemoryDeleteRequest(memory_id='memory-123'))

    assert decision.allowed is True
    assert decision.requires_confirmation is True
    assert 'requires confirmation' in decision.audit_reason
