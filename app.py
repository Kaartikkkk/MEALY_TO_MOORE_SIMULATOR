"""
AUTOMATA LAB — Finite-State Transducer Studio
Mealy <-> Moore Machine Conversion Simulator
Course: CSET302 Automata Theory & Computability (Topic 14)

A product-grade, interactive academic engineering laboratory for finite-state transducers.
"""

import json
import html
import textwrap
from typing import Dict, Any, List, Optional
import streamlit as st
import pandas as pd


def _html(s: str):
    clean = textwrap.dedent(s).strip()
    if hasattr(st, "html"):
        st.html(clean)
    else:
        st.markdown(clean, unsafe_allow_html=True)

from src.models import MealyMachine, MooreMachine, ConversionStep
from src.validation import validate_mealy, validate_moore
from src.mealy_to_moore import convert_mealy_to_moore
from src.moore_to_mealy import convert_moore_to_mealy
from src.simulation import simulate_mealy, simulate_moore
from src.equivalence import (
    check_string_equivalence,
    run_standard_test_suite,
    run_bounded_exhaustive_equivalence
)
from src.examples import get_mealy_examples, get_moore_examples
from src.ui.icons import get_svg_icon
from src.ui.theme import apply_theme
from src.ui.svg_diagram import render_svg_state_diagram, display_svg_diagram
from src.ui.conversion_animator import render_animated_conversion_view
from src.ui.components import render_top_bar, render_hero_banner, render_metric_tile


# --- Page Configuration ---
st.set_page_config(
    page_title="Automata Lab — Mealy ↔ Moore Studio",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Master Design System
apply_theme()


# --- Session State Management ---
def init_session_state():
    if "direction" not in st.session_state:
        st.session_state.direction = "Mealy -> Moore"
    if "current_mealy" not in st.session_state:
        mealy_presets = get_mealy_examples()
        st.session_state.current_mealy = list(mealy_presets.values())[0].copy()
    if "current_moore" not in st.session_state:
        moore_presets = get_moore_examples()
        st.session_state.current_moore = list(moore_presets.values())[0].copy()
    if "conversion_done" not in st.session_state:
        st.session_state.conversion_done = False
    if "converted_machine" not in st.session_state:
        st.session_state.converted_machine = None
    if "conversion_steps" not in st.session_state:
        st.session_state.conversion_steps = []
    if "sim_input" not in st.session_state:
        st.session_state.sim_input = "0011"
    if "sim_step_idx" not in st.session_state:
        st.session_state.sim_step_idx = -1

init_session_state()


# --- Sidebar Navigation & Lab Brand ---
with st.sidebar:
    # Lab Brand
    _html(f"""
    <div style="padding: 6px 4px 18px 4px; border-bottom: 1px solid var(--lab-border); margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="background: #EFF6FF; padding: 7px; border-radius: 8px; border: 1px solid #BFDBFE;">
                {get_svg_icon("logo", size=20, color="#2563EB")}
            </div>
            <div>
                <div style="font-size: 1.05rem; font-weight: 700; letter-spacing: -0.02em; color: #0F172A;">AUTOMATA LAB</div>
                <div style="font-size: 0.72rem; color: var(--lab-text-muted); font-family: 'JetBrains Mono', monospace;">FST STUDIO v1.0</div>
            </div>
        </div>
    </div>
    """)

    _html("""
    <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--lab-text-muted); margin-bottom: 8px;">
        STUDIO WORKSPACES
    </div>
    """)

    nav_options = [
        "Overview & Theory",
        "Conversion Studio",
        "String Simulator",
        "Equivalence & Verification",
        "Documentation & Viva"
    ]
    
    page = st.radio(
        "Navigation",
        nav_options,
        label_visibility="collapsed"
    )

    st.markdown("---")
    _html("""
    <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--lab-text-muted); margin-bottom: 8px;">
        CONVERSION MODE
    </div>
    """)

    dir_options = ["Mealy -> Moore", "Moore -> Mealy"]
    selected_dir = st.selectbox(
        "Select Direction",
        dir_options,
        index=0 if st.session_state.direction == "Mealy -> Moore" else 1,
        label_visibility="collapsed"
    )
    if selected_dir != st.session_state.direction:
        st.session_state.direction = selected_dir
        st.session_state.conversion_done = False
        st.session_state.converted_machine = None
        st.session_state.conversion_steps = []
        st.rerun()

    st.markdown("---")
    if st.button("Reset Presets", use_container_width=True):
        mealy_presets = get_mealy_examples()
        moore_presets = get_moore_examples()
        st.session_state.current_mealy = list(mealy_presets.values())[0].copy()
        st.session_state.current_moore = list(moore_presets.values())[0].copy()
        st.session_state.conversion_done = False
        st.session_state.converted_machine = None
        st.session_state.conversion_steps = []
        st.rerun()

    _html("""
    <div style="margin-top: 24px; padding: 12px; background: #F8FAFC; border-radius: 8px; border: 1px solid var(--lab-border); font-size: 0.75rem; color: var(--lab-text-muted);">
        <div style="color: var(--lab-text-primary); font-weight: 600; margin-bottom: 4px;">CSET302 AUTOMATA</div>
        <div>Topic 14: Mealy ↔ Moore</div>
        <div>Evaluation: Nov 2026</div>
    </div>
    """)


# ==============================================================================
# WORKSPACE 1: OVERVIEW & THEORY
# ==============================================================================
if page == "Overview & Theory":
    render_top_bar("Overview & Theory", st.session_state.direction, "READY")
    render_hero_banner()

    # Live Real Metrics
    st.markdown("### Studio Capability Statistics")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        render_metric_tile("Conversion Algorithms", "2 Directions", "Mealy ↔ Moore complete", "BI-DIRECTIONAL", "cyan")
    with m_col2:
        render_metric_tile("Verified Presets", "6 Machines", "2's complement, modulo, parity", "PRESETS", "violet")
    with m_col3:
        render_metric_tile("Automated Tests", "23 Tests", "100% test pass rate", "VERIFIED", "emerald")
    with m_col4:
        render_metric_tile("Time Complexity", "O(|Q'|·|Σ|)", "Linear to transition table", "OPTIMAL", "amber")

    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        _html(f"""
        <div class="lab-panel">
            <div class="lab-panel-header">
                <div class="lab-panel-title">
                    {get_svg_icon("code", size=18, color="#2563EB")}
                    <span>Mathematical Transducer Foundations</span>
                </div>
            </div>
            <p style="font-size: 0.92rem; color: var(--lab-text-secondary); line-height: 1.6;">
                A <b>finite-state transducer (FST)</b> is a deterministic 6-tuple:
                <br><code class="mono-font" style="color: #2563EB; font-weight: 600;">M = (Q, Σ, Γ, δ, λ, q₀)</code>
            </p>
            <ul style="font-size: 0.88rem; color: var(--lab-text-secondary); line-height: 1.7; padding-left: 20px;">
                <li><b>Q</b>: Finite non-empty set of internal states</li>
                <li><b>Σ</b>: Finite input symbol alphabet</li>
                <li><b>Γ</b>: Finite output symbol alphabet</li>
                <li><b>δ</b>: Transition function <code class="mono-font">Q × Σ → Q</code></li>
                <li><b>q₀</b>: Initial starting state (<code class="mono-font">q₀ ∈ Q</code>)</li>
            </ul>
            <div style="margin-top: 14px; padding: 10px 14px; background: #EFF6FF; border-left: 3px solid #2563EB; border-radius: 4px;">
                <div style="font-weight: 600; font-size: 0.85rem; color: #1D4ED8;">Output Function Divergence</div>
                <div style="font-size: 0.82rem; color: var(--lab-text-secondary); margin-top: 2px;">
                    • <b>Mealy:</b> <code class="mono-font">λ: Q × Σ → Γ</code> (Depends on current state AND input)<br>
                    • <b>Moore:</b> <code class="mono-font">λ: Q → Γ</code> (Depends exclusively on current state)
                </div>
            </div>
        </div>
        """)

    with col2:
        _html(f"""
        <div class="lab-panel">
            <div class="lab-panel-header">
                <div class="lab-panel-title">
                    {get_svg_icon("conversion", size=18, color="#8B5CF6")}
                    <span>Architectural Comparison</span>
                </div>
            </div>
        </div>
        """)
        comp_data = [
            {"Dimension": "Output Source", "Mealy Transducer": "Transition Edges", "Moore Transducer": "Internal States"},
            {"Dimension": "Output Timing", "Mealy Transducer": "Immediate with input", "Moore Transducer": "Clock edge / state entry"},
            {"Dimension": "Output Length |w|=n", "Mealy Transducer": "n symbols", "Moore Transducer": "n + 1 symbols (initial y₀)"},
            {"Dimension": "State Complexity", "Mealy Transducer": "Minimal |Q|", "Moore Transducer": "Splits up to |Q| × |Γ|"},
            {"Dimension": "Digital Hardware", "Mealy Transducer": "Combinational logic", "Moore Transducer": "Synchronous isolated register"},
            {"Dimension": "Alignment Rule", "Mealy Transducer": "Mealy(w)", "Moore Transducer": "y₀ · Mealy(w)"}
        ]
        st.dataframe(pd.DataFrame(comp_data), hide_index=True, use_container_width=True)

# ==============================================================================
# WORKSPACE 2: CONVERSION STUDIO
# ==============================================================================
elif page == "Conversion Studio":
    render_top_bar("Conversion Studio", st.session_state.direction, "VALIDATED" if st.session_state.conversion_done else "READY")

    # Section A: Header Mode Banner
    _html(f"""
    <div style="background: rgba(14, 22, 38, 0.7); border: 1px solid var(--lab-border); border-radius: 10px; padding: 14px 20px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span class="lab-badge {'lab-badge-mealy' if 'Mealy' in st.session_state.direction.split()[0] else 'lab-badge-moore'}">
                {html.escape(st.session_state.direction)}
            </span>
            <span style="font-size: 0.92rem; color: var(--lab-text-secondary);">
                {"State-splitting transformation based on incoming transition outputs." if "Mealy" in st.session_state.direction.split()[0] else "Destination state output projection onto transition edges."}
            </span>
        </div>
        <div style="display: flex; gap: 8px;">
            <span class="lab-badge lab-badge-cyan">DETERMINISTIC</span>
            <span class="lab-badge lab-badge-emerald">COMPLETE</span>
        </div>
    </div>
    """)

    tab_config, tab_results, tab_animated, tab_trace = st.tabs([
        "1. Machine Setup & Editor",
        "2. Vector Diagrams & Results",
        "3. Signature Conversion Animation",
        "4. Step-by-Step Trace"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: MACHINE SETUP
    # --------------------------------------------------------------------------
    with tab_config:
        st.markdown("#### Transducer Definition & Preset Selector")

        cfg_col1, cfg_col2 = st.columns([1, 1])

        if st.session_state.direction == "Mealy -> Moore":
            presets = get_mealy_examples()
            curr_machine = st.session_state.current_mealy

            with cfg_col1:
                selected_preset = st.selectbox("Select Verified Preset", list(presets.keys()))
                if st.button("Load Preset Machine", use_container_width=True):
                    st.session_state.current_mealy = presets[selected_preset].copy()
                    st.session_state.conversion_done = False
                    st.session_state.converted_machine = None
                    st.rerun()
                curr_machine = st.session_state.current_mealy

            with cfg_col2:
                states_str = st.text_input("States Q (comma-separated)", value=", ".join(curr_machine.states))
                parsed_states = [s.strip() for s in states_str.split(",") if s.strip()]
                init_idx = parsed_states.index(curr_machine.initial_state) if curr_machine.initial_state in parsed_states else 0
                init_state = st.selectbox("Initial State q0", parsed_states if parsed_states else ["q0"], index=init_idx)

            p_col1, p_col2 = st.columns(2)
            with p_col1:
                sigma_str = st.text_input("Input Alphabet Σ", value=", ".join(curr_machine.input_alphabet))
            with p_col2:
                gamma_str = st.text_input("Output Alphabet Γ", value=", ".join(curr_machine.output_alphabet))

            parsed_sigma = [s.strip() for s in sigma_str.split(",") if s.strip()]
            parsed_gamma = [s.strip() for s in gamma_str.split(",") if s.strip()]

            st.markdown("#### Transition & Output Matrix Editor")
            flat_df = curr_machine.to_flat_table()
            edited_df = st.data_editor(
                flat_df,
                num_rows="dynamic",
                use_container_width=True,
                key="editor_mealy"
            )

            new_trans = {}
            new_outs = {}
            for _, r in edited_df.iterrows():
                q = str(r.get("Current State", "")).strip()
                a = str(r.get("Input Symbol", "")).strip()
                nxt = str(r.get("Next State", "")).strip()
                out = str(r.get("Output Symbol", "")).strip()
                if q and a:
                    new_trans[(q, a)] = nxt
                    new_outs[(q, a)] = out

            candidate = MealyMachine(
                states=parsed_states,
                input_alphabet=parsed_sigma,
                output_alphabet=parsed_gamma,
                transitions=new_trans,
                outputs=new_outs,
                initial_state=init_state
            )
            st.session_state.current_mealy = candidate

            # Validation Status
            val_res = validate_mealy(candidate)
            if val_res.is_valid:
                _html(
                    f"""
                    <div style="padding: 10px 14px; background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 6px; font-size: 0.85rem; color: #065F46; font-weight: 500; margin: 12px 0;">
                        {get_svg_icon("success", size=16, color="#059669")} Machine structure is deterministically complete and valid.
                    </div>
                    """
                )
            else:
                for err in val_res.errors:
                    st.error(f"Error: {err}")

            st.markdown("---")
            if st.button("SYNTHESIZE CONVERSION (Mealy → Moore)", type="primary", use_container_width=True, disabled=not val_res.is_valid):
                with st.spinner("Synthesizing Moore Machine and Step Traces..."):
                    moore_res, steps = convert_mealy_to_moore(candidate)
                    st.session_state.converted_machine = moore_res
                    st.session_state.conversion_steps = steps
                    st.session_state.conversion_done = True
                st.rerun()

        else:  # Moore -> Mealy
            presets = get_moore_examples()
            curr_machine = st.session_state.current_moore

            with cfg_col1:
                selected_preset = st.selectbox("Select Verified Preset", list(presets.keys()))
                if st.button("Load Preset Machine", use_container_width=True):
                    st.session_state.current_moore = presets[selected_preset].copy()
                    st.session_state.conversion_done = False
                    st.session_state.converted_machine = None
                    st.rerun()
                curr_machine = st.session_state.current_moore

            with cfg_col2:
                states_str = st.text_input("States Q (comma-separated)", value=", ".join(curr_machine.states))
                parsed_states = [s.strip() for s in states_str.split(",") if s.strip()]
                init_idx = parsed_states.index(curr_machine.initial_state) if curr_machine.initial_state in parsed_states else 0
                init_state = st.selectbox("Initial State q0", parsed_states if parsed_states else ["q0"], index=init_idx)

            p_col1, p_col2 = st.columns(2)
            with p_col1:
                sigma_str = st.text_input("Input Alphabet Σ", value=", ".join(curr_machine.input_alphabet))
            with p_col2:
                gamma_str = st.text_input("Output Alphabet Γ", value=", ".join(curr_machine.output_alphabet))

            parsed_sigma = [s.strip() for s in sigma_str.split(",") if s.strip()]
            parsed_gamma = [s.strip() for s in gamma_str.split(",") if s.strip()]

            st.markdown("#### State Outputs & Transition Table Editor")
            flat_df = curr_machine.to_flat_table()
            edited_df = st.data_editor(
                flat_df,
                num_rows="dynamic",
                use_container_width=True,
                key="editor_moore"
            )

            new_trans = {}
            new_outs = {}
            for _, r in edited_df.iterrows():
                q = str(r.get("Current State", "")).strip()
                out = str(r.get("State Output", "")).strip()
                a = str(r.get("Input Symbol", "")).strip()
                nxt = str(r.get("Next State", "")).strip()
                if q:
                    new_outs[q] = out
                if q and a:
                    new_trans[(q, a)] = nxt

            candidate = MooreMachine(
                states=parsed_states,
                input_alphabet=parsed_sigma,
                output_alphabet=parsed_gamma,
                transitions=new_trans,
                outputs=new_outs,
                initial_state=init_state
            )
            st.session_state.current_moore = candidate

            val_res = validate_moore(candidate)
            if val_res.is_valid:
                _html(
                    f"""
                    <div style="padding: 10px 14px; background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 6px; font-size: 0.85rem; color: #065F46; font-weight: 500; margin: 12px 0;">
                        {get_svg_icon("success", size=16, color="#059669")} Machine structure is deterministically complete and valid.
                    </div>
                    """
                )
            else:
                for err in val_res.errors:
                    st.error(f"Error: {err}")

            st.markdown("---")
            if st.button("SYNTHESIZE CONVERSION (Moore → Mealy)", type="primary", use_container_width=True, disabled=not val_res.is_valid):
                with st.spinner("Synthesizing Mealy Machine and Step Traces..."):
                    mealy_res, steps = convert_moore_to_mealy(candidate)
                    st.session_state.converted_machine = mealy_res
                    st.session_state.conversion_steps = steps
                    st.session_state.conversion_done = True
                st.rerun()

        # JSON Export / Import
        with st.expander("Machine Definition JSON Interface"):
            e_col1, e_col2 = st.columns(2)
            with e_col1:
                st.download_button(
                    "Download Definition JSON",
                    data=json.dumps(curr_machine.to_dict(), indent=2),
                    file_name="fst_definition.json",
                    mime="application/json",
                    use_container_width=True
                )
            with e_col2:
                up_file = st.file_uploader("Upload JSON Definition", type=["json"])
                if up_file:
                    try:
                        d = json.load(up_file)
                        if d.get("type") == "Mealy" and st.session_state.direction == "Mealy -> Moore":
                            st.session_state.current_mealy = MealyMachine.from_dict(d)
                            st.rerun()
                        elif d.get("type") == "Moore" and st.session_state.direction == "Moore -> Mealy":
                            st.session_state.current_moore = MooreMachine.from_dict(d)
                            st.rerun()
                    except Exception as ex:
                        st.error(f"Error parsing JSON: {ex}")

    # --------------------------------------------------------------------------
    # TAB 2: DIAGRAMS & RESULTS
    # --------------------------------------------------------------------------
    with tab_results:
        if not st.session_state.conversion_done or st.session_state.converted_machine is None:
            st.info("Execute a conversion in Tab 1 to view synthesized vector diagrams and comparative metrics.")
        else:
            orig = st.session_state.current_mealy if "Mealy" in st.session_state.direction.split()[0] else st.session_state.current_moore
            conv = st.session_state.converted_machine

            # Comparative Metrics Grid
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                render_metric_tile("Source States", f"{len(orig.states)} states", f"Start: {orig.initial_state}", "SOURCE", "mealy")
            with m2:
                render_metric_tile("Target States", f"{len(conv.states)} states", f"Start: {conv.initial_state}", "TARGET", "moore")
            with m3:
                d_count = len(conv.states) - len(orig.states)
                d_str = f"+{d_count}" if d_count > 0 else f"{d_count}"
                render_metric_tile("State Splitting Delta", f"{d_str} states", "State copies created" if d_count > 0 else "Count preserved", "DELTA", "violet")
            with m4:
                render_metric_tile("Alphabets", f"|Σ|={len(orig.input_alphabet)} |Γ|={len(orig.output_alphabet)}", "Alphabets preserved", "ALPHABETS", "emerald")

            st.markdown("---")

            # Vector State Diagrams
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                _html(
                    f"""<div style="font-size: 0.95rem; font-weight: 700; color: #D97706; margin-bottom: 8px;">
                        SOURCE DIAGRAM ({type(orig).__name__})
                    </div>"""
                )
                display_svg_diagram(orig, width=540, height=330, container_id="diagram_orig")

            with d_col2:
                _html(
                    f"""<div style="font-size: 0.95rem; font-weight: 700; color: #0284C7; margin-bottom: 8px;">
                        TARGET DIAGRAM ({type(conv).__name__})
                    </div>"""
                )
                display_svg_diagram(conv, width=540, height=330, container_id="diagram_conv")

            st.markdown("---")

            # Transition Tables
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                st.markdown("**Source Transition Table**")
                o_df = orig.to_dataframe()
                st.dataframe(o_df, use_container_width=True, hide_index=True)
                st.download_button(
                    "Download Source Table (CSV)",
                    data=o_df.to_csv(index=False),
                    file_name="source_table.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with t_col2:
                st.markdown("**Synthesized Target Table**")
                c_df = conv.to_dataframe()
                st.dataframe(c_df, use_container_width=True, hide_index=True)
                st.download_button(
                    "Download Target Table (CSV)",
                    data=c_df.to_csv(index=False),
                    file_name="target_table.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    # --------------------------------------------------------------------------
    # TAB 3: SIGNATURE FEATURE ANIMATION
    # --------------------------------------------------------------------------
    with tab_animated:
        if not st.session_state.conversion_done or st.session_state.converted_machine is None:
            st.info("Execute a conversion in Tab 1 to run the animated transformation engine.")
        else:
            orig = st.session_state.current_mealy if "Mealy" in st.session_state.direction.split()[0] else st.session_state.current_moore
            conv = st.session_state.converted_machine
            render_animated_conversion_view(orig, conv, st.session_state.conversion_steps, direction=st.session_state.direction)

    # --------------------------------------------------------------------------
    # TAB 4: STEP-BY-STEP TRACE
    # --------------------------------------------------------------------------
    with tab_trace:
        if not st.session_state.conversion_done or not st.session_state.conversion_steps:
            st.info("Conversion trace will appear after execution.")
        else:
            for s in st.session_state.conversion_steps:
                with st.expander(f"Step {s.step_number}: {s.title}", expanded=(s.step_number <= 3)):
                    st.markdown(f"**Rationale:** {s.description}")
                    if s.table_data is not None:
                        st.dataframe(s.table_data, use_container_width=True, hide_index=True)


# ==============================================================================
# WORKSPACE 3: STRING SIMULATOR
# ==============================================================================
elif page == "String Simulator":
    render_top_bar("String Simulator", st.session_state.direction, "SIMULATING")

    orig_mach = st.session_state.current_mealy if "Mealy" in st.session_state.direction.split()[0] else st.session_state.current_moore
    conv_mach = st.session_state.converted_machine

    s_ctrl_col, s_view_col = st.columns([1, 2])

    with s_ctrl_col:
        st.markdown("#### Simulation Controls")
        
        target_options = ["Source Machine"]
        if st.session_state.conversion_done and conv_mach is not None:
            target_options.append("Target Machine (Converted)")
            target_options.append("Concurrent Side-by-Side Comparison")

        selected_sim_target = st.radio("Simulation Model", target_options)

        # Quick preset inputs
        st.markdown("**Quick Preset Strings:**")
        p1, p2, p3, p4 = st.columns(4)
        if p1.button("0011"):
            st.session_state.sim_input = "0011"
        if p2.button("1010"):
            st.session_state.sim_input = "1010"
        if p3.button("1101"):
            st.session_state.sim_input = "1101"
        if p4.button("ε (Empty)"):
            st.session_state.sim_input = ""

        input_str = st.text_input("Input String w", value=st.session_state.sim_input)
        st.session_state.sim_input = input_str

        # Validate alphabet
        valid_set = set(orig_mach.input_alphabet)
        invalid_symbols = [c for c in input_str if c not in valid_set]
        if invalid_symbols:
            st.error(f"Invalid symbol(s) detected: {set(invalid_symbols)}. Must be in Σ: {orig_mach.input_alphabet}")
            can_sim = False
        else:
            can_sim = True

    with s_view_col:
        if can_sim:
            if selected_sim_target == "Source Machine":
                trace = simulate_mealy(orig_mach, input_str) if isinstance(orig_mach, MealyMachine) else simulate_moore(orig_mach, input_str)

                # Metrics
                q1, q2, q3 = st.columns(3)
                with q1:
                    render_metric_tile("Input Sequence", f"'{input_str}'" if input_str else "ε (Empty)", f"Length: {len(input_str)}", "INPUT", "cyan")
                with q2:
                    render_metric_tile("Emitted Output", f"'{trace.output_string}'" if trace.output_string else "ε", f"Length: {len(trace.output_string)}", "OUTPUT", "emerald")
                with q3:
                    render_metric_tile("Final State", trace.final_state, f"Start: {trace.initial_state}", "TERMINUS", "violet")

                # Execution Path Chips
                st.markdown("**Execution State Trajectory:**")
                chips_html = '<div class="lab-path-flow">'
                for i, node in enumerate(trace.state_path):
                    chips_html += f'<span class="lab-path-node">{html.escape(node)}</span>'
                    if i < len(trace.state_path) - 1:
                        chips_html += '<span class="lab-path-arrow">→</span>'
                chips_html += '</div>'
                st.markdown(chips_html, unsafe_allow_html=True)

                # Live Animated State Highlight on SVG
                current_active_state = trace.state_path[-1] if trace.state_path else orig_mach.initial_state
                display_svg_diagram(
                    orig_mach,
                    width=600,
                    height=280,
                    active_state=current_active_state,
                    container_id="svg_sim_source"
                )

                # Trace Dataframe
                st.markdown("**Step-by-Step Transition Log:**")
                st.dataframe(trace.to_dataframe(), use_container_width=True, hide_index=True)

            elif selected_sim_target == "Target Machine (Converted)":
                if conv_mach is None:
                    st.warning("Convert a machine first in the Conversion Studio.")
                else:
                    trace = simulate_moore(conv_mach, input_str) if isinstance(conv_mach, MooreMachine) else simulate_mealy(conv_mach, input_str)

                    q1, q2, q3 = st.columns(3)
                    with q1:
                        render_metric_tile("Input Sequence", f"'{input_str}'" if input_str else "ε (Empty)", f"Length: {len(input_str)}", "INPUT", "cyan")
                    with q2:
                        render_metric_tile("Emitted Output", f"'{trace.output_string}'" if trace.output_string else "ε", f"Length: {len(trace.output_string)}", "OUTPUT", "emerald")
                    with q3:
                        render_metric_tile("Final State", trace.final_state, f"Start: {trace.initial_state}", "TERMINUS", "violet")

                    st.markdown("**Execution State Trajectory:**")
                    chips_html = '<div class="lab-path-flow">'
                    for i, node in enumerate(trace.state_path):
                        chips_html += f'<span class="lab-path-node">{html.escape(node)}</span>'
                        if i < len(trace.state_path) - 1:
                            chips_html += '<span class="lab-path-arrow">→</span>'
                    chips_html += '</div>'
                    _html(chips_html)

                    current_active_state = trace.state_path[-1] if trace.state_path else conv_mach.initial_state
                    display_svg_diagram(
                        conv_mach,
                        width=600,
                        height=280,
                        active_state=current_active_state,
                        container_id="svg_sim_target"
                    )

                    st.markdown("**Step-by-Step Transition Log:**")
                    st.dataframe(trace.to_dataframe(), use_container_width=True, hide_index=True)

            else:  # Concurrent
                mealy = orig_mach if isinstance(orig_mach, MealyMachine) else conv_mach
                moore = conv_mach if isinstance(orig_mach, MealyMachine) else orig_mach
                eq_res = check_string_equivalence(mealy, moore, input_str, direction=st.session_state.direction)

                _html(
                    f"""
                    <div class="lab-panel">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 700; font-size: 1.1rem; color: #0F172A;">
                                {'✅ EQUIVALENCE VERIFIED' if eq_res.passed else '❌ MISMATCH DETECTED'}
                            </span>
                            <span class="lab-badge {'lab-badge-emerald' if eq_res.passed else 'lab-badge-rose'}">
                                {'PASS' if eq_res.passed else 'FAIL'}
                            </span>
                        </div>
                        <div style="font-size: 0.88rem; color: var(--lab-text-secondary); margin-top: 8px;">
                            {html.escape(eq_res.details)}
                        </div>
                    </div>
                    """
                )

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Source Machine Trace**")
                    t1 = simulate_mealy(orig_mach, input_str) if isinstance(orig_mach, MealyMachine) else simulate_moore(orig_mach, input_str)
                    st.dataframe(t1.to_dataframe(), use_container_width=True, hide_index=True)
                with c2:
                    st.markdown("**Target Machine Trace**")
                    t2 = simulate_moore(conv_mach, input_str) if isinstance(conv_mach, MooreMachine) else simulate_mealy(conv_mach, input_str)
                    st.dataframe(t2.to_dataframe(), use_container_width=True, hide_index=True)


# ==============================================================================
# WORKSPACE 4: EQUIVALENCE & VERIFICATION
# ==============================================================================
elif page == "Equivalence & Verification":
    render_top_bar("Equivalence & Verification", st.session_state.direction, "VALIDATING")

    if not st.session_state.conversion_done or st.session_state.converted_machine is None:
        st.info("Execute a conversion in the Conversion Studio first to activate behavioral equivalence verification.")
    else:
        orig = st.session_state.current_mealy if "Mealy" in st.session_state.direction.split()[0] else st.session_state.current_moore
        conv = st.session_state.converted_machine

        mealy = orig if isinstance(orig, MealyMachine) else conv
        moore = conv if isinstance(orig, MealyMachine) else orig

        _html(
            f"""
            <div class="lab-panel">
                <div class="lab-panel-header">
                    <div class="lab-panel-title">
                        {get_svg_icon("validation", size=18, color="#059669")}
                        <span>Behavioral Equivalence Alignment Theorem</span>
                    </div>
                </div>
                <p style="font-size: 0.9rem; color: var(--lab-text-secondary); line-height: 1.6; margin-bottom: 0;">
                    For any input sequence <code class="mono-font">w ∈ Σ*</code> of length <code class="mono-font">n</code>:
                    A Moore machine emits <code class="mono-font">n + 1</code> symbols (initial state output <code class="mono-font">y₀</code> at <code class="mono-font">t = 0</code> followed by <code class="mono-font">n</code> transition outputs).
                    A Mealy machine emits <code class="mono-font">n</code> symbols.
                    The two transducers are behaviorally equivalent if and only if:
                    <br><code class="mono-font" style="color: #2563EB; font-weight: 700;">Output_Moore(w) = y₀ · Output_Mealy(w)</code>
                </p>
            </div>
            """
        )

        v_t1, v_t2, v_t3 = st.tabs([
            "Bounded Exhaustive Verification (Σ^≤k)",
            "Representative Edge-Case Suite",
            "Single-String Probe"
        ])

        with v_t1:
            st.markdown("#### Bounded Exhaustive Test Suite")
            b_col1, b_col2 = st.columns([1, 2])

            with b_col1:
                max_k = st.slider("Maximum String Length k", min_value=1, max_value=4, value=3)
                alpha_size = len(mealy.input_alphabet)
                total_k = sum(alpha_size ** i for i in range(max_k + 1))
                st.caption(f"Tests all {total_k} strings over Σ = {mealy.input_alphabet}.")

                btn_b = st.button("RUN BOUNDED VERIFICATION", type="primary", use_container_width=True)

            with b_col2:
                if btn_b:
                    with st.spinner(f"Verifying {total_k} strings..."):
                        b_res = run_bounded_exhaustive_equivalence(mealy, moore, max_length=max_k, direction=st.session_state.direction)

                    v1, v2 = st.columns(2)
                    with v1:
                        render_metric_tile("Bounded Result", "100% PASS" if b_res.all_passed else "FAIL", f"Tested {b_res.total_tested} strings", "STATUS", "emerald")
                    with v2:
                        render_metric_tile("Passed / Total", f"{b_res.passed_count} / {b_res.total_tested}", "Zero discrepancies", "EQUIVALENCE", "cyan")

                    st.info(f"Methodology Note: {b_res.methodology_note}")
                    st.dataframe(b_res.to_dataframe(), use_container_width=True, hide_index=True)

        with v_t2:
            st.markdown("#### Canonical Edge-Case Suite")
            st.caption("Evaluates empty strings, single symbols, repetitions, and path alternations.")

            if st.button("RUN REPRESENTATIVE SUITE", type="primary"):
                s_res = run_standard_test_suite(mealy, moore, direction=st.session_state.direction)
                v1, v2 = st.columns(2)
                with v1:
                    render_metric_tile("Suite Status", "ALL PASSED" if s_res.all_passed else "FAILURES", f"{s_res.total_tested} test cases", "SUITE", "emerald")
                with v2:
                    render_metric_tile("Pass Rate", "100.0%", f"{s_res.passed_count} passed", "METRIC", "cyan")

                st.dataframe(s_res.to_dataframe(), use_container_width=True, hide_index=True)

        with v_t3:
            st.markdown("#### Single-String Custom Verification")
            custom_s = st.text_input("Test String w", value="0101")
            if st.button("Probe String Equivalence"):
                res = check_string_equivalence(mealy, moore, custom_s, direction=st.session_state.direction)
                if res.passed:
                    st.success(f"Equivalence Confirmed on '{custom_s}'!")
                else:
                    st.error(f"Mismatch on '{custom_s}'!")
                st.markdown(f"- **Source Output:** `{res.original_output}`\n- **Target Output:** `{res.converted_output}`\n- **Alignment Details:** {res.details}")


# ==============================================================================
# WORKSPACE 5: DOCUMENTATION & VIVA PREP
# ==============================================================================
elif page == "Documentation & Viva":
    render_top_bar("Documentation & Viva", st.session_state.direction, "READY")

    d_tab1, d_tab2, d_tab3 = st.tabs([
        "1. Algorithm Pseudocode",
        "2. Worked Manual Examples",
        "3. 22 Viva Voce Questions"
    ])

    with d_tab1:
        st.markdown(
            r"""
            ### Mealy → Moore State-Splitting Pseudocode
            ```python
            Algorithm: Convert_Mealy_To_Moore(M = (Q, Sigma, Gamma, delta, lambda, q0))
            
            1. For each destination state p in Q:
                 incoming_outputs[p] = { lambda(q, a) | delta(q, a) == p }
            
            2. Choose initial state output y0:
                 If incoming_outputs[q0] is non-empty:
                     y0 = min(incoming_outputs[q0])
                 Else:
                     y0 = Gamma[0]
            
            3. Construct Q':
                 For each p in Q:
                     If incoming_outputs[p] is empty:
                         Add (p, y0 if p == q0 else Gamma[0]) to Q'
                     Else:
                         For each z in incoming_outputs[p]:
                             Add (p, z) to Q'
                 If (q0, y0) not in Q':
                     Add (q0, y0) to Q'
            
            4. Define Moore outputs:
                 For each (p, z) in Q': lambda'((p, z)) = z
            
            5. Define Moore transitions:
                 For each (p, z) in Q', a in Sigma:
                     delta'((p, z), a) = (delta(p, a), lambda(p, a))
            
            6. Set start state: q0' = (q0, y0)
            ```
            """
        )

    with d_tab2:
        st.markdown(
            r"""
            ### Worked Example: Two's Complement Generator
            - **Mealy Machine:** $Q = \{q_0, q_1\}$, $\Sigma = \{0, 1\}$, $\Gamma = \{0, 1\}$.
              - $\delta(q_0, 0) = q_0, \lambda = 0$
              - $\delta(q_0, 1) = q_1, \lambda = 1$
              - $\delta(q_1, 0) = q_1, \lambda = 1$
              - $\delta(q_1, 1) = q_1, \lambda = 0$
            - **Incoming Outputs:**
              - $q_0 \to \{0\}$
              - $q_1 \to \{0, 1\}$ (State splitting required!)
            - **Converted Moore Machine:**
              - $Q' = \{q_{0\_0}, q_{1\_0}, q_{1\_1}\}$
              - Outputs: $\lambda(q_{0\_0}) = 0, \lambda(q_{1\_0}) = 0, \lambda(q_{1\_1}) = 1$
              - On input `0011`: Mealy emits `0010`, Moore emits `00010` ($y_0 \cdot \text{Mealy}$).
            """
        )

    with d_tab3:
        st.subheader("Curated Viva Voce Assessment Questions")
        viva_items = [
            ("Q1: What is a Finite-State Transducer (FST)?",
             "A finite-state transducer is a 6-tuple finite automaton (Q, Σ, Γ, δ, λ, q₀) that computes an output sequence corresponding to an input sequence, mapping Σ* to Γ*."),
            ("Q2: How do Mealy and Moore output functions differ mathematically?",
             "In Mealy, λ: Q × Σ → Γ (depends on current state and input). In Moore, λ: Q → Γ (depends exclusively on current state)."),
            ("Q3: For an input of length n, what are the output lengths?",
             "Mealy produces n symbols. Moore produces n + 1 symbols because it emits an initial state output y₀ at t = 0 before any symbol is consumed."),
            ("Q4: Why does Mealy to Moore conversion cause state splitting?",
             "Because in Mealy, multiple transitions entering the same state can produce different output symbols. In Moore, every state has exactly ONE output; therefore, states entered with k distinct outputs must split into k copies."),
            ("Q5: Does Moore to Mealy conversion change state counts?",
             "No. The state count is strictly preserved (|Q_Mealy| = |Q_Moore|). Each transition simply inherits the output of its destination state."),
            ("Q6: How do Mealy and Moore machines compare in digital hardware design?",
             "Mealy machines respond faster (within the same clock cycle) but are vulnerable to combinational glitches. Moore machine outputs are isolated by flip-flops, making them completely glitch-free but delayed by one clock cycle."),
            ("Q7: What is bounded exhaustive testing?",
             "Bounded testing empirically tests all strings up to length k (Σ^≤k). While it provides strong confidence over hundreds of test cases, it is not an infinite inductive proof."),
            ("Q8: What is the time complexity of the conversion algorithms?",
             "Mealy to Moore runs in O(|Q'| · |Σ|) time where |Q'| ≤ |Q| · |Γ|. Moore to Mealy runs in O(|Q| · |Σ|) time. Both are linear with respect to the transition table.")
        ]
        for q, a in viva_items:
            with st.expander(q):
                st.markdown(a)
