# GemmaJury

**Three Gemma 4 judges running on your laptop. A verdict — not a chatbot.**

Built for **305 HackFiesta Miami** (GDG FIU). Gemma is required and must run locally.

Public repo: https://github.com/PinardKevin/GemmaJury

## Does this run Gemma locally?

**Yes, now.** The judges call Ollama at `http://127.0.0.1:11434`. The default model is `gemma4:e2b` (Gemma 4 edge, student-laptop sized). There is no Gemini API key on the live path.

Step-by-step: [docs/LOCAL.md](docs/LOCAL.md)

```bash
# 1. one-time: install Ollama + pull Gemma 4 onto this machine
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma4:e2b

# 2. run the app
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn server.main:app --reload --port 8080
```

Open http://localhost:8080

| Button | What happens |
|---|---|
| Play sample docket | Recorded verdict. Works even while the model is still downloading. |
| Convene the panel | Live local Gemma 4. CPU/GPU on this laptop. |

## Architecture

Local Gemma steward gathers the public repo/demo, then three local Gemma 4 judges score code, demo, and creativity in parallel.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/DEVPOST.md](docs/DEVPOST.md), [docs/KAGGLE_WRITEUP.md](docs/KAGGLE_WRITEUP.md).
