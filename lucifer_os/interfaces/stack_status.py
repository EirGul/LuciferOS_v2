def build_stack_status() -> str:
    lines = [
        'LuciferOS stack status',
        '',
        'Core:',
        '  Direct CLI:',
        '    py -m lucifer_os.interfaces.cli "Hei Lucifer"',
        '',
        'API server:',
        '  Start:',
        '    start_lucifer_api.bat',
        '  Health check:',
        '    py -m lucifer_os.interfaces.cli --api-health',
        '  Chat through API:',
        '    py -m lucifer_os.interfaces.cli --api "Hei Lucifer"',
        '',
        'HUD preview:',
        '  Health:',
        '    py -m lucifer_os.interfaces.hud_preview health',
        '  Chat:',
        '    py -m lucifer_os.interfaces.hud_preview chat "Hei Lucifer"',
        '  Check script:',
        '    check_lucifer_hud_preview.bat',
        '',
        'Recommended development order:',
        '  1. py -m pytest',
        '  2. start_lucifer_api.bat',
        '  3. py -m lucifer_os.interfaces.cli --api-health',
        '  4. py -m lucifer_os.interfaces.hud_preview health',
    ]

    return '\n'.join(lines)


def main() -> None:
    print(build_stack_status())


if __name__ == '__main__':
    main()
