"""
UI Helper and Styling Module for Streamlit.
Provides custom styling, card containers, diagram rendering with fallback,
and formatting utilities.
"""

import streamlit as st
import pandas as pd
from .models import MealyMachine, MooreMachine
from .visualization import (
    generate_mealy_dot,
    generate_moore_dot,
    generate_mealy_mermaid,
    generate_moore_mermaid,
)


CUSTOM_CSS = """
<style>
/* Modern Academic Theme Styling */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Metric card styling */
.metric-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.metric-title {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1e293b;
}

@media (prefers-color-scheme: dark) {
    .metric-value {
        color: #f1f5f9;
    }
    .metric-title {
        color: #94a3b8;
    }
}

/* Badge styling */
.badge {
    display: inline-block;
    padding: 3px 10px;
    font-size: 0.78rem;
    font-weight: 600;
    border-radius: 9999px;
    margin-right: 6px;
    margin-bottom: 4px;
}

.badge-blue {
    background-color: #dbeafe;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
}

.badge-green {
    background-color: #dcfce7;
    color: #15803d;
    border: 1px solid #bbf7d0;
}

.badge-purple {
    background-color: #f3e8ff;
    color: #7e22ce;
    border: 1px solid #e9d5ff;
}

.badge-amber {
    background-color: #fef3c7;
    color: #b45309;
    border: 1px solid #fde68a;
}

/* Path chip styling */
.path-container {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    padding: 12px;
    background-color: rgba(148, 163, 184, 0.08);
    border-radius: 10px;
    margin: 10px 0;
}

.path-node {
    background: #2563eb;
    color: white;
    padding: 4px 12px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.9rem;
}

.path-arrow {
    color: #64748b;
    font-weight: bold;
}
</style>
"""


def apply_custom_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_machine_diagram(machine, title: str = "State Diagram"):
    """
    Renders an automata diagram using Graphviz DOT with Mermaid fallback.
    """
    st.subheader(title)
    is_mealy = isinstance(machine, MealyMachine)

    dot_str = generate_mealy_dot(machine) if is_mealy else generate_moore_dot(machine)
    mermaid_str = generate_mealy_mermaid(machine) if is_mealy else generate_moore_mermaid(machine)

    rendered = False
    try:
        # Streamlit's st.graphviz_chart uses client-side Viz.js
        st.graphviz_chart(dot_str, use_container_width=True)
        rendered = True
    except Exception as e:
        # Fallback to Mermaid if Graphviz chart fails
        st.warning(f"Graphviz rendering encountered an issue: {e}. Falling back to Mermaid visualization.")
        st.markdown(f"```mermaid\n{mermaid_str}\n```")
        rendered = True

    with st.expander("🔍 View Raw Diagram Source Code (DOT & Mermaid)"):
        tab1, tab2 = st.tabs(["Graphviz DOT", "Mermaid.js"])
        with tab1:
            st.code(dot_str, language="dot")
        with tab2:
            st.code(mermaid_str, language="mermaid")


def render_metric_card(title: str, value: str, subtext: str = ""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            {"<div style='font-size: 0.8rem; color: #64748b; margin-top: 4px;'>" + subtext + "</div>" if subtext else ""}
        </div>
        """,
        unsafe_allow_html=True
    )
