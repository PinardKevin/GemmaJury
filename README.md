# GemmaJury

**Three Gemma 4 judges. One Gemini 3.5 steward. A verdict — not a chatbot.**

GemmaJury is a multi-agent judging panel that takes a public hackathon submission (repository + demo + pitch) and produces a structured scorecard. It was built for the [All Things Agentic Hackathon](https://allthingsagentichackathon.devpost.com/) on the **Taskmaster** track.

> Gemma is the product. Gemini is the clerk of court.

| Role | Model | Job |
|---|---|---|
| **Code Judge** | Gemma 4 (`gemma-4-31b-it`) | Architecture, correctness, Gemma-first design, reproducibility |
| **Demo Judge** | Gemma 4 (`gemma-4-31b-it`) | Presentation quality, demo-reel clarity, public proof it works |
| **Creativity Judge** | Gemma 4 (`gemma-4-31b-it`) | Novelty, taste, whether the idea actually needed agents |
| **Chief Steward** | Gemini 3.5 Flash | Ingests evidence, fans out the panel, writes the final verdict |

Orchestration is Google **ADK** (`ParallelAgent` + `SequentialAgent`). Persistence and deploy target are **Firestore** and **Cloud Run**.

## Why this exists

Hackathon judging is a messy, multi-step chore: open the repo, skim the README, click the demo, watch a reel, argue about creativity, write notes, assign scores. GemmaJury does that work. Humans still own the final call — the panel just shows up prepared.

Gemma is not a side model. Every specialist judge **is** Gemma 4, with native tool calling against the submission evidence. Gemini 3.5 only stewards the docket: gather evidence, run the panel in parallel, reconcile disagreements, persist the verdict.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add GEMINI_API_KEY
uvicorn server.main:app --reload --port 8080
```

Open http://localhost:8080

To inspect the agents in ADK's own UI:

```bash
adk web agents
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/DEVPOST.md](docs/DEVPOST.md).

## Hackathon compliance

| Requirement | How GemmaJury satisfies it |
|---|---|
| Gemini 3.5 or newer | Chief Steward and Verdict Writer use `gemini-3.5-flash` |
| Google agent framework | Google ADK (`LlmAgent`, `ParallelAgent`, `SequentialAgent`) |
| Google Cloud service | Cloud Run deploy + optional Firestore docket store |
| Gemma prioritized | All three specialist judges are Gemma 4 with tools |
| Public repo + demo | This repository, plus the Cloud Run UI |

Track: **Taskmaster** — a complete judging workflow, not a chatbot.

## License

Apache 2.0
