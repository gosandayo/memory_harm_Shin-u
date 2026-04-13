"""Utility functions for the simulation."""

import os
import json
import time
import asyncio
from typing import Any, Dict, Optional
import numpy as np
from openai import OpenAI, AsyncOpenAI


_LLM_API_KEY = os.getenv("LLM_API_KEY", "EMPTY")
_LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:8000/v1")


def configure_llm_backend(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> None:
    """Configure the LLM backend used by call_llm/call_llm_async."""
    global _LLM_API_KEY, _LLM_BASE_URL
    _LLM_API_KEY = "EMPTY" if api_key is None else api_key
    _LLM_BASE_URL = base_url


def get_llm_backend_config() -> Dict[str, Optional[str]]:
    """Return the current LLM backend config."""
    return {
        "api_key": _LLM_API_KEY,
        "base_url": _LLM_BASE_URL,
    }


def _make_openai_client() -> OpenAI:
    """Create a sync OpenAI-compatible client from the current backend config."""
    kwargs = {"api_key": _LLM_API_KEY, "timeout": 60.0}
    if _LLM_BASE_URL is not None:
        kwargs["base_url"] = _LLM_BASE_URL
    return OpenAI(**kwargs)


def _make_async_openai_client() -> AsyncOpenAI:
    """Create an async OpenAI-compatible client from the current backend config."""
    kwargs = {"api_key": _LLM_API_KEY}
    if _LLM_BASE_URL is not None:
        kwargs["base_url"] = _LLM_BASE_URL
    return AsyncOpenAI(**kwargs)


def _resolve_model_name(model: str) -> str:
    """Reject local model IDs on the OpenAI backend."""
    normalized = model.strip()
    if _LLM_BASE_URL is None and "/" in normalized:
        raise ValueError(
            f"Model {normalized!r} looks like a local/HuggingFace model ID, but the backend "
            "is configured for the OpenAI API (base_url=None). Use an OpenAI model ID such as "
            "'gpt-4o-mini', or call configure_llm_backend(api_key='EMPTY', "
            "base_url='http://localhost:8000/v1') for local vLLM."
        )
    return normalized


def clip(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clip value to [min_val, max_val]."""
    return max(min_val, min(max_val, value))


def setup_rng(seed: int) -> np.random.Generator:
    """Create a seeded random number generator."""
    return np.random.default_rng(seed)


def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    json_mode: bool = False,
) -> str:
    """
    Call OpenAI LLM with retry logic.

    Args:
        system_prompt: System message
        user_prompt: User message
        model: Model name
        temperature: Sampling temperature
        max_retries: Maximum number of retries on failure
        retry_delay: Delay between retries (seconds)
        json_mode: If True, force JSON output via response_format (requires "json" in prompt)

    Returns:
        LLM response text
    """
    client = _make_openai_client()
    model = _resolve_model_name(model)
    kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                **kwargs,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"LLM call failed (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(retry_delay)
            else:
                raise RuntimeError(f"LLM call failed after {max_retries} attempts: {e}")


async def call_llm_async(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    json_mode: bool = False,
) -> str:
    """
    Call OpenAI LLM asynchronously with retry logic.

    Args:
        system_prompt: System message
        user_prompt: User message
        model: Model name
        temperature: Sampling temperature
        max_retries: Maximum number of retries on failure
        retry_delay: Delay between retries (seconds)
        json_mode: If True, force JSON output via response_format (requires "json" in prompt)

    Returns:
        LLM response text
    """
    client = _make_async_openai_client()
    model = _resolve_model_name(model)
    kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}

    for attempt in range(max_retries):
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                **kwargs,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"LLM call failed (attempt {attempt + 1}/{max_retries}): {e}")
                await asyncio.sleep(retry_delay)
            else:
                raise RuntimeError(f"LLM call failed after {max_retries} attempts: {e}")


def parse_json_response(response: str, required_keys: list[str]) -> Dict[str, Any]:
    """
    Parse JSON response from LLM and validate required keys.

    Args:
        response: LLM response string
        required_keys: List of required keys in the JSON

    Returns:
        Parsed JSON dict

    Raises:
        ValueError: If parsing fails or required keys are missing
    """
    try:
        # Try to extract JSON if wrapped in markdown code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            response = response[start:end].strip()

        data = json.loads(response)

        # Validate required keys
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")

        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}\nResponse: {response}")


def validate_score(score: float, name: str, min_val: float = 0.0, max_val: float = 10.0) -> float:
    """Validate and clip a score to the expected range."""
    if not isinstance(score, (int, float)):
        raise ValueError(f"{name} must be numeric, got {type(score)}")
    return clip(score, min_val, max_val)


def render_history(
    history: list[tuple[str, str]],
    budget: int = 6000,
    approval_scores: list[float | None] | None = None,
) -> str:
    """
    Render conversation history as text, truncating if needed.

    Args:
        history: List of (role, text) tuples
        budget: Approximate token budget (rough estimate: 4 chars ≈ 1 token)
        approval_scores: Optional list of approval scores to interleave after
                         each assistant turn. Length should match the number of
                         assistant turns in history.

    Returns:
        Formatted history string
    """
    if not history:
        return "(No previous conversation)"

    # Build lines with optional approval annotations
    all_lines = []
    asst_idx = 0
    for role, text in history:
        all_lines.append(f"{role.capitalize()}: {text}")
        if role == "assistant" and approval_scores is not None:
            if asst_idx < len(approval_scores) and approval_scores[asst_idx] is not None:
                all_lines.append(f"[Approval: {approval_scores[asst_idx]}/10]")
            asst_idx += 1

    # Truncate from the front if over budget
    char_budget = budget * 4
    result_lines = []
    char_count = 0
    for line in reversed(all_lines):
        char_count += len(line) + 1
        if char_count > char_budget:
            break
        result_lines.append(line)

    result_lines.reverse()
    return "\n".join(result_lines)


def fmt_approval(approval: Optional[float]) -> str:
    """Format approval score for display."""
    if approval is None:
        return "None (first turn)"
    return f"{approval:.1f}/10"
