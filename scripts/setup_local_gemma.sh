#!/usr/bin/env bash
set -euo pipefail
MODEL="${GEMMA_LOCAL_MODEL:-gemma4:e2b}"

if ! command -v ollama >/dev/null 2>&1; then
  echo "Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
fi

echo "Pulling $MODEL — this is the Gemma 4 weights living on your disk."
ollama pull "$MODEL"
ollama list
echo "Done. Keep this machine awake and run: uvicorn server.main:app --port 8080"
