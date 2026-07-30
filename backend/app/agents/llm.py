from __future__ import annotations

import json
import logging
import re
from typing import Any

from openai import AsyncOpenAI
from app.config import Settings

logger = logging.getLogger(__name__)


def get_llm_client(settings: Settings | None = None) -> AsyncOpenAI:
    if settings is None:
        settings = Settings()
        
    if settings.llm_provider.lower() == "groq":
        return AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )
    else:
        return AsyncOpenAI(
            api_key=settings.openai_api_key,
        )


def parse_json_response(response: str) -> dict:
    """Robustly extract JSON from an LLM response, even if wrapped in markdown code blocks."""
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
    if match:
        response = match.group(1)
    else:
        # Fallback to finding the first { and last }
        start = response.find("{")
        end = response.rfind("}")
        if start != -1 and end != -1:
            response = response[start : end + 1]
    
    return json.loads(response)


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o",
) -> str:
    """Helper to make a simple LLM call."""
    settings = Settings()
    
    # Map models for Groq if selected
    if settings.llm_provider.lower() == "groq":
        model = "llama-3.1-70b-versatile"
        
    client = get_llm_client(settings)
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error("LLM call failed: %s", e)
        return f"Error contacting LLM: {str(e)}"
