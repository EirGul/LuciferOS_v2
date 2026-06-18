from lucifer_os.interfaces.api_adapter import ApiAdapter
from lucifer_os.interfaces.base import InterfaceAdapter
from lucifer_os.interfaces.cli_adapter import CliAdapter
from lucifer_os.interfaces.hud_adapter import HudAdapter
from lucifer_os.interfaces.voice_adapter import VoiceAdapter


def create_interface_adapter(
    name: str,
    project_root: str = '.',
    provider_name: str | None = None,
) -> InterfaceAdapter:
    interface_name = name.strip().lower()

    if interface_name == 'cli':
        return CliAdapter(project_root=project_root, provider_name=provider_name)

    if interface_name == 'api':
        return ApiAdapter(project_root=project_root, provider_name=provider_name)

    if interface_name == 'hud':
        return HudAdapter(project_root=project_root, provider_name=provider_name)

    if interface_name == 'voice':
        return VoiceAdapter(project_root=project_root, provider_name=provider_name)

    raise ValueError(f'Ukjent interface: {name}')
