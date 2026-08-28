"""ADK root agent — every LlmAgent uses local Gemma 4 through Ollama."""

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

from .models import local_gemma_adk_model
from .prompts import CODE_JUDGE, CREATIVITY_JUDGE, DEMO_JUDGE, STEWARD_INGEST, VERDICT_WRITER
from .tools import fetch_demo_evidence, fetch_github_evidence, fetch_github_file

_local = local_gemma_adk_model()

ingest_agent = LlmAgent(
    name="chief_steward_ingest",
    model=_local,
    description="Local Gemma 4 steward that gathers public repo and demo evidence.",
    instruction=STEWARD_INGEST,
    tools=[fetch_github_evidence, fetch_demo_evidence, fetch_github_file],
    output_key="evidence_pack",
)

code_judge = LlmAgent(
    name="code_judge",
    model=_local,
    description="Local Gemma 4 judge for architecture and Gemma-first design.",
    instruction=CODE_JUDGE,
    tools=[fetch_github_file],
    output_key="code_opinion",
)

demo_judge = LlmAgent(
    name="demo_judge",
    model=_local,
    description="Local Gemma 4 judge for demo reels and public proof.",
    instruction=DEMO_JUDGE,
    tools=[fetch_demo_evidence],
    output_key="demo_opinion",
)

creativity_judge = LlmAgent(
    name="creativity_judge",
    model=_local,
    description="Local Gemma 4 judge for novelty and taste.",
    instruction=CREATIVITY_JUDGE,
    output_key="creativity_opinion",
)

panel = ParallelAgent(
    name="gemma_panel",
    description="Three local Gemma 4 specialist judges running concurrently.",
    sub_agents=[code_judge, demo_judge, creativity_judge],
)

verdict_agent = LlmAgent(
    name="chief_steward_verdict",
    model=_local,
    description="Local Gemma 4 steward that writes the weighted verdict.",
    instruction=VERDICT_WRITER,
    output_key="verdict",
)

root_agent = SequentialAgent(
    name="gemma_jury",
    description="Fully local Gemma 4 judging workflow.",
    sub_agents=[ingest_agent, panel, verdict_agent],
)
