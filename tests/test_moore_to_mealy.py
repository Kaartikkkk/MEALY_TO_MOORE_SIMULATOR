"""
Unit tests for Moore to Mealy conversion algorithm.
"""

import pytest
from src.models import MooreMachine
from src.moore_to_mealy import convert_moore_to_mealy
from src.examples import get_moore_examples
from src.validation import validate_mealy


def test_moore_to_mealy_state_preservation():
    """
    In Moore to Mealy conversion, the number of states must be preserved:
    |Q_Mealy| == |Q_Moore|.
    """
    presets = get_moore_examples()
    for name, moore in presets.items():
        mealy, steps = convert_moore_to_mealy(moore)
        
        # State count must match exactly
        assert len(mealy.states) == len(moore.states), f"State count mismatch on {name}"
        assert set(mealy.states) == set(moore.states)
        assert mealy.initial_state == moore.initial_state
        
        # Structurally validate resulting Mealy machine
        val = validate_mealy(mealy)
        assert val.is_valid, f"Converted Mealy machine invalid for {name}: {val.errors}"
        
        # Step trace verification
        assert len(steps) >= 5
        assert steps[0].step_number == 1


def test_moore_to_mealy_destination_output_mapping():
    """
    For every transition q --a--> p, the Mealy output must equal lambda_Moore(p).
    """
    presets = get_moore_examples()
    mod3 = presets["Residue Modulo 3 Counter (Multi-Output Transducer)"]
    mealy, _ = convert_moore_to_mealy(mod3)
    
    for (q, a), p in mealy.transitions.items():
        expected_output = mod3.outputs[p]
        actual_output = mealy.outputs[(q, a)]
        assert actual_output == expected_output, f"Mismatch at ({q}, {a}) -> {p}"
