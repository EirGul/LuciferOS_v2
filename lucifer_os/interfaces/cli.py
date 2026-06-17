import sys

from lucifer_os.core.core import CoreRequest, LuciferCore
from lucifer_os.providers.ollama import OllamaProvider


def run_cli(args: list[str] | None = None) -> int:
    cli_args = list(args if args is not None else sys.argv[1:])

    provider_name = 'offline'

    if len(cli_args) >= 2 and cli_args[0] == '--provider':
        provider_name = cli_args[1].strip().lower()
        cli_args = cli_args[2:]

    text = ' '.join(cli_args).strip()

    if not text:
        print('Bruk: python -m lucifer_os.interfaces.cli --provider ollama <tekst>')
        return 1

    if provider_name == 'offline':
        core = LuciferCore()
    elif provider_name == 'ollama':
        core = LuciferCore(primary_provider=OllamaProvider())
    else:
        print(f'Ukjent provider: {provider_name}')
        return 2

    result = core.handle(CoreRequest(text=text))

    print(result.response.voice_summary)

    if result.response.visual_text != result.response.voice_summary:
        print()
        print(result.response.visual_text)

    return 0


def main() -> None:
    raise SystemExit(run_cli())


if __name__ == '__main__':
    main()
