"""
Theme and Design System for Automata Lab.
Provides CSS variables, component styling, typography, and light-theme tokens.
Designed for high-contrast academic software and modern scientific developer tools.
"""

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --lab-bg-main: #F8FAFC;
    --lab-bg-surface: #FFFFFF;
    --lab-bg-surface-elevated: #F1F5F9;
    --lab-bg-surface-hover: #E2E8F0;
    --lab-border: #E2E8F0;
    --lab-border-strong: #CBD5E1;
    --lab-border-focus: #2563EB;
    --lab-text-primary: #0F172A;
    --lab-text-secondary: #475569;
    --lab-text-muted: #64748B;
    --lab-cyan: #0284C7;
    --lab-violet: #7C3AED;
    --lab-amber: #D97706;
    --lab-moore-blue: #0284C7;
    --lab-emerald: #059669;
    --lab-rose: #DC2626;
}

/* Global Application Surface */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    color: var(--lab-text-primary);
}

.stApp {
    background-color: #F8FAFC !important;
    background: radial-gradient(circle at 15% 10%, #FFFFFF 0%, #F1F5F9 100%) !important;
}

/* Subtle Graph / Grid Overlay for light mode */
.stApp::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: 
        radial-gradient(#CBD5E1 1.2px, transparent 1.2px);
    background-size: 24px 24px;
    pointer-events: none;
    z-index: 0;
    opacity: 0.65;
}

/* Code & Monospace Elements */
code, pre, .mono-font {
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: -0.02em;
}

/* Compact, Refined Sidebar in light theme */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid var(--lab-border) !important;
    padding-top: 1.5rem !important;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.02) !important;
}

[data-testid="stSidebar"] .stRadio label {
    color: #475569 !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 6px 10px !important;
    border-radius: 6px !important;
    transition: all 0.15s ease-in-out !important;
}

[data-testid="stSidebar"] .stRadio label:hover {
    color: #2563EB !important;
    background: #EFF6FF !important;
}

/* Top App Breadcrumb & Status Bar */
.lab-top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 18px;
    background: #FFFFFF;
    border: 1px solid var(--lab-border);
    border-radius: 10px;
    margin-bottom: 22px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.lab-breadcrumb {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.82rem;
    color: var(--lab-text-muted);
}

.lab-breadcrumb-active {
    color: var(--lab-cyan);
    font-weight: 600;
}

.lab-status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.76rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 3px 10px;
    border-radius: 9999px;
}

.lab-status-ready {
    background: #ECFDF5;
    color: #059669;
    border: 1px solid #A7F3D0;
}

.lab-status-active {
    background: #EFF6FF;
    color: #2563EB;
    border: 1px solid #BFDBFE;
}

/* Modern Card & Panel Layouts */
.lab-panel {
    background: #FFFFFF;
    border: 1px solid var(--lab-border);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 18px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
    position: relative;
    overflow: hidden;
}

.lab-panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--lab-border);
    padding-bottom: 10px;
}

.lab-panel-title {
    font-size: 0.98rem;
    font-weight: 600;
    color: var(--lab-text-primary);
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Hero Section */
.lab-hero-card {
    background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
    border: 1px solid #CBD5E1;
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 24px;
    position: relative;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
}

.lab-hero-title {
    font-size: 1.85rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #0F172A;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.lab-hero-subtitle {
    font-size: 0.96rem;
    color: var(--lab-text-secondary);
    line-height: 1.5;
    max-width: 780px;
    margin-bottom: 20px;
}

/* Stat & Metric Tiles */
.lab-metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 14px;
    margin: 16px 0;
}

.lab-metric-tile {
    background: #FFFFFF;
    border: 1px solid var(--lab-border);
    border-radius: 10px;
    padding: 14px 18px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}

.lab-metric-tile:hover {
    border-color: #93C5FD;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08);
}

.lab-metric-label {
    font-size: 0.74rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--lab-text-muted);
    margin-bottom: 4px;
}

.lab-metric-val {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--lab-text-primary);
    font-family: 'JetBrains Mono', monospace;
}

.lab-metric-sub {
    font-size: 0.76rem;
    color: var(--lab-text-secondary);
    margin-top: 2px;
}

/* Badges */
.lab-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 8px;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 5px;
    font-family: 'JetBrains Mono', monospace;
}

.lab-badge-mealy {
    background: #FEF3C7;
    color: #B45309;
    border: 1px solid #FDE68A;
}

.lab-badge-moore {
    background: #E0F2FE;
    color: #0369A1;
    border: 1px solid #BAE6FD;
}

.lab-badge-cyan {
    background: #EFF6FF;
    color: #1D4ED8;
    border: 1px solid #BFDBFE;
}

.lab-badge-violet {
    background: #F3E8FF;
    color: #6D28D9;
    border: 1px solid #DDD6FE;
}

.lab-badge-emerald {
    background: #ECFDF5;
    color: #15803D;
    border: 1px solid #A7F3D0;
}

.lab-badge-rose {
    background: #FEF2F2;
    color: #B91C1C;
    border: 1px solid #FECACA;
}

/* Execution Path Chips */
.lab-path-flow {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    background: #F8FAFC;
    border: 1px solid var(--lab-border);
    border-radius: 8px;
    margin: 12px 0;
}

.lab-path-node {
    background: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    padding: 3px 10px;
    border-radius: 5px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    font-size: 0.86rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.lab-path-node.active-state {
    background: #2563EB;
    color: #FFFFFF;
    border-color: #1D4ED8;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
}

.lab-path-arrow {
    color: var(--lab-text-muted);
    font-size: 0.8rem;
}

/* Button & Control Refinements */
button[kind="primary"] {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
    border: none !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 8px 18px !important;
    box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25) !important;
    transition: all 0.15s ease-in-out !important;
}

button[kind="primary"]:hover {
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
    transform: translateY(-1px) !important;
}

button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    color: #334155 !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
}

button[kind="secondary"]:hover {
    border-color: #2563EB !important;
    color: #2563EB !important;
    background: #F8FAFC !important;
}

/* Custom Scrollbar for Light Theme */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #F1F5F9;
}
::-webkit-scrollbar-thumb {
    background: #CBD5E1;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #94A3B8;
}
</style>
"""


def apply_theme():
    import streamlit as st
    st.markdown(THEME_CSS, unsafe_allow_html=True)
