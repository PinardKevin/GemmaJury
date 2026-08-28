# Devpost draft — GemmaJury

Copy these fields into https://allthingsagentichackathon.devpost.com/

**Category:** Taskmaster

**Project name:** GemmaJury

## Tagline

Three Gemma 4 judges. One Gemini 3.5 steward. A verdict, not a chatbot.

## Description

Hackathon judging is a messy multi-step chore: open the repo, skim the README, click the demo, watch a reel, argue about creativity, write notes. GemmaJury does that work.

A Chief Steward running Gemini 3.5 Flash pulls public evidence (GitHub tree + README + demo page). It then fans the docket out to three specialist judges — all Gemma 4 — in a Google ADK ParallelAgent:

- Code Judge — architecture, reproducibility, whether Gemma is actually doing the work
- Demo Judge — public proof, narrative, whether the agent loop is visible
- Creativity Judge — novelty, taste, whether multi-agent earned its keep

Gemini writes the final weighted opinion (code 40 / demo 30 / creativity 30) and stores the docket in Firestore. The UI is a scorecard, not a chat box.

Gemma is prioritized on purpose. Gemini only clerks the court.

## Built with

Google Gemma 4, Gemini 3.5 Flash, Google Agent Development Kit (ADK), Cloud Run, Firestore, FastAPI, public GitHub API

## What to attach

- Hosted project URL: your Cloud Run service after `./deploy/deploy.sh`
- Repo: https://github.com/PinardKevin/GemmaJury
- Architecture diagram: screenshot of docs/ARCHITECTURE.md or the header graphic
- Demo video (~4 min): convene the panel on a third-party public repo, then run the sample self-docket
- Bonus social: post on X with #AllThingsAgenticHackathon

## Script for the 4-minute video

0:00 Problem — judging a hackathon submission is a workflow, not a prompt.
0:30 Architecture — three Gemma judges, Gemini steward, ADK parallel fan-out, Cloud Run.
1:10 Live — paste a public repo + demo, watch ingest, three cards fill, verdict lands.
2:40 Open agents/agent.py and agents/models.py. Point at Gemma as the panel.
3:20 Deploy path and Firestore docket id.
3:40 Close — "Gemma sits the bench. Gemini keeps the minutes."
