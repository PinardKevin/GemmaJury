# Architecture

GemmaJury is a **Taskmaster** workflow: ingest evidence, run specialists, write an opinion, persist the docket. It is not a chat loop.

## Required stack

| Rule | Implementation |
|---|---|
| Gemini 3.5 or newer | `gemini-3.5-flash` as Chief Steward (ingest + verdict) |
| Google agent framework | Google ADK: `LlmAgent`, `ParallelAgent`, `SequentialAgent` |
| Google Cloud service | Cloud Run service + optional Firestore collection `gemmajury_dockets` |
| Gemma prioritized | All three specialist judges are `gemma-4-31b-it` via the Gemini API |

## Orchestration pattern

ADK workshop pattern: sequential spine with a parallel fan-out.

```
SequentialAgent (gemma_jury)
├── LlmAgent chief_steward_ingest     Gemini 3.5 + tools
├── ParallelAgent gemma_panel
│   ├── LlmAgent code_judge           Gemma 4 + fetch_github_file
│   ├── LlmAgent demo_judge           Gemma 4 + fetch_demo_evidence
│   └── LlmAgent creativity_judge     Gemma 4
└── LlmAgent chief_steward_verdict    Gemini 3.5
```

Shared session state keys: `evidence_pack`, `code_opinion`, `demo_opinion`, `creativity_opinion`, `verdict`.

## Why Gemma sits the panel

Gemma 4 has native tool calling and structured output in ADK. That is the whole point of a specialist judge: read a file, return JSON, do not narrate. Gemini 3.5 is better at long-context intake and writing a human-readable opinion, so it clerks the court. The product story is intentional, not a fallback.

## Tools

- `fetch_github_evidence` — public GitHub metadata, README, languages, file tree
- `fetch_github_file` — one source file, capped
- `fetch_demo_evidence` — public demo HTTP status, title, text excerpt

No private tokens. Submissions must already be public, which matches the Devpost rule.

## Persistence

`server/store.py` writes the docket to Firestore when `GOOGLE_CLOUD_PROJECT` is set. Otherwise it keeps an in-memory list so Cloud Run still serves the UI if Firestore is off.

## Two runtimes, one panel

1. `adk web agents` — official ADK developer UI against `root_agent`
2. `uvicorn server.main:app` — public scorecard used as the hosted demo

The HTTP path calls the same models and tools. If the key is missing, it serves the recorded self-verdict so the four-minute video never dies on a cold start.
