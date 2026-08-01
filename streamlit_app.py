"""Interactive Streamlit UI for the Energent agent demo."""

import os
import sys
from pathlib import Path

import streamlit as st

# Ensure imports work when launching from repository root.
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT.parent))

from agents.agent import Agent, ModelConfig
from agents.tools.think import ThinkTool


st.set_page_config(
    page_title="Energent Agent Studio",
    page_icon="AI",
    layout="wide",
)

st.markdown(
    """
    <style>
      .stApp {
        background: radial-gradient(circle at top left, #e9f5ff 0%, #fdfdf8 45%, #ffeccd 100%);
      }
      .block-container {
        max-width: 1100px;
        padding-top: 2rem;
      }
      .hero {
        border: 1px solid rgba(30, 41, 59, 0.15);
        border-radius: 18px;
        padding: 1.2rem 1.4rem;
        background: rgba(255, 255, 255, 0.78);
        backdrop-filter: blur(4px);
      }
      .hero h1 {
        margin: 0;
        font-size: 2.1rem;
        letter-spacing: 0.3px;
      }
      .hero p {
        margin: 0.5rem 0 0 0;
        color: #334155;
      }
      .result-box {
        border-left: 6px solid #0f766e;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 1rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
      <h1>Energent Agent Studio</h1>
      <p>Run a configurable Claude-powered tool agent and inspect responses in one place.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Run Settings")
    model = st.selectbox(
        "Model",
        [
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-haiku-4-5-20251001",
        ],
        index=0,
    )
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    max_tokens = st.slider("Max Tokens", min_value=128, max_value=4096, value=512, step=128)
    verbose = st.checkbox("Verbose Logging", value=False)

if not os.environ.get("ANTHROPIC_API_KEY"):
    st.warning("ANTHROPIC_API_KEY is not set. Add it to your environment to execute live runs.")

prompt = st.text_area(
    "Prompt",
    value="Give me a concise checklist for evaluating an AI agent project before production.",
    height=130,
)

col_a, col_b = st.columns([1, 4])
run_clicked = col_a.button("Run Agent", type="primary", use_container_width=True)
col_b.caption("Tip: start with concise prompts, then increase complexity and tool use.")

if run_clicked:
    if not prompt.strip():
        st.error("Prompt cannot be empty.")
    elif not os.environ.get("ANTHROPIC_API_KEY"):
        st.error("Set ANTHROPIC_API_KEY before running the agent.")
    else:
        config = ModelConfig(model=model, temperature=temperature, max_tokens=max_tokens)
        agent = Agent(
            name="StudioAgent",
            system="You are a pragmatic AI engineering assistant.",
            tools=[ThinkTool()],
            config=config,
            verbose=verbose,
        )

        with st.spinner("Running agent..."):
            response = agent.run(prompt)

        text_blocks = [b.text for b in response.content if getattr(b, "type", "") == "text"]
        combined_text = "\n\n".join(text_blocks).strip() or "(No text content returned.)"

        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.subheader("Agent Response")
        st.write(combined_text)
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("Raw Response Blocks"):
            st.write(response.content)
