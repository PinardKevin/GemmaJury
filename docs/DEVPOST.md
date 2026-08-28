# Devpost + live demo — 305 HackFiesta Miami (Session A)

**Event:** 305 HackFiesta Miami Edition August 2026
**Room:** FIU PG6 Room 144
**Live demos:** today 6:00–7:00 PM
**Required form:** https://305hackfiestamiamiaug2026.devpost.com/
**Public repo:** https://github.com/PinardKevin/GemmaJury

Gemma is required and scored at 30/100. Do not mention Gemini as the star. Gemma sits the three judge seats.

## Paste into Devpost

**Project name:** GemmaJury

**Tagline:** Three Gemma 4 judges score a hackathon submission in one sitting.

**Built with:** Gemma 4, Google ADK, Gemini 3.5 Flash (steward only), FastAPI, GitHub API

**Description:**

Hackathon judges run out of time. They open a repo, skim a README, click a demo, argue about creativity, and guess at a score.

GemmaJury is a multi-agent panel that does that chore. A steward gathers the public repo and demo. Then three specialist judges — all Gemma 4 — score in parallel:

- Code judge: architecture, reproducibility, whether Gemma is actually doing the work
- Demo judge: public proof and whether a stranger can see the agent loop
- Creativity judge: novelty, taste, whether multi-agent earned its keep

The steward writes one weighted verdict a human can read aloud. Gemma is the panel. Everything else is clerk work.

**Repo URL:** https://github.com/PinardKevin/GemmaJury
**Demo URL:** http://localhost:8080 (live on our laptop at the showcase; sample docket works without a key)

## 90-second live demo script

1. Problem (15s): Judges cannot fairly read every repo tonight. We built them a panel.
2. Gemma first (15s): Open agents/models.py. Three judges are gemma-4-31b-it. Gemini only stewards.
3. Click (30s): Open localhost:8080. Hit Play sample docket. Three cards fill: code, demo, creativity. Total and ship/revise/reject.
4. If the key works (20s): Paste this repo URL, convene the live panel, show tools fetching GitHub.
5. Close (10s): Gemma sits the bench. The steward keeps the minutes.

If Wi-Fi dies: sample docket still renders. That is the fallback. Do not debug live.
