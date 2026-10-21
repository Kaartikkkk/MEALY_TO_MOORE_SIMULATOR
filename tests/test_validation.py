"""
Unit tests for Mealy and Moore machine validation.
"""

import pytest
from src.models import MealyMachine, MooreMachine
from src.validation import validate_mealy, validate_moore
from src.examples import get_mealy_examples, get_moore_examples


def test_valid_mealy_presets():
    presets = get_mealy_examples()
    for name, machine in presets.items():
        res = validate_mealy(machine)
        assert res.is_valid, f"Preset '{name}' failed validation: {res.errors}"


def test_valid_moore_presets():
    presets = get_moore_examples()
    for name, machine in presets.items():
        res = validate_moore(machine)
        assert res.is_valid, f"Preset '{name}' failed validation: {res.errors}"


def test_mealy_missing_state():
    m = MealyMachine(
        states=[],
        input_alphabet=["0", "1"],
        output_alphabet=["0", "1"],
        transitions={},
        outputs={},
        initial_state="q0"
    )
    res = validate_mealy(m)
    assert not res.is_valid
    assert any("State set Q cannot be empty" in e for e in res.errors)


def test_mealy_invalid_initial_state():
    m = MealyMachine(
        states=["q0", "q1"],
        input_alphabet=["0", "1"],
        output_alphabet=["0", "1"],
        transitions={
            ("q0", "0"): "q0", ("q0", "1"): "q1",
            ("q1", "0"): "q0", ("q1", "1"): "q1",
        },
        outputs={
            ("q0", "0"): "0", ("q0", "1"): "1",
            ("q1", "0"): "0", ("q1", "1"): "1",
        },
        initial_state="q_unknown"
    )
    res = validate_mealy(m)
    assert not res.is_valid
    assert any("Initial state 'q_unknown' is not in" in e for e in res.errors)


def test_mealy_missing_transition():
    m = MealyMachine(
        states=["q0", "q1"],
        input_alphabet=["0", "1"],
        output_alphabet=["0", "1"],
        transitions={
            ("q0", "0"): "q0",
            # missing (q0, 1)
            ("q1", "0"): "q0", ("q1", "1"): "q1",
        },
        outputs={
            ("q0", "0"): "0", ("q0", "1"): "1",
            ("q1", "0"): "0", ("q1", "1"): "1",
        },
        initial_state="q0"
    )
    res = validate_mealy(m)
    assert not res.is_valid
    assert any("Missing transition" in e for e in res.errors)


def test_mealy_missing_output():
    m = MealyMachine(
        states=["q0"],
        input_alphabet=["0"],
        output_alphabet=["0", "1"],
        transitions={("q0", "0"): "q0"},
        outputs={},  # missing output for (q0, 0)
        initial_state="q0"
    )
    res = validate_mealy(m)
    assert not res.is_valid
    assert any("Missing output" in e for e in res.errors)


def test_moore_missing_state_output():
    m = MooreMachine(
        states=["q0", "q1"],
        input_alphabet=["0"],
        output_alphabet=["0", "1"],
        transitions={("q0", "0"): "q1", ("q1", "0"): "q0"},
        outputs={"q0": "0"},  # missing q1 output
        initial_state="q0"
    )
    res = validate_moore(m)
    assert not res.is_valid
    assert any("Missing state output" in e for e in res.errors)


def test_unreachable_state_warning():
    # q2 is unreachable
    m = MealyMachine(
        states=["q0", "q1", "q2"],
        input_alphabet=["0"],
        output_alphabet=["0"],
        transitions={
            ("q0", "0"): "q1",
            ("q1", "0"): "q0",
            ("q2", "0"): "q2",
        },
        outputs={
            ("q0", "0"): "0",
            ("q1", "0"): "0",
            ("q2", "0"): "0",
        },
        initial_state="q0"
    )
    res = validate_mealy(m)
    assert res.is_valid
    assert len(res.warnings) > 0
    assert any("unreachable" in w.lower() for w in res.warnings)
