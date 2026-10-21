"""
Automata Visualization Engine.
Generates Graphviz DOT source strings and Mermaid diagram definitions for Mealy and Moore machines.
Provides graceful fallbacks and dual-rendering capabilities.
"""

from typing import Dict, List, Tuple
from .models import MealyMachine, MooreMachine


def generate_mealy_dot(machine: MealyMachine) -> str:
    """
    Generates a Graphviz DOT representation for a Mealy Machine:
    - States as circles
    - Start state highlighted with an incoming arrow from an invisible anchor
    - Transitions labeled as 'input / output'
    """
    lines = [
        'digraph MealyMachine {',
        '  rankdir=LR;',
        '  bgcolor="transparent";',
        '  node [fontname="Inter, Roboto, sans-serif", fontsize=12, shape=circle, style="filled", fillcolor="#F8FAFC", color="#334155", penwidth=1.8];',
        '  edge [fontname="Inter, Roboto, sans-serif", fontsize=11, color="#475569", arrowsize=0.8, penwidth=1.4];',
        '',
        '  // Invisible start anchor',
        '  __start [shape=none, label="", width=0, height=0];',
        f'  __start -> "{machine.initial_state}" [label="start", color="#2563EB", fontcolor="#2563EB", penwidth=2.0];',
        ''
    ]

    # Style initial state specially
    for q in machine.states:
        if q == machine.initial_state:
            lines.append(f'  "{q}" [label="{q}", color="#2563EB", fillcolor="#EFF6FF", penwidth=2.4];')
        else:
            lines.append(f'  "{q}" [label="{q}"];')

    lines.append('')

    # Group transitions between same (src, dest)
    edge_groups: Dict[Tuple[str, str], List[str]] = {}
    for (q, a), nxt in machine.transitions.items():
        out = machine.outputs.get((q, a), "?")
        label = f"{a} / {out}"
        edge_groups.setdefault((q, nxt), []).append(label)

    for (src, dest), labels in edge_groups.items():
        combined_label = "\\n".join(labels)
        lines.append(f'  "{src}" -> "{dest}" [label="  {combined_label}  "];')

    lines.append('}')
    return "\n".join(lines)


def generate_moore_dot(machine: MooreMachine) -> str:
    """
    Generates a Graphviz DOT representation for a Moore Machine:
    - States as Mrecord / divided nodes displaying State Name and State Output
    - Start state highlighted
    - Transitions labeled with input symbol only
    """
    lines = [
        'digraph MooreMachine {',
        '  rankdir=LR;',
        '  bgcolor="transparent";',
        '  node [fontname="Inter, Roboto, sans-serif", fontsize=12, shape=Mrecord, style="filled", fillcolor="#F8FAFC", color="#334155", penwidth=1.8];',
        '  edge [fontname="Inter, Roboto, sans-serif", fontsize=11, color="#475569", arrowsize=0.8, penwidth=1.4];',
        '',
        '  // Invisible start anchor',
        '  __start [shape=none, label="", width=0, height=0];',
        f'  __start -> "{machine.initial_state}" [label="start", color="#16A34A", fontcolor="#16A34A", penwidth=2.0];',
        ''
    ]

    for q in machine.states:
        out = machine.outputs.get(q, "-")
        record_label = f"{{ {q} | out: {out} }}"
        if q == machine.initial_state:
            lines.append(f'  "{q}" [label="{record_label}", color="#16A34A", fillcolor="#F0FDF4", penwidth=2.4];')
        else:
            lines.append(f'  "{q}" [label="{record_label}"];')

    lines.append('')

    # Group transitions between same (src, dest)
    edge_groups: Dict[Tuple[str, str], List[str]] = {}
    for (q, a), nxt in machine.transitions.items():
        edge_groups.setdefault((q, nxt), []).append(a)

    for (src, dest), symbols in edge_groups.items():
        combined_label = ", ".join(symbols)
        lines.append(f'  "{src}" -> "{dest}" [label="  {combined_label}  "];')

    lines.append('}')
    return "\n".join(lines)


def generate_mealy_mermaid(machine: MealyMachine) -> str:
    """
    Generates a Mermaid stateDiagram-v2 as a robust fallback.
    """
    lines = [
        'stateDiagram-v2',
        f'    [*] --> {machine.initial_state}'
    ]

    edge_groups: Dict[Tuple[str, str], List[str]] = {}
    for (q, a), nxt in machine.transitions.items():
        out = machine.outputs.get((q, a), "?")
        edge_groups.setdefault((q, nxt), []).append(f"{a} / {out}")

    for (src, dest), labels in edge_groups.items():
        combined = ", ".join(labels)
        lines.append(f'    {src} --> {dest}: {combined}')

    return "\n".join(lines)


def generate_moore_mermaid(machine: MooreMachine) -> str:
    """
    Generates a Mermaid stateDiagram-v2 for Moore machines.
    """
    lines = [
        'stateDiagram-v2',
        f'    [*] --> {machine.initial_state}'
    ]

    for q in machine.states:
        out = machine.outputs.get(q, "-")
        # Sanitize for mermaid state name
        safe_id = q.replace("-", "_")
        lines.append(f'    {safe_id}: {q} [out={out}]')

    edge_groups: Dict[Tuple[str, str], List[str]] = {}
    for (q, a), nxt in machine.transitions.items():
        edge_groups.setdefault((q, nxt), []).append(a)

    for (src, dest), symbols in edge_groups.items():
        safe_src = src.replace("-", "_")
        safe_dest = dest.replace("-", "_")
        combined = ", ".join(symbols)
        lines.append(f'    {safe_src} --> {safe_dest}: {combined}')

    return "\n".join(lines)
