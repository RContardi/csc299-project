"""OpenAI integration helpers for Task Manager.

This module provides a thin wrapper around the OpenAI ChatCompletion API to
extract structured task fields from a natural-language sentence.

It is optional: if `OPENAI_API_KEY` is not set the functions return a low-
confidence empty result so callers can fall back to local heuristics.
"""
from __future__ import annotations

import json
import os
import logging
from typing import Dict, Optional

try:
    import openai
    from openai.error import OpenAIError
except Exception:  # pragma: no cover - optional dependency
    openai = None  # type: ignore
    OpenAIError = Exception  # type: ignore

_LOG = logging.getLogger(__name__)

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
MODEL = os.environ.get("TASK_MANAGER_AI_MODEL", "gpt-3.5-turbo-0613")


def set_api_key(key: Optional[str]) -> None:
    """Set the OpenAI API key to use for subsequent calls.

    Passing None or empty string unsets the key. This sets the module-level
    OPENAI_KEY variable and configures the `openai` library if available.
    """
    global OPENAI_KEY
    if key:
        OPENAI_KEY = key
        if openai is not None:
            openai.api_key = key
    else:
        OPENAI_KEY = None
        if openai is not None:
            openai.api_key = None

def parse_with_ai(text: str, timeout: int = 10, api_key: Optional[str] = None) -> Dict[str, Optional[str]]:
    """Ask OpenAI to parse a natural-language sentence into task fields.

    Returns a dict with keys: title, description, due_date, priority, confidence.
    If OpenAI is not configured or an error occurs, returns a low-confidence
    empty response so callers can fall back.
    """
    key_to_use = api_key or OPENAI_KEY
    if not key_to_use or openai is None:
        _LOG.debug("OpenAI key not configured or openai package missing")
        return {"title": None, "description": None, "due_date": None, "priority": None, "confidence": 0.0}

    openai.api_key = key_to_use

    functions = [
        {
            "name": "extract_task",
            "description": "Extract a task title, optional description, due date, and priority.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": ["string", "null"]},
                    "due_date": {"type": ["string", "null"]},
                    "priority": {"type": ["string", "null"], "enum": ["low", "medium", "high", None]},
                    "confidence": {"type": "number"},
                },
                "required": ["title"],
            },
        }
    ]

    try:
        resp = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You extract concise task fields: title, description, due_date, priority."},
                {"role": "user", "content": f"Parse this into a task: {text}"},
            ],
            functions=functions,
            function_call={"name": "extract_task"},
            temperature=0.0,
            timeout=timeout,
        )

        msg = resp["choices"][0]["message"]
        if msg.get("function_call"):
            payload = msg["function_call"].get("arguments", "{}")
            try:
                parsed = json.loads(payload)
            except Exception:
                parsed = {}
            return {
                "title": parsed.get("title"),
                "description": parsed.get("description"),
                "due_date": parsed.get("due_date"),
                "priority": parsed.get("priority"),
                "confidence": float(parsed.get("confidence", 0.9)),
            }
        _LOG.debug("No function_call in OpenAI response")
        return {"title": None, "description": None, "due_date": None, "priority": None, "confidence": 0.0}
    except OpenAIError as e:
        _LOG.exception("OpenAI API error: %s", e)
        return {"title": None, "description": None, "due_date": None, "priority": None, "confidence": 0.0}


def test_api_key(api_key: Optional[str], timeout: int = 5) -> tuple[bool, str]:
    """Validate an OpenAI API key by making a tiny chat request.

    Returns (True, message) on success or (False, error_message) on failure.
    This is intentionally minimal and uses the same model configured by
    TASK_MANAGER_AI_MODEL.
    """
    key_to_use = api_key or OPENAI_KEY
    if not key_to_use or openai is None:
        return False, "OpenAI package missing or API key not provided"

    try:
        openai.api_key = key_to_use
        # perform a minimal call that should succeed with a valid key
        resp = openai.ChatCompletion.create(
            model=MODEL,
            messages=[{"role": "system", "content": "Respond with OK."}, {"role": "user", "content": "ping"}],
            temperature=0.0,
            timeout=timeout,
        )
        # if we got a response, treat it as success
        return True, "OK"
    except Exception as e:  # pragma: no cover - network/credentials dependent
        _LOG.exception("OpenAI test call failed")
        return False, str(e)
