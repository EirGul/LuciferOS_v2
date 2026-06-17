from lucifer_os.tools.base import ToolRequest, ToolResult
from lucifer_os.tools.dev import GitStatusTool


def test_git_status_tool_metadata():
    tool = GitStatusTool()
    metadata = tool.metadata()

    assert metadata.name == 'git.status'
    assert metadata.capability == 'development'
    assert metadata.risk_level == 1
    assert metadata.requires_confirmation is False
    assert metadata.supports_dry_run is True
    assert metadata.platform_support == ('windows', 'linux', 'darwin')


def test_git_status_tool_dry_run():
    tool = GitStatusTool()
    request = ToolRequest(name='git.status', dry_run=True)

    result = tool.run(request)

    assert isinstance(result, ToolResult)
    assert result.success is True
    assert result.dry_run is True
    assert result.data['command'] == 'git status'
    assert 'Dry-run' in result.message


def test_git_status_tool_rejects_wrong_request_name():
    tool = GitStatusTool()
    request = ToolRequest(name='wrong.tool', dry_run=True)

    result = tool.run(request)

    assert result.success is False
    assert result.dry_run is True
    assert 'Unsupported tool request' in result.message


def test_git_status_tool_real_execution_not_enabled_yet():
    tool = GitStatusTool()
    request = ToolRequest(name='git.status', dry_run=False)

    result = tool.run(request)

    assert result.success is False
    assert result.dry_run is False
    assert 'not enabled yet' in result.message
