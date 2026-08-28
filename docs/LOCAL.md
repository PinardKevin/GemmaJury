# Run Gemma 4 on this laptop

GemmaJury does **not** need a Google API key.
The three judges and the steward all call a Gemma 4 model that Ollama loaded onto your machine.

## 1. Install Ollama

Mac / Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Windows: download the installer from https://ollama.com

## 2. Download Gemma 4 (one time, several GB)

Student laptop / 8 GB RAM — use the small edge model:

```bash
ollama pull gemma4:e2b
```

16 GB RAM laptop — better quality:

```bash
ollama pull gemma4:e4b
```

Confirm:

```bash
ollama list
ollama run gemma4:e2b "Say hello in one sentence."
```

Leave Ollama running. On most machines `ollama serve` starts by itself after install.

## 3. Run GemmaJury

```bash
cd GemmaJury
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn server.main:app --port 8080
```

Open http://localhost:8080

- **Play sample docket** = fake recorded verdict. Use this if the download is still running.
- **Convene the panel** = live local Gemma. The laptop CPU/GPU does the work. No cloud.

If you pulled `gemma4:e4b` instead, create a `.env` file:

```
GEMMA_LOCAL_MODEL=gemma4:e4b
```

## How to prove it is local to judges

1. Open a terminal and run `ollama list`. They will see `gemma4:e2b`.
2. Open `agents/local_gemma.py`. It only talks to `http://127.0.0.1:11434`.
3. Turn Wi-Fi off *after* the model is pulled. **Convene the panel** still works for the model calls (GitHub fetch will fail offline — that is expected; paste the pitch instead).
