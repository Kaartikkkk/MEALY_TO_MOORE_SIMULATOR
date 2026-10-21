"""
Reusable UI Components for Automata Lab.
Provides top navigation bars, hero headers, metric tiles, and status indicators.
"""

import html
import textwrap
from typing import Optional
import streamlit as st
from .icons import get_svg_icon


def _html(s: str):
    clean = textwrap.dedent(s).strip()
    if hasattr(st, "html"):
        st.html(clean)
    else:
        st.markdown(clean, unsafe_allow_html=True)


def render_top_bar(
    page_name: str,
    direction: str,
    status: str = "READY",
    is_validated: bool = True
):
    """Renders the top application status and breadcrumb bar."""
    status_class = "lab-status-ready" if is_validated else "lab-status-active"
    status_icon = get_svg_icon("check" if is_validated else "cpu", size=14)

    bar_html = f"""<div class="lab-top-bar">
<div class="lab-breadcrumb">
<span>{get_svg_icon("logo", size=16, color="#2563EB")}</span>
<span>AUTOMATA LAB</span>
<span>/</span>
<span class="lab-breadcrumb-active">{html.escape(page_name)}</span>
</div>
<div style="display: flex; align-items: center; gap: 14px;">
<div style="font-size: 0.8rem; font-family: 'JetBrains Mono', monospace; color: var(--lab-text-secondary);">
MODE: <span style="color: var(--lab-cyan); font-weight: 600;">{html.escape(direction)}</span>
</div>
<div class="lab-status-badge {status_class}">
<span>{status_icon}</span>
<span>{html.escape(status)}</span>
</div>
</div>
</div>"""
    _html(bar_html)


def render_hero_banner():
    """Renders the master hero section on the Overview page."""
    logo_icon = get_svg_icon("logo", size=28, color="#2563EB")
    
    hero_html = f"""<div class="lab-hero-card">
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
<span class="lab-badge lab-badge-cyan">ACADEMIC LAB</span>
<span class="lab-badge lab-badge-violet">CSET302 AUTOMATA THEORY</span>
<span class="lab-badge lab-badge-mealy">TOPIC 14</span>
</div>
<div class="lab-hero-title">
<span>{logo_icon}</span>
<span>AUTOMATA LAB — Finite-State Transducer Studio</span>
</div>
<div class="lab-hero-subtitle">
A mathematical engineering laboratory for deterministic finite-state transducers. 
Explore state-splitting constructions, bidirectional <b>Mealy ↔ Moore</b> conversions, 
step-by-step algorithmic synthesis, vector diagrams, and bounded equivalence verification.
</div>
<svg width="100%" height="90" viewBox="0 0 700 90" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-top: 10px;">
<circle cx="60" cy="45" r="22" stroke="#D97706" stroke-width="2" fill="#FEF3C7"/>
<text x="60" y="49" fill="#0F172A" font-size="11" font-family="JetBrains Mono" font-weight="700" text-anchor="middle">q₀</text>
<circle cx="210" cy="45" r="22" stroke="#D97706" stroke-width="2" fill="#FEF3C7"/>
<text x="210" y="49" fill="#0F172A" font-size="11" font-family="JetBrains Mono" font-weight="700" text-anchor="middle">q₁</text>
<path d="M82 45H186" stroke="#2563EB" stroke-width="2" stroke-dasharray="4 3"/>
<text x="134" y="38" fill="#2563EB" font-size="10" font-family="JetBrains Mono" font-weight="600" text-anchor="middle">0 / 1</text>
<path d="M250 45H330" stroke="#7C3AED" stroke-width="2" stroke-linecap="round"/>
<polygon points="330,41 342,45 330,49" fill="#7C3AED"/>
<text x="290" y="36" fill="#6D28D9" font-size="9" font-family="JetBrains Mono" font-weight="700" text-anchor="middle">CONVERT</text>
<circle cx="410" cy="45" r="22" stroke="#0284C7" stroke-width="2" fill="#E0F2FE"/>
<text x="410" y="42" fill="#0F172A" font-size="10" font-family="JetBrains Mono" font-weight="700" text-anchor="middle">q₀_₀</text>
<text x="410" y="55" fill="#0369A1" font-size="8" font-family="JetBrains Mono" text-anchor="middle">λ=0</text>
<circle cx="560" cy="45" r="22" stroke="#0284C7" stroke-width="2" fill="#E0F2FE"/>
<text x="560" y="42" fill="#0F172A" font-size="10" font-family="JetBrains Mono" font-weight="700" text-anchor="middle">q₁_₁</text>
<text x="560" y="55" fill="#0369A1" font-size="8" font-family="JetBrains Mono" text-anchor="middle">λ=1</text>
<path d="M432 45H536" stroke="#0284C7" stroke-width="2"/>
<text x="484" y="38" fill="#0369A1" font-size="10" font-family="JetBrains Mono" font-weight="600" text-anchor="middle">0</text>
</svg>
</div>"""
    _html(hero_html)


def render_metric_tile(
    label: str,
    value: str,
    subtext: str = "",
    badge_label: Optional[str] = None,
    badge_type: str = "cyan"
):
    """Renders a high-tech metric tile."""
    badge_html = f'<span class="lab-badge lab-badge-{badge_type}" style="float: right;">{html.escape(badge_label)}</span>' if badge_label else ""
    tile_html = f"""<div class="lab-metric-tile">
{badge_html}
<div class="lab-metric-label">{html.escape(label)}</div>
<div class="lab-metric-val">{html.escape(value)}</div>
{"<div class='lab-metric-sub'>" + html.escape(subtext) + "</div>" if subtext else ""}
</div>"""
    _html(tile_html)
