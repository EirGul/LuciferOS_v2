VALID_RESPONSE_CHANNELS = {'cli', 'voice', 'hud', 'api'}


def normalize_response_channel(interface: str) -> str:
    normalized = interface.strip().lower()

    if normalized in VALID_RESPONSE_CHANNELS:
        return normalized

    return 'cli'
