"""Tests for parallel and error-handled tool execution."""

from dataclasses import dataclass

import pytest

from agents.utils.tool_util import execute_tools


@dataclass
class FakeCall:
    """Tool call payload used by execute_tools."""

    id: str
    name: str
    input: dict


class OkTool:
    """Tool that returns a deterministic value."""

    async def execute(self, **kwargs) -> str:
        return f"ok:{kwargs['value']}"


class FailingTool:
    """Tool that raises an exception."""

    async def execute(self, **_kwargs) -> str:
        raise RuntimeError("boom")


@pytest.mark.asyncio
async def test_execute_tools_parallel_success() -> None:
    """Parallel execution should return result per tool call."""
    calls = [
        FakeCall(id="1", name="ok", input={"value": "a"}),
        FakeCall(id="2", name="ok", input={"value": "b"}),
    ]

    results = await execute_tools(calls, tool_dict={"ok": OkTool()}, parallel=True)

    assert len(results) == 2
    assert results[0]["content"] == "ok:a"
    assert results[1]["content"] == "ok:b"


@pytest.mark.asyncio
async def test_execute_tools_missing_tool_marks_error() -> None:
    """Unknown tool names should produce an error response."""
    calls = [FakeCall(id="1", name="missing", input={})]

    results = await execute_tools(calls, tool_dict={}, parallel=False)

    assert results[0]["is_error"] is True
    assert "not found" in results[0]["content"]


@pytest.mark.asyncio
async def test_execute_tools_exception_marks_error() -> None:
    """Tool execution exceptions should be captured and reported."""
    calls = [FakeCall(id="1", name="broken", input={})]

    results = await execute_tools(
        calls,
        tool_dict={"broken": FailingTool()},
        parallel=False,
    )

    assert results[0]["is_error"] is True
    assert "Error executing tool" in results[0]["content"]
