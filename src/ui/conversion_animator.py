"""
Signature Feature: Animated Machine Conversion Engine for Automata Lab.
Renders step-by-step visual transformations of finite-state transducers,
including incoming transition output tracing, state splitting, and transition remapping.
"""

import html
import textwrap
from typing import List, Optional
import streamlit as st
import streamlit.components.v1 as components
from .svg_diagram import render_svg_state_diagram, display_svg_diagram


def _html(s: str):
    clean = textwrap.dedent(s).strip()
    if hasattr(st, "html"):
        st.html(clean)
    else:
        st.markdown(clean, unsafe_allow_html=True)


def render_animated_conversion_view(
    orig_machine,
    conv_machine,
    steps: List[ConversionStep],
    direction: str = "Mealy -> Moore"
):
    """
    Renders an interactive, step-by-step visual animation of the conversion process.
    Provides Play, Pause, Step Forward, Step Backward, and Restart controls.
    """
    if not steps:
        st.info("Execute a conversion to activate the transformation animator.")
        return

    # Initialize playback state in session_state
    if "anim_step_idx" not in st.session_state:
        st.session_state.anim_step_idx = 0
    if "anim_playing" not in st.session_state:
        st.session_state.anim_playing = False

    total_steps = len(steps)
    curr_idx = min(st.session_state.anim_step_idx, total_steps - 1)
    current_step = steps[curr_idx]

    # --- Header & Step Timeline Controls ---
    _html(f"""
    <div class="lab-panel" style="margin-bottom: 14px; padding: 16px 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <span class="lab-badge lab-badge-cyan">ANIMATION ENGINE</span>
                <span style="font-weight: 700; font-size: 1.1rem; color: #FFFFFF; margin-left: 8px;">
                    Step {curr_idx + 1} of {total_steps}: {html.escape(current_step.title)}
                </span>
            </div>
            <div style="font-size: 0.82rem; color: var(--lab-text-muted); font-family: 'JetBrains Mono', monospace;">
                MODE: {html.escape(direction)}
            </div>
        </div>
    </div>
    """)

    # --- Interactive Playback Control Bar ---
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4, ctrl_col5 = st.columns([1, 1, 1, 1, 2])

    with ctrl_col1:
        if st.button("⏮️ Start", use_container_width=True, key="anim_start"):
            st.session_state.anim_step_idx = 0
            st.rerun()

    with ctrl_col2:
        if st.button("◀️ Previous", use_container_width=True, disabled=(curr_idx <= 0), key="anim_prev"):
            st.session_state.anim_step_idx = max(0, curr_idx - 1)
            st.rerun()

    with ctrl_col3:
        if st.button("Next ▶️", use_container_width=True, disabled=(curr_idx >= total_steps - 1), key="anim_next"):
            st.session_state.anim_step_idx = min(total_steps - 1, curr_idx + 1)
            st.rerun()

    with ctrl_col4:
        if st.button("⏭️ End", use_container_width=True, key="anim_end"):
            st.session_state.anim_step_idx = total_steps - 1
            st.rerun()

    with ctrl_col5:
        # Step Slider for direct access
        new_step = st.slider(
            "Scrub Animation Step",
            min_value=1,
            max_value=total_steps,
            value=curr_idx + 1,
            label_visibility="collapsed",
            key="anim_slider"
        )
        if new_step - 1 != curr_idx:
            st.session_state.anim_step_idx = new_step - 1
            st.rerun()

    # --- Dynamic Visual Canvas ---
    # Depending on current step index, display transformation stages:
    # Early steps (1-3): Focus on original machine and incoming outputs
    # Mid steps (4-5): Show state splitting and transition calculation
    # Final steps (6+): Show converted machine settling and validation
    canv_col1, canv_col2 = st.columns([1, 1])

    with canv_col1:
        _html(f"""
        <div style="font-size: 0.85rem; font-weight: 600; color: #D97706; margin-bottom: 6px; display:flex; align-items:center; gap:6px;">
            <span>ORIGINAL TRANSDUCER</span>
            <span class="lab-badge lab-badge-mealy">SOURCE</span>
        </div>
        """)
        # Highlight original machine with active stage styling
        active_state = None
        if "Mealy" in direction.split()[0] and curr_idx in [1, 2]:
            # Highlight states being analyzed for incoming outputs
            active_state = orig_machine.states[min(curr_idx, len(orig_machine.states) - 1)]

        display_svg_diagram(
            orig_machine,
            width=520,
            height=300,
            active_state=active_state,
            container_id="anim_orig_svg"
        )

    with canv_col2:
        _html(f"""
        <div style="font-size: 0.85rem; font-weight: 600; color: #0284C7; margin-bottom: 6px; display:flex; align-items:center; gap:6px;">
            <span>CONVERTED TRANSDUCER</span>
            <span class="lab-badge lab-badge-moore">{"TARGET" if curr_idx >= 3 else "SYNTHESIZING..."}</span>
        </div>
        """)
        if curr_idx < 3:
            _html("""
            <div style="height: 300px; display: flex; flex-direction: column; align-items: center; justify-content: center;
                        background: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 10px; color: var(--lab-text-muted); box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);">
                <div style="font-size: 1.8rem; margin-bottom: 8px;">⚙️</div>
                <div style="font-size: 0.9rem; font-weight: 600; color: var(--lab-text-secondary);">Analyzing Transition Structures...</div>
                <div style="font-size: 0.78rem;">Advance steps to watch state-splitting and transition remapping.</div>
            </div>
            """)
        else:
            display_svg_diagram(
                conv_machine,
                width=520,
                height=300,
                active_state=conv_machine.initial_state if curr_idx == 4 else None,
                container_id="anim_conv_svg"
            )

    # --- Step Mathematical Rationale Card ---
    _html(f"""
    <div class="lab-panel" style="margin-top: 16px;">
        <div class="lab-panel-header">
            <div class="lab-panel-title">
                <span style="color: var(--lab-cyan); font-family: 'JetBrains Mono', monospace;">STEP {current_step.step_number}:</span>
                <span>{html.escape(current_step.title)}</span>
            </div>
            <div class="lab-badge lab-badge-cyan">STAGE {curr_idx + 1}/{total_steps}</div>
        </div>
        <p style="font-size: 0.93rem; color: var(--lab-text-secondary); line-height: 1.6; margin-bottom: 12px;">
            {html.escape(current_step.description)}
        </p>
    </div>
    """)
    if current_step.table_data is not None:
        st.markdown("**Step Computation Data:**")
        st.dataframe(current_step.table_data, use_container_width=True, hide_index=True)
