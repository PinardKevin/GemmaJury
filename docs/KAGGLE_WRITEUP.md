# GemmaJury — Kaggle / Gemma Challenge writeup

## Project overview
GemmaJury is a multi-agent judging panel for hackathon submissions. Three Gemma 4 specialists score code, demo/presentation, and creativity. A steward gathers public evidence and writes a single verdict.

## Problem
In-person judging is a bottleneck. Teams get two minutes. Judges cannot read a whole repository. Scores drift toward whoever demoed last.

## Solution
Treat judging as a workflow, not a chat:
1. Ingest a public GitHub URL, demo URL, and pitch.
2. Fan out to three Gemma 4 judges in an ADK ParallelAgent.
3. Reconcile into a weighted scorecard (code 40 / demo 30 / creativity 30).

## Architecture
SequentialAgent: ingest (Gemini 3.5 steward + tools) → ParallelAgent of three Gemma 4 LlmAgents → verdict writer.
Tools: fetch_github_evidence, fetch_github_file, fetch_demo_evidence.
UI: FastAPI scorecard so the panel is visible, not hidden in logs.

## How Gemma was used
Gemma 4 (`gemma-4-31b-it` via the Gemini API / AI Studio) is every specialist judge. Each judge has its own rubric and must return structured JSON with citations. Gemma is not a logo on a Gemini wrapper. If Gemma is removed, there is no panel.

## Challenges
Live Gemma 4 calls add latency. We shipped a recorded self-verdict so the 6pm showcase still works if the key or network fails.

## What was built
Public repo, local scorecard UI, ADK agent graph, evidence tools, sample docket, Devpost copy.
Repo: https://github.com/PinardKevin/GemmaJury
