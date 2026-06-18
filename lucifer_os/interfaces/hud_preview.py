import sys

from lucifer_os.interfaces.hud_controller import HudController


def run_hud_preview(args: list[str] | None = None) -> int:
    cli_args = list(args if args is not None else sys.argv[1:])

    if not cli_args:
        print('Bruk: python -m lucifer_os.interfaces.hud_preview health|chat <tekst>')
        return 1

    command = cli_args[0].strip().lower()
    controller = HudController()

    try:
        if command == 'health':
            view = controller.health_view()
            print(f'online: {view.online}')
            print(f'status: {view.status_text}')
            print(f'provider: {view.provider_name}')
            print(f'adapter: {view.adapter_name}')
            return 0

        if command == 'chat':
            text = ' '.join(cli_args[1:]).strip()
            if not text:
                print('Bruk: python -m lucifer_os.interfaces.hud_preview chat <tekst>')
                return 1

            view = controller.send_text_view(text)
            print(f'voice: {view.voice_summary}')
            print(f'visual: {view.visual_text}')
            print(f'trace_id: {view.trace_id}')
            return 0

    except ConnectionError as error:
        print(str(error))
        return 2

    print(f'Ukjent HUD-preview kommando: {command}')
    return 1


def main() -> None:
    raise SystemExit(run_hud_preview())


if __name__ == '__main__':
    main()
