from lucifer_os.memory import MemoryCommandParser, MemoryCommandType


def test_parser_parses_norwegian_quoted_correction_grammar():
    parser = MemoryCommandParser()

    command = parser.parse(
        'korriger minne "SQLite for memory" til "LuciferOS bruker SQLite som persistent memory store"'
    )

    assert command.type == MemoryCommandType.CORRECT
    assert command.query == "SQLite for memory"
    assert command.content == "LuciferOS bruker SQLite som persistent memory store"
    assert command.memory_id is None


def test_parser_parses_english_quoted_correction_grammar():
    parser = MemoryCommandParser()

    command = parser.parse(
        'correct memory "temporary preference" to "persistent project preference"'
    )

    assert command.type == MemoryCommandType.CORRECT
    assert command.query == "temporary preference"
    assert command.content == "persistent project preference"


def test_parser_quoted_correction_grammar_is_case_insensitive():
    parser = MemoryCommandParser()

    command = parser.parse(
        'KORRIGER MINNE "SQLite" TIL "Persistent SQLite store"'
    )

    assert command.type == MemoryCommandType.CORRECT
    assert command.query == "SQLite"
    assert command.content == "Persistent SQLite store"


def test_parser_keeps_legacy_correction_prefix_contract():
    parser = MemoryCommandParser()

    command = parser.parse("korriger minne LuciferOS skal bruke SQLite")

    assert command.type == MemoryCommandType.CORRECT
    assert command.content == "LuciferOS skal bruke SQLite"
    assert command.query is None


def test_parser_does_not_parse_incomplete_quoted_correction_as_target_and_replacement():
    parser = MemoryCommandParser()

    inputs = [
        'korriger minne "SQLite" til',
        'korriger minne SQLite til "Persistent SQLite store"',
        'correct memory "SQLite" to',
        'correct memory SQLite to "Persistent SQLite store"',
    ]

    for text in inputs:
        command = parser.parse(text)

        assert not (
            command.type == MemoryCommandType.CORRECT
            and command.query is not None
            and command.content is not None
        )


def test_parser_does_not_hijack_normal_conversation_with_correction_words():
    parser = MemoryCommandParser()

    inputs = [
        "kan du korrigere denne setningen for meg",
        "jeg vil rette opp i noe senere",
        "what does correct memory mean",
        "endre hvordan LuciferOS lærer over tid",
    ]

    for text in inputs:
        command = parser.parse(text)

        assert command.type == MemoryCommandType.NOT_MEMORY_COMMAND
