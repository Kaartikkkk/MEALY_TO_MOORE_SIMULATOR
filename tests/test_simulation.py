"""
Unit tests for the String Simulation Engine.
"""

import pytest
from src.examples import get_mealy_examples, get_moore_examples
from src.simulation import simulate_mealy, simulate_moore


def test_mealy_simulation_empty_string():
    presets = get_mealy_examples()
    m = presets["Two's Complement Generator (Forces State Splitting)"]
    trace = simulate_mealy(m, "")
    
    assert trace.input_string == ""
    assert trace.output_string == ""
    assert trace.initial_output is None
    assert trace.final_state == m.initial_state
    assert len(trace.steps) == 0
    assert trace.state_path == [m.initial_state]


def test_moore_simulation_empty_string():
    presets = get_moore_examples()
    m = presets["Even/Odd '1's Parity Detector (2-State Binary)"]
    trace = simulate_moore(m, "")
    
    assert trace.input_string == ""
    assert trace.initial_output == m.outputs[m.initial_state]
    assert trace.output_string == m.outputs[m.initial_state]
    assert len(trace.steps) == 0
    assert trace.state_path == [m.initial_state]


def test_mealy_simulation_twos_complement():
    """
    Two's complement of 1100 (LSB first: 0011):
    Input '0011':
    - '0' from q0: out '0', state q0
    - '0' from q0: out '0', state q0
    - '1' from q0: out '1', state q1
    - '1' from q1: out '0', state q1
    Expected output: '0010'
    """
    presets = get_mealy_examples()
    m = presets["Two's Complement Generator (Forces State Splitting)"]
    trace = simulate_mealy(m, "0011")
    
    assert trace.output_string == "0010"
    assert len(trace.steps) == 4
    assert trace.state_path == ["q0", "q0", "q0", "q1", "q1"]


def test_moore_simulation_parity():
    """
    Parity of 101:
    - t=0: in q_even, out '0'
    - '1': to q_odd, out '1'
    - '0': to q_odd, out '1'
    - '1': to q_even, out '0'
    Total output: '0110' (length 4)
    Transition output: '110' (length 3)
    """
    presets = get_moore_examples()
    m = presets["Even/Odd '1's Parity Detector (2-State Binary)"]
    trace = simulate_moore(m, "101")
    
    assert trace.output_string == "0110"
    assert trace.transition_output_string == "110"
    assert len(trace.steps) == 3
    assert trace.state_path == ["q_even", "q_odd", "q_odd", "q_even"]


def test_simulation_invalid_symbol_raises():
    presets = get_mealy_examples()
    m = presets["Two's Complement Generator (Forces State Splitting)"]
    with pytest.raises(ValueError, match="Invalid symbol 'x'"):
        simulate_mealy(m, "01x0")

    moore_presets = get_moore_examples()
    moore = moore_presets["Even/Odd '1's Parity Detector (2-State Binary)"]
    with pytest.raises(ValueError, match="Invalid symbol '9'"):
        simulate_moore(moore, "109")
