from lucifer_os.interfaces.base import InterfaceInput, InterfaceOutput
from lucifer_os.interfaces.factory import create_interface_adapter


class LuciferApp:
    def __init__(
        self,
        project_root: str = '.',
        interface_name: str = 'cli',
        provider_name: str | None = None,
    ):
        self.project_root = project_root
        self.interface_name = interface_name
        self.provider_name = provider_name
        self.adapter = create_interface_adapter(
            interface_name,
            project_root=project_root,
            provider_name=provider_name,
        )

    def handle_text(
        self,
        text: str,
        session_id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> InterfaceOutput:
        input_data = InterfaceInput(
            text=text,
            interface=self.adapter.name,
            session_id=session_id,
            metadata=dict(metadata or {}),
        )

        return self.adapter.handle_input(input_data)

    def status(self) -> InterfaceOutput:
        return self.handle_text('status')

    def health(self) -> dict[str, str | bool | None]:
        return {
            'app_ready': True,
            'project_root': self.project_root,
            'interface_name': self.interface_name,
            'provider_name': self.provider_name,
            'adapter_name': self.adapter.name,
        }
