"""
Custom SVG State Diagram Engine for Automata Lab.
Renders responsive, theme-tailored vector state diagrams for Mealy and Moore machines.
Supports edge curvature, self-loops, initial-state vectors, and live state/transition highlighting.
"""

import math
import html
from typing import Dict, List, Tuple, Optional, Set
from ..models import MealyMachine, MooreMachine


def _compute_state_positions(
    states: List[str],
    width: int = 580,
    height: int = 340
) -> Dict[str, Tuple[float, float]]:
    """Computes harmonic coordinates (x, y) for states in the viewport."""
    n = len(states)
    cx, cy = width / 2, height / 2

    if n == 1:
        return {states[0]: (cx, cy)}
    elif n == 2:
        return {
            states[0]: (cx - 130, cy),
            states[1]: (cx + 130, cy)
        }
    elif n == 3:
        # Equilateral triangle
        r = min(width, height) * 0.36
        angles = [-math.pi / 2, -math.pi / 2 + 2 * math.pi / 3, -math.pi / 2 + 4 * math.pi / 3]
        return {
            states[i]: (cx + r * math.cos(angles[i]), cy + r * math.sin(angles[i]) * 0.9)
            for i in range(3)
        }
    elif n == 4:
        # Balanced rectangle
        dx, dy = 140, 95
        return {
            states[0]: (cx - dx, cy - dy),
            states[1]: (cx + dx, cy - dy),
            states[2]: (cx + dx, cy + dy),
            states[3]: (cx - dx, cy + dy)
        }
    else:
        # Elliptical distribution
        rx = min(width * 0.40, 230)
        ry = min(height * 0.38, 125)
        pos = {}
        for i, s in enumerate(states):
            theta = -math.pi / 2 + (2 * math.pi * i / n)
            pos[s] = (cx + rx * math.cos(theta), cy + ry * math.sin(theta))
        return pos


def render_svg_state_diagram(
    machine,
    width: int = 580,
    height: int = 340,
    active_state: Optional[str] = None,
    active_transition: Optional[Tuple[str, str]] = None,
    container_id: str = "fst_diagram"
) -> str:
    """
    Renders an arbitrary Mealy or Moore machine as an interactive, responsive SVG diagram.
    """
    is_mealy = isinstance(machine, MealyMachine)
    states = machine.states
    pos = _compute_state_positions(states, width, height)
    node_radius = 28 if len(states) <= 4 else 24

    # Group transitions between (src, dest)
    edge_groups: Dict[Tuple[str, str], List[Tuple[str, str]]] = {}
    for (src, sym), dest in machine.transitions.items():
        out_sym = machine.outputs.get((src, sym), "") if is_mealy else machine.outputs.get(dest, "")
        edge_groups.setdefault((src, dest), []).append((sym, out_sym))

    # Detect pairs that have bidirectional transitions
    bidirectional_pairs: Set[Tuple[str, str]] = set()
    for (src, dest) in edge_groups.keys():
        if (dest, src) in edge_groups and src != dest:
            bidirectional_pairs.add((src, dest))

    svg_parts = [
        f'<svg id="{container_id}" viewBox="0 0 {width} {height}" '
        f'style="width: 100%; height: auto; max-height: {height}px; background: #FFFFFF; '
        f'border-radius: 10px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05); overflow: visible;" '
        f'xmlns="http://www.w3.org/2000/svg">',
        '''
        <defs>
            <marker id="arrow-cyan" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#2563EB" />
            </marker>
            <marker id="arrow-amber" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#D97706" />
            </marker>
            <marker id="arrow-moore" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#0284C7" />
            </marker>
            <marker id="arrow-dim" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#94A3B8" />
            </marker>
            <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
        </defs>
        '''
    ]

    # 1. Render Start State Vector
    q0 = machine.initial_state
    if q0 in pos:
        q0_x, q0_y = pos[q0]
        start_dx = -50
        arrow_marker = "url(#arrow-amber)" if is_mealy else "url(#arrow-moore)"
        vector_color = "#D97706" if is_mealy else "#0284C7"

        svg_parts.append(f'''
            <g class="start-vector">
                <line x1="{q0_x + start_dx}" y1="{q0_y}" x2="{q0_x - node_radius - 2}" y2="{q0_y}"
                      stroke="{vector_color}" stroke-width="2.2" stroke-linecap="round" marker-end="{arrow_marker}" />
                <text x="{q0_x + start_dx - 4}" y="{q0_y + 4}" fill="{vector_color}"
                      font-size="10" font-family="JetBrains Mono, monospace" font-weight="700" text-anchor="end">START</text>
            </g>
        ''')

    # 2. Render Transition Edges
    for (src, dest), trans_list in edge_groups.items():
        if src not in pos or dest not in pos:
            continue

        x1, y1 = pos[src]
        x2, y2 = pos[dest]

        # Check if this edge is active
        is_edge_active = False
        if active_transition is not None and active_transition[0] == src:
            for sym, _ in trans_list:
                if sym == active_transition[1]:
                    is_edge_active = True
                    break

        stroke_color = "#2563EB" if is_edge_active else "#64748B"
        stroke_width = "2.4" if is_edge_active else "1.6"
        marker_id = "arrow-cyan" if is_edge_active else ("arrow-amber" if is_mealy else "arrow-moore")

        # Format label
        if is_mealy:
            label_text = ", ".join(f"{sym}/{out}" for sym, out in trans_list)
        else:
            label_text = ", ".join(sym for sym, _ in trans_list)

        if src == dest:
            # Self-loop
            loop_r = 30
            loop_x1 = x1 - 10
            loop_y1 = y1 - node_radius
            loop_x2 = x1 + 10
            loop_y2 = y1 - node_radius
            cp1_x, cp1_y = x1 - loop_r, y1 - node_radius - loop_r * 1.6
            cp2_x, cp2_y = x1 + loop_r, y1 - node_radius - loop_r * 1.6

            path_d = f"M {loop_x1} {loop_y1} C {cp1_x} {cp1_y}, {cp2_x} {cp2_y}, {loop_x2} {loop_y2}"
            label_x = x1
            label_y = y1 - node_radius - loop_r * 1.35

            svg_parts.append(f'''
                <path d="{path_d}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_width}"
                      marker-end="url(#{marker_id})" />
                <rect x="{label_x - len(label_text)*4.5}" y="{label_y - 9}" width="{len(label_text)*9 + 6}" height="15"
                      rx="3" fill="#FFFFFF" stroke="{stroke_color}" stroke-width="0.8"/>
                <text x="{label_x}" y="{label_y + 2}" fill="#0F172A" font-size="10"
                      font-family="JetBrains Mono, monospace" font-weight="600" text-anchor="middle">{html.escape(label_text)}</text>
            ''')
        else:
            # Curved transition between distinct nodes
            dx, dy = x2 - x1, y2 - y1
            dist = math.hypot(dx, dy)
            if dist == 0:
                dist = 1
            ux, uy = dx / dist, dy / dist
            nx, ny = -uy, ux  # Normal vector

            # Curve offset
            curve_offset = 24 if (src, dest) in bidirectional_pairs else 12

            # Start and end adjusted for node radius
            sx = x1 + ux * node_radius
            sy = y1 + uy * node_radius
            ex = x2 - ux * (node_radius + 4)
            ey = y2 - uy * (node_radius + 4)

            # Control point for quadratic Bézier
            cpx = (x1 + x2) / 2 + nx * curve_offset
            cpy = (y1 + y2) / 2 + ny * curve_offset

            path_d = f"M {sx} {sy} Q {cpx} {cpy} {ex} {ey}"

            # Label at midpoint of curve
            lx = 0.25 * sx + 0.5 * cpx + 0.25 * ex + nx * 5
            ly = 0.25 * sy + 0.5 * cpy + 0.25 * ey + ny * 5

            svg_parts.append(f'''
                <path d="{path_d}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_width}"
                      marker-end="url(#{marker_id})" />
                <rect x="{lx - len(label_text)*4.2 - 2}" y="{ly - 8}" width="{len(label_text)*8.4 + 4}" height="14"
                      rx="3" fill="#FFFFFF" stroke="{stroke_color}" stroke-width="0.8"/>
                <text x="{lx}" y="{ly + 2}" fill="#0F172A" font-size="9.5"
                      font-family="JetBrains Mono, monospace" font-weight="600" text-anchor="middle">{html.escape(label_text)}</text>
            ''')

    # 3. Render State Nodes
    for s in states:
        x, y = pos[s]
        is_active = (s == active_state)
        is_initial = (s == machine.initial_state)

        # Mealy vs Moore styling
        if is_mealy:
            stroke = "#2563EB" if is_active else ("#D97706" if is_initial else "#94A3B8")
            fill = "#EFF6FF" if is_active else "#FFFFFF"
            stroke_width = "2.8" if is_active or is_initial else "1.8"

            pulse_svg = f'<circle cx="{x}" cy="{y}" r="{node_radius + 6}" fill="none" stroke="#2563EB" stroke-width="2" stroke-dasharray="4 2" opacity="0.8"/>' if is_active else ""

            svg_parts.append(f'''
                <g class="state-node" id="node-{s}">
                    {pulse_svg}
                    <circle cx="{x}" cy="{y}" r="{node_radius}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" />
                    <text x="{x}" y="{y + 4}" fill="#0F172A" font-size="12" font-weight="700"
                          font-family="JetBrains Mono, monospace" text-anchor="middle">{html.escape(s)}</text>
                </g>
            ''')
        else:
            # Moore Machine: Show State Name and State Output
            state_out = machine.outputs.get(s, "-")
            stroke = "#2563EB" if is_active else ("#0284C7" if is_initial else "#94A3B8")
            fill = "#EFF6FF" if is_active else "#FFFFFF"
            stroke_width = "2.8" if is_active or is_initial else "1.8"

            pulse_svg = f'<circle cx="{x}" cy="{y}" r="{node_radius + 6}" fill="none" stroke="#2563EB" stroke-width="2" stroke-dasharray="4 2" opacity="0.8"/>' if is_active else ""

            # Dual badge inside node
            svg_parts.append(f'''
                <g class="state-node" id="node-{s}">
                    {pulse_svg}
                    <circle cx="{x}" cy="{y}" r="{node_radius}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" />
                    <text x="{x}" y="{y - 3}" fill="#0F172A" font-size="11" font-weight="700"
                          font-family="JetBrains Mono, monospace" text-anchor="middle">{html.escape(s)}</text>
                    <rect x="{x - 14}" y="{y + 4}" width="28" height="12" rx="3" fill="#E0F2FE" stroke="#BAE6FD" stroke-width="0.8"/>
                    <text x="{x}" y="{y + 13}" fill="#0369A1" font-size="8.5" font-weight="700"
                          font-family="JetBrains Mono, monospace" text-anchor="middle">{html.escape(state_out)}</text>
                </g>
            ''')

    svg_parts.append('</svg>')
    clean_lines = [line.strip() for line in "\n".join(svg_parts).splitlines() if line.strip()]
    return "\n".join(clean_lines)


def display_svg_diagram(
    machine,
    width: int = 580,
    height: int = 340,
    active_state: Optional[str] = None,
    active_transition: Optional[Tuple[str, str]] = None,
    container_id: str = "fst_diagram"
):
    """Safely renders and embeds the SVG state diagram using Streamlit's official components.html iframe container."""
    import streamlit.components.v1 as components
    svg_code = render_svg_state_diagram(
        machine=machine,
        width=width,
        height=height,
        active_state=active_state,
        active_transition=active_transition,
        container_id=container_id
    )
    iframe_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: transparent;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
  }}
  svg {{
    width: 100%;
    height: auto;
  }}
</style>
</head>
<body>
{svg_code}
</body>
</html>"""
    components.html(iframe_content, height=height + 16)


