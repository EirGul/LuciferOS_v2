import sys

from lucifer_os.core.core import CoreRequest, LuciferCore


def run_cli(args: list[str] | None = None) -> int:
    cli_args = args if args is not None else sys.argv[1:]
    text = ' '.join(cli_args).strip()

    if not text:
        print('Bruk: python -m lucifer_os.interfaces.cli "din tekst her"')
        return 1

    core = LuciferCore()
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
