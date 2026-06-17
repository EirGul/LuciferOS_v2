from lucifer_os.registries.tool_registry import ToolMetadata
from lucifer_os.tools.base import Tool, ToolRequest, ToolResult


class GitStatusTool(Tool):
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name='git.status',
            capability='development',
            risk_level=1,
            requires_confirmation=False,
            supports_dry_run=True,
            platform_support=('windows', 'linux', 'darwin'),
        )

    def run(self, request: ToolRequest) -> ToolResult:
        if request.name != 'git.status':
            return ToolResult(
                success=False,
                message=f'Unsupported tool request: {request.name}',
                data={},
                dry_run=request.dry_run,
            )

        if request.dry_run:
            return ToolResult(
                success=True,
                message='Dry-run: would check Git repository status.',
                data={'command': 'git status'},
                dry_run=True,
            )

        return ToolResult(
            success=False,
            message='Real git status execution is not enabled yet.',
            data={},
            dry_run=False,
        )
