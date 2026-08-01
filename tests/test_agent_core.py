"""Unit tests for Agent core behavior without live API calls."""

from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

from agents.agent import Agent, ModelConfig
from agents.tools.base import Tool


@dataclass
class FakeUsage:
    """Minimal usage object shape used by MessageHistory."""

    input_tokens: int
    output_tokens: int
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0


@dataclass
class FakeTextBlock:
    """Represents a text output block from the model."""

    text: str
    type: str = "text"


@dataclass
class FakeToolUseBlock:
    """Represents a tool call block from the model."""

    name: str
    input: dict[str, Any]
    id: str = "tool-1"
    type: str = "tool_use"


@dataclass
class FakeResponse:
    """Represents a model response payload."""

    content: list[Any]
    usage: FakeUsage


class FakeMessagesAPI:
    """Fake Anthropic messages API implementation."""

    def __init__(self, responses: list[FakeResponse]):
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if not self._responses:
            raise AssertionError("No fake responses remaining")
        return self._responses.pop(0)

    def count_tokens(self, **_kwargs):
        return SimpleNamespace(input_tokens=12)


class FakeAnthropicClient:
    """Fake client exposing the messages API."""

    def __init__(self, responses: list[FakeResponse]):
        self.messages = FakeMessagesAPI(responses)


class EchoTool(Tool):
    """Simple tool used to test tool call loops."""

    def __init__(self):
        super().__init__(
            name="echo",
            description="Echoes text",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                },
                "required": ["text"],
            },
        )

    async def execute(self, text: str) -> str:
        return f"echo:{text}"


def test_prepare_message_params_respects_overrides() -> None:
    """message_params should override defaults from ModelConfig."""
    client = FakeAnthropicClient(responses=[])
    agent = Agent(
        name="ParamAgent",
        system="Test system",
        config=ModelConfig(max_tokens=32, temperature=1.0),
        client=client,
        message_params={
            "max_tokens": 128,
            "temperature": 0.2,
            "top_k": 7,
        },
    )

    params = agent._prepare_message_params()

    assert params["max_tokens"] == 128
    assert params["temperature"] == 0.2
    assert params["top_k"] == 7
    assert params["messages"] == []


def test_agent_merges_default_and_custom_headers() -> None:
    """Default beta header should be merged with user extra headers."""
    response = FakeResponse(
        content=[FakeTextBlock(text="Done")],
        usage=FakeUsage(input_tokens=20, output_tokens=8),
    )
    client = FakeAnthropicClient(responses=[response])

    agent = Agent(
        name="HeaderAgent",
        system="Be concise.",
        client=client,
        message_params={
            "extra_headers": {"X-Test": "1"},
        },
    )

    final_response = agent.run("Hi")

    assert final_response.content[0].text == "Done"
    call = client.messages.calls[0]
    assert call["extra_headers"]["anthropic-beta"] == "code-execution-2025-05-22"
    assert call["extra_headers"]["X-Test"] == "1"


def test_agent_allows_custom_beta_header_override() -> None:
    """User-provided anthropic-beta header should override default value."""
    response = FakeResponse(
        content=[FakeTextBlock(text="Done")],
        usage=FakeUsage(input_tokens=20, output_tokens=8),
    )
    client = FakeAnthropicClient(responses=[response])

    agent = Agent(
        name="BetaOverrideAgent",
        system="Be concise.",
        client=client,
        message_params={
            "extra_headers": {"anthropic-beta": "files-api-2025-04-14"},
        },
    )

    agent.run("Hi")
    call = client.messages.calls[0]

    assert call["extra_headers"]["anthropic-beta"] == "files-api-2025-04-14"


def test_agent_executes_tool_and_completes_loop() -> None:
    """Agent should execute tool calls and continue until text output."""
    responses = [
        FakeResponse(
            content=[FakeToolUseBlock(name="echo", input={"text": "abc"})],
            usage=FakeUsage(input_tokens=25, output_tokens=5),
        ),
        FakeResponse(
            content=[FakeTextBlock(text="Finished")],
            usage=FakeUsage(input_tokens=35, output_tokens=5),
        ),
    ]
    client = FakeAnthropicClient(responses=responses)
    tool = EchoTool()

    agent = Agent(
        name="ToolAgent",
        system="Use tools when needed.",
        tools=[tool],
        client=client,
    )

    final_response = agent.run("Start")

    assert final_response.content[0].text == "Finished"
    assert len(client.messages.calls) == 2
    assert client.messages.calls[0]["tools"][0]["name"] == "echo"

    tool_result_message = agent.history.messages[2]
    assert tool_result_message["role"] == "user"
    assert tool_result_message["content"][0]["type"] == "tool_result"
    assert tool_result_message["content"][0]["content"] == "echo:abc"
