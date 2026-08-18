# BLACK — AI Agent Security / Multi-Step Tool Attacks

Dedicated BLACK execution layer for the Kaggle **AI Agent Security - Multi-Step Tool Attacks** competition.

## Objective

Search for reproducible multi-step failure traces against the competition environment, validate them locally, rank them by measured evidence, and package replayable candidates for Kaggle submission.

## Architecture

```text
BLACK Controller
  ├─ Environment probe / capability inventory
  ├─ Parallel exploration workers
  │   ├─ single-turn baseline
  │   ├─ multi-turn chains
  │   ├─ state/snapshot exploration
  │   ├─ mutation / replay checks
  │   └─ independent strategy arms
  ├─ Trace archive
  ├─ Replay / reproducibility gate
  ├─ Candidate scorer
  ├─ Diversity + novelty filter
  └─ Submission packer (≤ 2,000 candidates)
```

## Competition contract

The competition provides `env.reset()`, `env.interact(prompt)`, `env.snapshot()`, `env.restore(handle)`, and `env.export_trace_dict()`. Candidate chains are independently replayed against public/private guardrails. The competition permits up to 2,000 candidates, 32 messages per candidate, 8 tool hops per interaction, and 10,000 characters per message.

## Safety boundary

This project is restricted to the competition's supplied sandbox and evaluation fixtures. It does not target real services, credentials, users, or external systems.

## Execution

The implementation is intentionally split into deterministic orchestration, candidate generation, replay validation, scoring, and submission packaging so each experimental arm can be measured independently.
