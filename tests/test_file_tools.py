"""Tests for local file operation tools."""

import pytest

from agents.tools.file_tools import FileReadTool, FileWriteTool


@pytest.mark.asyncio
async def test_write_then_read_roundtrip(tmp_path) -> None:
    """Write a file then read a subset of lines."""
    path = tmp_path / "notes.txt"
    writer = FileWriteTool()
    reader = FileReadTool()

    result = await writer.execute(
        operation="write",
        path=str(path),
        content="line1\nline2\n",
    )
    first_line = await reader.execute(
        operation="read",
        path=str(path),
        max_lines=1,
    )

    assert "Successfully wrote" in result
    assert first_line == "line1\n"


@pytest.mark.asyncio
async def test_edit_reports_missing_text(tmp_path) -> None:
    """Edit should fail when the target text is missing."""
    path = tmp_path / "edit.txt"
    path.write_text("alpha beta", encoding="utf-8")
    writer = FileWriteTool()

    result = await writer.execute(
        operation="edit",
        path=str(path),
        old_text="missing",
        new_text="x",
    )

    assert "not found" in result


@pytest.mark.asyncio
async def test_list_files_with_pattern(tmp_path) -> None:
    """List operation should return files matching a pattern."""
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.md").write_text("b", encoding="utf-8")
    reader = FileReadTool()

    result = await reader.execute(
        operation="list",
        path=str(tmp_path),
        pattern="*.txt",
    )

    assert "a.txt" in result
    assert "b.md" not in result
