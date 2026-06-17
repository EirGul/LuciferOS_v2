import sys

from lucifer_os.core.config import ConfigLoader
from lucifer_os.core.core import CoreRequest, LuciferCore
from lucifer_os.providers.factory import create_provider


def run_cli(args: list[str] | None = None) -> int:
    cli_args = list(args if args is not None else sys.argv[1:])
    config = ConfigLoader(project_root='.').load()

    provider_name = config.default_provider

    if len(cli_args) >= 2 and cli_args[0] == '--provider':
        provider_name = cli_args[1].strip().lower()
        cli_args = cli_args[2:]

    text = ' '.join(cli_args).strip()

    if not text:
        print('Bruk: python -m lucifer_os.interfaces.cli --provider ollama <tekst>')
        return 1

    try:
        provider = create_provider(provider_name, config)
    except ValueError as error:
        print(str(error))
        return 2

    core = LuciferCore(primary_provider=provider, project_root='.')
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
