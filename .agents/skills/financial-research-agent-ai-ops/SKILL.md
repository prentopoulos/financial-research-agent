---
name: financial-research-agent-ai-ops
description: Operate Ledger retrieval, LangGraph workflow, future LLM/RAG behavior, evaluation, runtime state, monitoring, and recovery.
---

# Ledger AI operations

Read `AI_OPS.md`, `PROJECT.md`, and the build-safety skill. Version provider contracts, workflow
topology, prompts/models, retrieval configuration, and evaluation cases together. Deterministic
calculations and citations remain authoritative over generated language.

Before enabling an LLM or RAG, add fixed groundedness/completeness cases, planted-injection tests,
token/time/cost limits, provider fallback policy, and recovery evidence. Before durable memory, define
schema ownership, retention, deletion, isolation, and replay behavior. Before Phoenix or production
telemetry, define redaction and access. Paid calls and deployment require owner approval.
