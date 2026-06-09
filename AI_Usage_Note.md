# AI Usage Note — SLA Breach Prediction System

## Overview

This project uses Large Language Models (LLMs) as its core intelligence layer for ticket classification and risk reasoning. All AI interactions are stateless, prompt-driven, and performed via the Groq API.

---

## Model Used

| Property | Value |
|---|---|
| Provider | Groq |
| Model | `llama-3.3-70b-versatile` |
| Interface | REST API via `groq` Python SDK |
| Context window | 128k tokens |

---

## AI-Powered Functions

### 1. Ticket Severity Classification (`analyze_ticket`)

Called on every ticket submission (manual or CSV). The LLM receives the raw ticket description and returns a structured severity assessment.

**Input:** Free-text issue description  
**Output:** `(priority: str, complexity_score: int)`

Evaluation criteria used in the prompt:
- Business impact
- User impact (single user vs. many users)
- Technical complexity
- Service availability risk
- Revenue impact

**Complexity → Priority mapping:**

| Score | Priority |
|---|---|
| 1–2 | Low |
| 3 | Medium |
| 4 | High |
| 5 | Critical |

---

### 2. Risk Reason Generation (`generate_risk_reason`)

Called on-demand for tickets in `CRITICAL BREACH RISK` or `Breached` state. The LLM generates a short, human-readable explanation of why a ticket is at risk.

**Input:** Ticket description, complexity score, remaining minutes  
**Output:** 1–2 sentence risk rationale string

Results are cached via `@st.cache_data(ttl=600)` to avoid redundant API calls on dashboard refresh.

---

## Token Optimisation

- Prompts are single-turn (no conversation history sent).
- System prompts are compact; no chain-of-thought is requested unless reasoning is needed.
- Risk reason responses are capped to ~50 tokens via `max_tokens` constraint.
- `generate_risk_reason` results are cached for 10 minutes per ticket to suppress repeat calls during the 30-second dashboard auto-refresh cycle.

---

## Limitations & Caveats

- The LLM does not have access to ticket history or customer context — it classifies purely from the description text.
- Severity scores are non-deterministic; the same description may occasionally yield a ±1 score variation.
- Groq API rate limits apply; bulk CSV imports process tickets sequentially to avoid hitting limits.
- No PII scrubbing is applied before sending ticket text to the Groq API. Operators should ensure customer descriptions do not contain sensitive personal data.

---

## Future AI Enhancements

- RAG-based incident knowledge base for classification grounding
- Multi-agent escalation reasoning
- Root cause analysis via tool-augmented LLM
- SLA breach forecasting using historical ticket embeddings
