import sys

from lucifer_os.core.config import ConfigLoader
from lucifer_os.core.core import CoreRequest, LuciferCore
from lucifer_os.providers.ollama import OllamaConfig, OllamaProvider


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

    if provider_name == 'offline':
        core = LuciferCore(project_root='.')
    elif provider_name == 'ollama':
        ollama_config = OllamaConfig(model=config.ollama_model)
        core = LuciferCore(primary_provider=OllamaProvider(config=ollama_config), project_root='.')
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
