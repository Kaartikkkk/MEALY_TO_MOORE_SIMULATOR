"""
Unit tests for Mealy to Moore conversion algorithm.
"""

import pytest
from src.models import MealyMachine
from src.mealy_to_moore import convert_mealy_to_moore
from src.examples import get_mealy_examples
from src.validation import validate_moore


def test_mealy_to_moore_state_splitting():
    """
    Test that state splitting correctly increases state count.
    In the Two's Complement preset:
    - Original states: |Q| = 2 (q0, q1)
    - q1 receives incoming outputs 0 and 1, so it splits into 2 Moore copies.
    - Resulting Moore machine must have at least 3 states.
    """
    presets = get_mealy_examples()
    twos_comp = presets["Two's Complement Generator (Forces State Splitting)"]
    
    moore, steps = convert_mealy_to_moore(twos_comp)
    
    # State count must increase
    assert len(moore.states) > len(twos_comp.states)
    assert len(moore.states) == 3  # q0_0, q1_1, q1_0
    
    # Validate resulting Moore machine structurally
    val = validate_moore(moore)
    assert val.is_valid, f"Converted Moore machine invalid: {val.errors}"
    
    # Check that steps are generated
    assert len(steps) >= 6
    assert steps[0].step_number == 1


def test_mealy_to_moore_multi_split():
    """Test comprehensive multi-state splitting."""
    presets = get_mealy_examples()
    splitter = presets["Multi-State Splitter (Comprehensive Split)"]
    
    moore, steps = convert_mealy_to_moore(splitter)
    
    assert len(moore.states) > len(splitter.states)
    val = validate_moore(moore)
    assert val.is_valid


def test_mealy_to_moore_transient_initial_state():
    """Test case where initial state has no incoming transitions."""
    presets = get_mealy_examples()
    transient = presets["Transient Initial State with Self-Loops"]
    
    moore, steps = convert_mealy_to_moore(transient)
    val = validate_moore(moore)
    assert val.is_valid
    assert moore.initial_state in moore.states


def test_mealy_to_moore_custom_initial_output():
    """Test passing an explicit initial output."""
    m = MealyMachine(
        states=["A"],
        input_alphabet=["0"],
        output_alphabet=["x", "y"],
        transitions={("A", "0"): "A"},
        outputs={("A", "0"): "x"},
        initial_state="A"
    )
    moore, _ = convert_mealy_to_moore(m, initial_output="y")
    assert moore.outputs[moore.initial_state] == "y"


def test_mealy_to_moore_invalid_initial_output_raises():
    m = MealyMachine(
        states=["A"],
        input_alphabet=["0"],
        output_alphabet=["x", "y"],
        transitions={("A", "0"): "A"},
        outputs={("A", "0"): "x"},
        initial_state="A"
    )
    with pytest.raises(ValueError, match="not in Γ"):
        convert_mealy_to_moore(m, initial_output="invalid_sym")
