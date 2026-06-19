# Memory Correction Command Grammar Design

## Milestone 115 status

Milestone 115 is design-only.

It must not modify MemoryCommandParser, MemoryCommandExecutor, IntentRouter, Core, API, HUD, provider prompts, voice, tools, or runtime adapters.

## Purpose

Correction commands need both a target memory query and replacement content.

The existing correction parser shape has only one content field and cannot safely infer both values from ordinary text.

Correction target resolution must not guess.

## Canonical correction grammar

The canonical Norwegian correction command is:

`korriger minne "<target>" til "<replacement>"`

The canonical English correction command is:

`correct memory "<target>" to "<replacement>"`

## Parsed command fields

A valid correction command must produce:

- type = CORRECT
- query = target text
- content = replacement text
- memory_id = None unless an explicit id syntax is added later

## Examples

Input:

`korriger minne "SQLite for memory" til "LuciferOS bruker SQLite som persistent memory store"`

Output:

- query = SQLite for memory
- content = LuciferOS bruker SQLite som persistent memory store

Input:

`correct memory "temporary preference" to "persistent project preference"`

Output:

- query = temporary preference
- content = persistent project preference

## Invalid correction commands

The parser must reject correction commands when:

- target text is missing
- replacement text is missing
- the separator `til` or `to` is missing
- quotation boundaries are missing or malformed
- normal conversation merely contains words such as korriger, rett, endre, correct or memory

## Safety rules

- Parser output must never guess a target memory id.
- Parser output must not create a pending action.
- Parser output must not update memory.
- Parser output must not delete memory.
- Resolver and executor remain responsible for target resolution and confirmation.
- Normal conversation must remain not_memory_command unless it matches the explicit grammar.

## Compatibility rule

Existing correction prefixes remain unsupported for execution until the explicit target-plus-replacement grammar is implemented and tested.

## Non-goals

Milestone 115 must not add:

- parser implementation
- executor integration
- resolver integration
- pending-action creation
- Core integration
- API endpoints
- HUD memory panels
- provider prompt injection
- automatic memory extraction
- semantic/vector search
- OS/tool actions
- voice integration

## Next milestone direction

The next safe step is to implement the explicit correction grammar in MemoryCommandParser with parser-only tests.

Executor integration must wait until parser output is proven to contain both query and replacement content.
