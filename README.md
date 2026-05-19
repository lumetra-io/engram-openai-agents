# engram-openai-agents

[OpenAI Agents SDK](https://github.com/openai/openai-agents-python) integration for [Engram](https://lumetra.io) — durable memory tools for the official OpenAI agent framework.

Returns two pre-decorated `@function_tool` callables bound to a single Engram bucket. Pass them as `tools=[...]` to any `Agent` and it gains persistent cross-session memory with hybrid retrieval (BM25 + vector + knowledge graph).

## Install

```bash
pip install lumetra-engram openai-agents
```

Vendor `engram_openai_agents.py` from this repo (~45 LOC). PyPI release coming.

```bash
export ENGRAM_API_KEY="eng_live_..."
```

## Get an Engram API key

Sign up at <https://lumetra.io> — free tier, no card. You'll see an `eng_live_…` token in your dashboard.

**Don't forget BYOK** — Engram is bring-your-own-key end-to-end for the LLM that does extraction + synthesis. Configure a provider at <https://lumetra.io/models>. DeepSeek is cheap and fast. Without one, store/query returns HTTP 412.

## Usage

```python
from agents import Agent, Runner
from engram_openai_agents import engram_tools

store, query = engram_tools(bucket="my-agent")

agent = Agent(
    name="assistant",
    instructions=(
        "You have durable memory. Before answering questions about prior "
        "context, call engram_query_memory. When the user shares a fact "
        "worth remembering, call engram_store_memory."
    ),
    tools=[store, query],
)

result = await Runner.run(agent, "My name is Jacob, please remember that.")
```

The agent's tool palette includes:

- `engram_store_memory(content)` — save an atomic fact.
- `engram_query_memory(question)` — hybrid retrieval + synthesized answer.

Pass `bucket=f"user-{user_id}"` per request for per-user isolation.

## Why this beats stateless agent runs

- **Persists across `Runner.run()` calls and across processes.** OpenAI Agent instances are stateless by default.
- **Hybrid retrieval** — BM25 + vector + knowledge graph fusion.
- **Bring-your-own-LLM for extraction + synthesis** independent of the agent's own model. Engram's BYOK provider key (at <https://lumetra.io/models>) handles inference inside Engram; your agent can use any OpenAI model on top.

## Verified

Smoke-tested against live `api.lumetra.io`:

- Both tools register as `FunctionTool` with correct `params_json_schema` (`content` / `question`) and parsed descriptions.
- Underlying client store + query round-trip: 2 memories stored, query "What decorator does the OpenAI Agents SDK use?" returns `"@function_tool."` with `memories_found=2`.

## License

MIT — Lumetra
