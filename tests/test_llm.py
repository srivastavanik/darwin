"""Tests for LLM wrapper: retry, fallback, cost tracking (mocked)."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from markov.llm import LLMResponse, call_llm, get_cost_summary, reset_costs


@pytest.fixture(autouse=True)
def clean_costs():
    """Reset cost tracker before each test."""
    reset_costs()
    yield
    reset_costs()


def _mock_response(text: str = "hello", prompt_tok: int = 10, completion_tok: int = 5):
    """Build a mock LiteLLM response object."""
    resp = MagicMock()
    resp.choices = [MagicMock()]
    resp.choices[0].message.content = text
    resp.usage = MagicMock()
    resp.usage.prompt_tokens = prompt_tok
    resp.usage.completion_tokens = completion_tok
    return resp


class TestCallLLM:
    @pytest.mark.asyncio
    async def test_successful_call(self):
        mock_resp = _mock_response("test output", 100, 50)
        with patch("markov.llm.litellm.acompletion", new_callable=AsyncMock, return_value=mock_resp):
            result = await call_llm("test-model", "system", "user")
            assert result.text == "test output"
            assert result.prompt_tokens == 100
            assert result.completion_tokens == 50
            assert not result.failed

    @pytest.mark.asyncio
    async def test_retry_on_first_failure(self):
        mock_resp = _mock_response("retry output")
        call_count = 0

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise TimeoutError("timeout")
            return mock_resp

        with patch("markov.llm.litellm.acompletion", new_callable=AsyncMock, side_effect=side_effect):
            result = await call_llm("test-model", "system", "user")
            assert result.text == "retry output"
            assert call_count == 2
            assert not result.failed

    @pytest.mark.asyncio
    async def test_fallback_on_total_failure(self):
        async def fail(*args, **kwargs):
            raise RuntimeError("boom")

        with patch("markov.llm.litellm.acompletion", new_callable=AsyncMock, side_effect=fail):
            result = await call_llm("test-model", "system", "user", fallback="fallback_text")
            assert result.text == "fallback_text"
            assert result.failed

    @pytest.mark.asyncio
    async def test_cost_accumulation(self):
        mock1 = _mock_response("a", 100, 50)
        mock2 = _mock_response("b", 200, 100)

        with patch("markov.llm.litellm.acompletion", new_callable=AsyncMock) as mock_fn:
            mock_fn.side_effect = [mock1, mock2]
            await call_llm("model-a", "s", "u")
            await call_llm("model-b", "s", "u")

            summary = get_cost_summary()
            assert summary["total_calls"] == 2
            assert summary["total_prompt_tokens"] == 300
            assert summary["total_completion_tokens"] == 150
            assert summary["total_tokens"] == 450

    @pytest.mark.asyncio
    async def test_failure_counted(self):
        async def fail(*args, **kwargs):
            raise RuntimeError("boom")

        with patch("markov.llm.litellm.acompletion", new_callable=AsyncMock, side_effect=fail):
            await call_llm("test-model", "s", "u")
            summary = get_cost_summary()
            assert summary["total_failures"] == 1

    @pytest.mark.asyncio
    async def test_reset_costs(self):
        mock_resp = _mock_response("x", 50, 25)
        with patch("markov.llm.litellm.acompletion", new_callable=AsyncMock, return_value=mock_resp):
            await call_llm("m", "s", "u")
            assert get_cost_summary()["total_calls"] == 1
            reset_costs()
            assert get_cost_summary()["total_calls"] == 0
