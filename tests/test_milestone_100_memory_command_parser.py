from lucifer_os.memory import MemoryCommandParser, MemoryCommandType


def test_memory_command_parser_parses_explicit_remember_commands():
    parser = MemoryCommandParser()

    command = parser.parse("husk at LuciferOS skal være lokal først")

    assert command.type == MemoryCommandType.REMEMBER
    assert command.content == "LuciferOS skal være lokal først"


def test_memory_command_parser_parses_english_remember_commands():
    parser = MemoryCommandParser()

    command = parser.parse("remember that memory must be explicit")

    assert command.type == MemoryCommandType.REMEMBER
    assert command.content == "memory must be explicit"


def test_memory_command_parser_parses_list_memory_commands():
    parser = MemoryCommandParser()

    assert parser.parse("hva husker du").type == MemoryCommandType.LIST
    assert parser.parse("vis minner").type == MemoryCommandType.LIST


def test_memory_command_parser_parses_search_memory_commands():
    parser = MemoryCommandParser()

    command = parser.parse("hva husker du om LuciferOS")

    assert command.type == MemoryCommandType.SEARCH
    assert command.query == "LuciferOS"


def test_memory_command_parser_parses_correct_memory_commands():
    parser = MemoryCommandParser()

    command = parser.parse("korriger minne LuciferOS skal bruke SQLite")

    assert command.type == MemoryCommandType.CORRECT
    assert command.content == "LuciferOS skal bruke SQLite"


def test_memory_command_parser_parses_delete_memory_commands():
    parser = MemoryCommandParser()

    command = parser.parse("glem at LuciferOS bruker midlertidig JSON")

    assert command.type == MemoryCommandType.DELETE
    assert command.query == "LuciferOS bruker midlertidig JSON"


def test_memory_command_parser_parses_policy_and_confirmation_commands():
    parser = MemoryCommandParser()

    assert parser.parse("forklar minnepolicy").type == MemoryCommandType.EXPLAIN_POLICY
    assert parser.parse("bekreft").type == MemoryCommandType.CONFIRM_PENDING
    assert parser.parse("avbryt").type == MemoryCommandType.CANCEL_PENDING


def test_memory_command_parser_does_not_hijack_normal_conversation():
    parser = MemoryCommandParser()

    normal_inputs = [
        "hva vil du lære etter hvert",
        "jeg husker ikke hva vi gjorde",
        "kan du forklare hva glem betyr",
        "læring er viktig for LuciferOS",
        "fortell meg om memory architecture",
    ]

    for text in normal_inputs:
        command = parser.parse(text)
        assert command.type == MemoryCommandType.NOT_MEMORY_COMMAND


def test_memory_command_parser_returns_not_memory_command_for_empty_input():
    parser = MemoryCommandParser()

    command = parser.parse("   ")

    assert command.type == MemoryCommandType.NOT_MEMORY_COMMAND
    assert command.normalized_text == ""


def test_memory_command_parser_is_public_memory_export():
    import lucifer_os.memory as memory

    assert memory.MemoryCommandParser is MemoryCommandParser
    assert memory.MemoryCommandType is MemoryCommandType
