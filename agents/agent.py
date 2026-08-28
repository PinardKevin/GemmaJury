"""ADK root agent.

Pattern used (the ADK workshop's parallel fan-out):
  SequentialAgent
    1. ingest steward  (Gemini 3.5)
    2. ParallelAgent   (three Gemma 4 judges)
    3. verdict steward (Gemini 3.5)
"""

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

from .models import gemini_steward_model, gemma_judge_model
from .prompts import CODE_JUDGE, CREATIVITY_JUDGE, DEMO_JUDGE, STEWARD_INGEST, VERDICT_WRITER
from .tools import fetch_demo_evidence, fetch_github_evidence, fetch_github_file

ingest_agent = LlmAgent(
    name="chief_steward_ingest",
    model=gemini_steward_model(),
    description="Gathers public repo, demo, and pitch evidence into a docket.",
    instruction=STEWARD_INGEST,
    tools=[fetch_github_evidence, fetch_demo_evidence, fetch_github_file],
    output_key="evidence_pack",
)

code_judge = LlmAgent(
    name="code_judge",
    model=gemma_judge_model(),
    description="Gemma 4 judge for architecture, correctness, and Gemma-first design.",
    instruction=CODE_JUDGE,
    tools=[fetch_github_file],
    output_key="code_opinion",
)

demo_judge = LlmAgent(
    name="demo_judge",
    model=gemma_judge_model(),
    description="Gemma 4 judge for demo reels, public proof, and presentation.",
    instruction=DEMO_JUDGE,
    tools=[fetch_demo_evidence],
    output_key="demo_opinion",
)

creativity_judge = LlmAgent(
    name="creativity_judge",
    model=gemma_judge_model(),
    description="Gemma 4 judge for novelty, taste, and whether agents were necessary.",
    instruction=CREATIVITY_JUDGE,
    output_key="creativity_opinion",
)

panel = ParallelAgent(
    name="gemma_panel",
    description="Three Gemma 4 specialist judges running concurrently.",
    sub_agents=[code_judge, demo_judge, creativity_judge],
)

verdict_agent = LlmAgent(
    name="chief_steward_verdict",
    model=gemini_steward_model(),
    description="Reconciles the Gemma panel into a weighted verdict.",
    instruction=VERDICT_WRITER,
    output_key="verdict",
)

root_agent = SequentialAgent(
    name="gemma_jury",
    description="Hackathon judging workflow: ingest, Gemma panel, verdict.",
    sub_agents=[ingest_agent, panel, verdict_agent],
)
