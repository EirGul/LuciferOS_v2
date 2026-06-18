import sys

from lucifer_os.interfaces.base import InterfaceInput
from lucifer_os.interfaces.factory import create_interface_adapter


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
        adapter = create_interface_adapter('cli', project_root='.', provider_name=provider_name)
    except ValueError as error:
        print(str(error))
        return 2

    output = adapter.handle_input(
        InterfaceInput(
            text=text,
            interface='cli',
        )
    )

    print(output.voice_summary)

    if output.visual_text != output.voice_summary:
        print()
        print(output.visual_text)

    return 0


def main() -> None:
    raise SystemExit(run_cli())


if __name__ == '__main__':
    main()
