import sys

from lucifer_os.runtime.app import LuciferApp


def run_cli(args: list[str] | None = None) -> int:
    cli_args = list(args if args is not None else sys.argv[1:])

    provider_name = None

    if len(cli_args) >= 2 and cli_args[0] == '--provider':
        provider_name = cli_args[1].strip().lower()
        cli_args = cli_args[2:]

    text = ' '.join(cli_args).strip()

    if not text:
        print('Bruk: python -m lucifer_os.interfaces.cli --provider ollama <tekst>')
        return 1

    try:
        app = LuciferApp(
            project_root='.',
            interface_name='cli',
            provider_name=provider_name,
        )
    except ValueError as error:
        print(str(error))
        return 2

    output = app.handle_text(text)

    print(output.voice_summary)

    if output.visual_text != output.voice_summary:
        print()
        print(output.visual_text)

    return 0


def main() -> None:
    raise SystemExit(run_cli())


if __name__ == '__main__':
    main()
