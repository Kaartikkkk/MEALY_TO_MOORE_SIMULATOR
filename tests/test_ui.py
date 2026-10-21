"""
Unit tests for Automata Lab UI rendering and SVG generation.
Ensures that all generated SVGs and HTML components are well-formed and do not produce
CommonMark indented code blocks.
"""

import xml.etree.ElementTree as ET
from src.examples import get_mealy_examples, get_moore_examples
from src.models import MealyMachine, MooreMachine
from src.ui.svg_diagram import render_svg_state_diagram
from src.ui.icons import get_svg_icon, SVG_PATHS
from src.mealy_to_moore import convert_mealy_to_moore
from src.moore_to_mealy import convert_moore_to_mealy


def test_svg_diagram_mealy_validity():
    """Verify that all Mealy presets render valid SVG without markdown code block indentation."""
    for name, mealy in get_mealy_examples().items():
        svg = render_svg_state_diagram(mealy, width=540, height=320)
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")
        # Check that no line begins with 4 spaces (which triggers Markdown <pre><code>)
        for line in svg.splitlines():
            assert not line.startswith("    "), f"Line has 4-space indent: {line}"
        # Validate that the SVG is parseable XML
        root = ET.fromstring(svg)
        assert root.tag == "{http://www.w3.org/2000/svg}svg" or root.tag == "svg"


def test_svg_diagram_moore_validity():
    """Verify that all Moore presets render valid SVG without markdown code block indentation."""
    for name, moore in get_moore_examples().items():
        svg = render_svg_state_diagram(moore, width=540, height=320)
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")
        for line in svg.splitlines():
            assert not line.startswith("    "), f"Line has 4-space indent: {line}"
        root = ET.fromstring(svg)
        assert root.tag == "{http://www.w3.org/2000/svg}svg" or root.tag == "svg"


def test_conversion_dual_diagrams():
    """Test converted Mealy->Moore and Moore->Mealy machines render in SVG properly."""
    mealy = list(get_mealy_examples().values())[0]
    moore_conv, _ = convert_mealy_to_moore(mealy)

    svg = render_svg_state_diagram(moore_conv, active_state=moore_conv.initial_state)
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    ET.fromstring(svg)

    moore = list(get_moore_examples().values())[0]
    mealy_conv, _ = convert_moore_to_mealy(moore)
    svg2 = render_svg_state_diagram(mealy_conv, active_state=mealy_conv.initial_state)
    assert svg2.startswith("<svg")
    assert svg2.endswith("</svg>")
    ET.fromstring(svg2)


def test_svg_icons():
    """Verify that all registered icons in the SVG library render cleanly."""
    for icon_name in SVG_PATHS:
        icon_svg = get_svg_icon(icon_name, size=20)
        assert "<svg" in icon_svg
        assert "</svg>" in icon_svg
        assert not any(l.startswith("    ") for l in icon_svg.splitlines())
