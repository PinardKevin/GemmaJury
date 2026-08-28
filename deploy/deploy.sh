#!/usr/bin/env bash
# Deploy GemmaJury to Cloud Run.
# Prereqs: gcloud auth login && gcloud config set project YOUR_PROJECT
set -euo pipefail

PROJECT="${GOOGLE_CLOUD_PROJECT:?set GOOGLE_CLOUD_PROJECT}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
SERVICE="${SERVICE_NAME:-gemmajury}"

gcloud run deploy "$SERVICE" \
  --source . \
  --region "$REGION" \
  --project "$PROJECT" \
  --allow-unauthenticated \
  --timeout 300 \
  --memory 1Gi \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY:?set GEMINI_API_KEY},GEMMA_JUDGE_MODEL=${GEMMA_JUDGE_MODEL:-gemma-4-31b-it},GEMINI_STEWARD_MODEL=${GEMINI_STEWARD_MODEL:-gemini-3.5-flash},GOOGLE_CLOUD_PROJECT=${PROJECT},FIRESTORE_COLLECTION=${FIRESTORE_COLLECTION:-gemmajury_dockets}"

gcloud run services describe "$SERVICE" --region "$REGION" --project "$PROJECT" --format='value(status.url)'
