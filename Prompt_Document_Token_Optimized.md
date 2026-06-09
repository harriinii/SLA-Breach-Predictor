# Prompt Documentation — Token-Optimized

## Project: AI Docker Natural Language Health Dashboard

> **Goal:** Minimize token usage while preserving accuracy. Every word below earns its place.

---

## Why Token Optimization Matters

| Issue | Impact |
|-------|--------|
| Verbose system prompts | Slower LLM response, higher cost per call |
| Redundant examples | Wasted context window |
| Repeated rules | Inflated input tokens on every request |
| Over-specified output | LLM ignores excess instructions anyway |

---

## Original vs Optimized System Prompt

### Original (≈ 340 tokens)

```
You are a Docker command translator. Your task is to convert natural language 
requests into structured JSON actions.

Available actions and their formats:
1. List containers: {"action": "list_containers", "status": "running|stopped|..."}
2. Restart container: {"action": "restart_container", "container": "container_name"}
... (7 actions with full descriptions)

Examples:
- "show running containers" → {"action": "list_containers", "status": "running"}
... (14 examples)

Rules:
1. Always respond with ONLY valid JSON
2. No explanations, no markdown formatting, just the JSON object
3. Use lowercase for container names
...
Always respond with ONLY valid JSON. No explanations, no markdown, just the JSON object.
```

---

### ✅ Optimized (≈ 95 tokens) — 72% reduction

```
Docker NL→JSON translator. Output ONLY valid JSON, no text.

Actions:
list_containers: {"action":"list_containers","status":"running|stopped|restarting|exited|paused|all"}
restart_container|start_container|stop_container|get_container_health|get_container_resource_usage: {"action":"<action>","container":"<name>"}
get_container_logs: {"action":"get_container_logs","container":"<name>","tail":100}

Rules: lowercase names. status default=all. tail default=100.
```

---

## Prompt Optimization Techniques Applied

### 1. Role Compression
| Before | After | Saving |
|--------|-------|--------|
| `You are a Docker command translator. Your task is to convert natural language requests into structured JSON actions.` | `Docker NL→JSON translator.` | ~18 tokens |

### 2. Example Pruning
Keep only **ambiguous** cases — the LLM already infers direct ones.

| Keep | Remove |
|------|--------|
| `"what crashed" → {..."exited"}` | `"show running containers" → {..."running"}` (obvious) |
| `"what's broken" → {..."exited"}` | `"restart nginx" → {...}` (obvious) |
| `"check cpu and memory" → resource_usage` | `"start mysql" → start_container` (obvious) |

Reduced from 14 examples → 3 ambiguous-only examples saves ≈ 80 tokens.

### 3. Rule Deduplication
Original repeated the JSON-only rule twice. One instance is enough.

### 4. Action Schema Compression
Group actions sharing the same schema on one line instead of separate numbered blocks.

### 5. Eliminate Filler Phrases
Remove phrases like: `"Your task is to"`, `"Always respond with"`, `"No explanations"` (redundant after stating output format once).

---

## Optimized Prompts Per Use Case

### System Prompt (send once, reused every call)

```
Docker NL→JSON. Output ONLY JSON, no text.

Actions:
{"action":"list_containers","status":"running|stopped|restarting|exited|paused|all"}
{"action":"restart_container|start_container|stop_container|get_container_health|get_container_resource_usage","container":"<name>"}
{"action":"get_container_logs","container":"<name>","tail":100}

Ambiguous mappings:
crashed/broken/failed → exited
cpu/memory/stats → get_container_resource_usage
no name given → use "all" for status
```

**Token count: ~85**

---

### User Message Template (per request)

```
<user_input>
```

No wrapper needed — pass the raw user string directly. Avoid adding: `"Please translate the following:"` or `"Convert this command:"` — these add 5–8 tokens per call with zero benefit.

---

### Summary Generation Prompt (Step 6 of ReAct loop)

**Original (verbose):**
```
Based on the Docker operation results provided below, generate a concise, 
human-readable summary for the user. Be friendly and informative. 
Results: <data>
```
**Token count: ~35 + data**

**Optimized:**
```
Summarize in 1 sentence: <data>
```
**Token count: ~8 + data — 77% reduction**

---

### Agent Step Analysis Prompt (Step 2 of ReAct loop)

**Original:**
```
Analyze the following user request and determine what Docker action needs to be taken.
Consider the context and provide a structured analysis.
User request: <input>
```
**Token count: ~40**

**Optimized:**
```
Docker action for: <input>
```
**Token count: ~6 — 85% reduction**

---

## Prompt Log Analysis (from `logs/prompt_log.txt`)

Actual prompts captured from the running system:

| Timestamp | User Prompt | Action Generated | Time (ms) |
|-----------|------------|-----------------|-----------|
| 2026-06-09 09:48 | List all containers | `list_containers / all` | 1961 |
| 2026-06-09 09:48 | Give the list of stopped container | `list_containers / stopped` | 734 |
| 2026-06-09 09:51 | Give the list of stopped container | `list_containers / stopped` | 1552 |
| 2026-06-09 09:51 | Give the list of stopped container | `list_containers / stopped` | 1094 |
| 2026-06-09 09:53 | list all container | `list_containers / all` | 2176 |
| 2026-06-09 10:26 | List all containers | `list_containers / all` | 15734 |

### Observations

1. **Duplicate prompts** — "Give the list of stopped container" was sent 3 times in 2 minutes. Add client-side deduplication or a 2-second debounce to avoid redundant LLM calls.
2. **High execution time on last entry** (15,734 ms) — likely Ollama cold-start or model reload. Not a prompt issue; consider keepalive pinging Ollama every 5 minutes to keep it warm.
3. **All prompts are simple list queries** — the current system prompt is over-specified for the actual query complexity seen in production.

---

## Token Budget Recommendation

| Prompt Component | Recommended Max Tokens |
|-----------------|----------------------|
| System prompt | ≤ 100 tokens |
| User message | ≤ 50 tokens (natural language commands are short) |
| LLM output (JSON) | ≤ 40 tokens |
| Summary generation | ≤ 30 tokens output |
| **Total per call** | **≤ 220 tokens** |

With the original system prompt (~340 tokens), every single call starts 240 tokens over budget before the user even types anything.

---

## Caching Strategy for Further Savings

Since the system prompt never changes at runtime, enable **prompt caching** if your LLM provider supports it (Anthropic, OpenAI both do):

```python
# Example: mark system prompt as cacheable (Anthropic API)
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}  # cache this block
            },
            {
                "type": "text",
                "text": user_input
            }
        ]
    }
]
```

With Ollama (local), caching is implicit in the KV cache as long as the system prompt stays identical across calls — so keep it **byte-for-byte identical** every request.

---

## Before / After Token Summary

| Component | Before | After | Saved |
|-----------|--------|-------|-------|
| System prompt | ~340 | ~85 | 255 |
| Examples block | ~110 | ~30 | 80 |
| Rules block | ~60 | ~15 | 45 |
| Summary prompt | ~35 | ~8 | 27 |
| Analysis prompt | ~40 | ~6 | 34 |
| **Total per call** | **~585** | **~144** | **~441 (75%)** |

---

## Quick Reference — Drop-In Optimized Prompts

### `prompts/system_prompt.txt` (replace existing)
```
Docker NL→JSON. Output ONLY JSON, no text.

Actions:
{"action":"list_containers","status":"running|stopped|restarting|exited|paused|all"}
{"action":"restart_container|start_container|stop_container|get_container_health|get_container_resource_usage","container":"<name>"}
{"action":"get_container_logs","container":"<name>","tail":100}

crashed/broken → exited | cpu/memory/stats → get_container_resource_usage
```

### Summary call (replace in `agent.py` Step 6)
```
Summarize in 1 sentence: {result_data}
```

### Analysis call (replace in `agent.py` Step 2)
```
Docker action for: {user_input}
```

---

*Token counts estimated at ~0.75 tokens/word for English prose and exact for JSON.*
