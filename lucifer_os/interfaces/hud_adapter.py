from lucifer_os.core.core import CoreRequest
from lucifer_os.core.factory import create_core
from lucifer_os.interfaces.base import InterfaceAdapter, InterfaceInput, InterfaceOutput, output_from_core_result


class HudAdapter(InterfaceAdapter):
    def __init__(self, project_root: str = '.', provider_name: str | None = None):
        self.project_root = project_root
        self.provider_name = provider_name
        self.core = create_core(project_root=project_root, provider_name=provider_name)

    @property
    def name(self) -> str:
        return 'hud'

    def handle_input(self, input_data: InterfaceInput) -> InterfaceOutput:
        result = self.core.handle(
            CoreRequest(
                text=input_data.text,
                interface='hud',
                session_id=input_data.session_id,
                metadata=input_data.metadata,
            )
        )

        return output_from_core_result(result)
