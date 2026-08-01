"""Tests for message history token tracking and formatting."""

from types import SimpleNamespace

import pytest

from agents.utils.history_util import MessageHistory


class FakeMessagesAPI:
    """Fake token counting endpoint."""

    @staticmethod
    def count_tokens(**_kwargs):
        return SimpleNamespace(input_tokens=6)


class FakeClient:
    """Fake client exposing messages API."""

    def __init__(self):
        self.messages = FakeMessagesAPI()


@pytest.mark.asyncio
async def test_add_message_tracks_usage_tokens() -> None:
    """Assistant messages with usage should update token counters."""
    history = MessageHistory(
        model="fake",
        system="System prompt",
        context_window_tokens=10_000,
        client=FakeClient(),
    )

    await history.add_message("user", "hello")
    usage = SimpleNamespace(
        input_tokens=25,
        output_tokens=8,
        cache_read_input_tokens=0,
        cache_creation_input_tokens=0,
    )
    await history.add_message("assistant", "hi", usage)

    assert len(history.messages) == 2
    assert len(history.message_tokens) == 1
    assert history.total_tokens > 0


@pytest.mark.asyncio
async def test_format_for_api_adds_ephemeral_cache_control() -> None:
    """Latest message blocks should include ephemeral cache control."""
    history = MessageHistory(
        model="fake",
        system="System prompt",
        context_window_tokens=10_000,
        client=FakeClient(),
        enable_caching=True,
    )

    await history.add_message("user", "hello")
    payload = history.format_for_api()

    assert payload[-1]["content"][0]["cache_control"]["type"] == "ephemeral"


@pytest.mark.asyncio
async def test_truncate_replaces_oldest_with_notice() -> None:
    """When tokens exceed context window, oldest turns should be truncated."""
    history = MessageHistory(
        model="fake",
        system="System prompt",
        context_window_tokens=30,
        client=FakeClient(),
    )

    await history.add_message("user", "first")
    await history.add_message(
        "assistant",
        "response one",
        SimpleNamespace(
            input_tokens=25,
            output_tokens=5,
            cache_read_input_tokens=0,
            cache_creation_input_tokens=0,
        ),
    )
    await history.add_message("user", "second")
    await history.add_message(
        "assistant",
        "response two",
        SimpleNamespace(
            input_tokens=45,
            output_tokens=5,
            cache_read_input_tokens=0,
            cache_creation_input_tokens=0,
        ),
    )

    history.truncate()

    assert history.total_tokens <= history.context_window_tokens
    if history.messages:
        assert (
            history.messages[0]["content"][0]["text"]
            == "[Earlier history has been truncated.]"
        )
