"""Shared Gemini API helper for BD Tools.

The API key is read lazily so the Streamlit UI can load even before a key is
configured. On Streamlit Community Cloud, add:

[gemini]
api_key = "YOUR_KEY"
model = "gemini-3.8-flash"
"""

from __future__ import annotations

import json
import os
import re
import time
from typing import Any

import streamlit as st
from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3.8-flash"


def _secret_value(section: str, key: str, default: str | None = None) -> str | None:
    try:
        section_value = st.secrets.get(section, {})
        if hasattr(section_value, "get"):
            return section_value.get(key, default)
    except Exception:
        pass
    return default


def get_api_key() -> str:
    """Return the Gemini API key from env or Streamlit secrets."""
    api_key = os.getenv("GEMINI_API_KEY") or _secret_value("gemini", "api_key")
    if not api_key:
        raise RuntimeError(
            "Gemini API key is missing. In Streamlit Cloud open Manage app > "
            "Settings > Secrets and add:\n\n[gemini]\napi_key = \"YOUR_KEY\""
        )
    return str(api_key)


def get_model() -> str:
    return str(os.getenv("GEMINI_MODEL") or _secret_value("gemini", "model", DEFAULT_MODEL))


def generate_text(
    prompt: str,
    *,
    system_instruction: str | None = None,
    max_output_tokens: int | None = None,
    retries: int = 3,
) -> str:
    """Generate plain text with Gemini using a small retry loop."""
    client = genai.Client(api_key=get_api_key())

    config_kwargs: dict[str, Any] = {}
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction
    if max_output_tokens:
        config_kwargs["max_output_tokens"] = max_output_tokens

    config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=get_model(),
                contents=prompt,
                config=config,
            )
            text = (response.text or "").strip()
            if not text:
                raise RuntimeError("Gemini returned an empty response.")
            return text
        except Exception as exc:  # SDK errors vary by version/status code
            last_error = exc
            if attempt < retries - 1:
                time.sleep(2 ** attempt)

    raise RuntimeError(f"Gemini request failed after {retries} attempts: {last_error}")


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object even if the model wrapped it in Markdown fences."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError(f"Gemini did not return a JSON object: {cleaned[:300]}")
        value = json.loads(cleaned[start : end + 1])

    if not isinstance(value, dict):
        raise ValueError("Gemini response was valid JSON but not a JSON object.")
    return value
