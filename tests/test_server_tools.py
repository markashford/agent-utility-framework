"""Tests for Anthropic server tool schema wrappers."""

from agents.tools.code_execution import CodeExecutionServerTool
from agents.tools.web_search import WebSearchServerTool


def test_code_execution_tool_to_dict() -> None:
    """Code execution server tool should serialize required fields."""
    tool = CodeExecutionServerTool()

    payload = tool.to_dict()

    assert payload["type"] == "code_execution_20250522"
    assert payload["name"] == "code_execution"


def test_web_search_tool_to_dict_with_options() -> None:
    """Web search server tool should include optional fields when provided."""
    tool = WebSearchServerTool(
        max_uses=3,
        allowed_domains=["example.com"],
        blocked_domains=["blocked.test"],
        user_location={"country": "US"},
    )

    payload = tool.to_dict()

    assert payload["type"] == "web_search_20250305"
    assert payload["name"] == "web_search"
    assert payload["max_uses"] == 3
    assert payload["allowed_domains"] == ["example.com"]
    assert payload["blocked_domains"] == ["blocked.test"]
    assert payload["user_location"] == {"country": "US"}
