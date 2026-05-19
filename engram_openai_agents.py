"""
engram_openai_agents — durable memory tools for the OpenAI Agents SDK.

OpenAI's Agents SDK exposes tools via the @function_tool decorator. This
module returns two pre-decorated tools bound to a single Engram bucket.

Usage:

    from agents import Agent, Runner
    from engram_openai_agents import engram_tools

    store, query = engram_tools(bucket="my-agent")
    agent = Agent(
        name="assistant",
        instructions="Use engram_query_memory before answering ...",
        tools=[store, query],
    )
"""

from __future__ import annotations

import os
from typing import Optional

from agents import function_tool
from lumetra_engram import EngramClient


def engram_tools(
    bucket: str,
    *,
    client: Optional[EngramClient] = None,
):
    """Return (store_tool, query_tool) bound to a single Engram bucket."""
    c = client or EngramClient(api_key=os.environ.get("ENGRAM_API_KEY"))

    @function_tool
    def engram_store_memory(content: str) -> str:
        """Save an atomic fact to durable agent memory.

        Args:
            content: One declarative fact, e.g. "User prefers dark mode."
        """
        r = c.store_memory(content, bucket)
        return f"stored {r.get('memory_id', '(unknown)')}"

    @function_tool
    def engram_query_memory(question: str) -> str:
        """Hybrid retrieval + synthesized answer over prior memory.

        Args:
            question: Natural-language question about prior context.
        """
        r = c.query(question, buckets=[bucket])
        ans = r.get("answer") or ""
        return ans.split("FINAL ANSWER:")[-1].strip() or "No memories found."

    return engram_store_memory, engram_query_memory
