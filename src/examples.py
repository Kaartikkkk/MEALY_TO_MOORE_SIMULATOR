"""
Predefined Example Machines for Mealy and Moore Conversions.
Includes verified standard textbook examples, sequence detectors,
arithmetic transducers, and edge cases.
"""

from typing import Dict
from .models import MealyMachine, MooreMachine


def get_mealy_examples() -> Dict[str, MealyMachine]:
    """
    Returns a dictionary of curated Mealy machine presets:
    1. Two's Complement Generator (Classic 2-state arithmetic transducer)
    2. State-Splitting Sequence Transducer (Forces state q1/q2 splitting with distinct incoming outputs)
    3. Transient Initial State with Self-Loops (Initial state has no incoming transitions)
    """
    # Preset 1: Two's Complement Generator (LSB to MSB)
    # q0: scanning trailing zeros, remains in q0 on '0' emitting '0'. On '1', emits '1' and transitions to q1.
    # q1: inverting subsequent bits: on '0' emits '1', on '1' emits '0'.
    # In q1, incoming transitions: (q0, '1')->q1 emits '1', (q1, '0')->q1 emits '1', (q1, '1')->q1 emits '0'.
    # Therefore, q1 has incoming outputs {0, 1} and will SPLIT into q1_0 and q1_1 in Moore!
    twos_comp = MealyMachine(
        states=["q0", "q1"],
        input_alphabet=["0", "1"],
        output_alphabet=["0", "1"],
        transitions={
            ("q0", "0"): "q0",
            ("q0", "1"): "q1",
            ("q1", "0"): "q1",
            ("q1", "1"): "q1",
        },
        outputs={
            ("q0", "0"): "0",
            ("q0", "1"): "1",
            ("q1", "0"): "1",
            ("q1", "1"): "0",
        },
        initial_state="q0"
    )

    # Preset 2: State-Splitting Sequence Transducer (Hopcroft & Ullman style)
    # States: q0, q1, q2
    # q1 is entered with both output '0' and '1'
    # q2 is entered with both output '0' and '1'
    # Forces multiple states to split into copies.
    splitter = MealyMachine(
        states=["q0", "q1", "q2"],
        input_alphabet=["0", "1"],
        output_alphabet=["0", "1"],
        transitions={
            ("q0", "0"): "q1",
            ("q0", "1"): "q2",
            ("q1", "0"): "q1",
            ("q1", "1"): "q2",
            ("q2", "0"): "q0",
            ("q2", "1"): "q1",
        },
        outputs={
            ("q0", "0"): "0",
            ("q0", "1"): "1",
            ("q1", "0"): "1",  # entering q1 with '1' (from q0 it entered with '0')
            ("q1", "1"): "0",
            ("q2", "0"): "0",
            ("q2", "1"): "1",  # entering q1 with '1'
        },
        initial_state="q0"
    )

    # Preset 3: Transient Initial State with Self-Loops
    # q0 has NO incoming transitions (transient start state)
    # q1 and q2 form a cycle with self-loops
    transient_init = MealyMachine(
        states=["q0", "q1", "q2"],
        input_alphabet=["0", "1"],
        output_alphabet=["0", "1"],
        transitions={
            ("q0", "0"): "q1",
            ("q0", "1"): "q2",
            ("q1", "0"): "q1",
            ("q1", "1"): "q2",
            ("q2", "0"): "q2",
            ("q2", "1"): "q1",
        },
        outputs={
            ("q0", "0"): "0",
            ("q0", "1"): "1",
            ("q1", "0"): "0",
            ("q1", "1"): "1",
            ("q2", "0"): "1",
            ("q2", "1"): "0",
        },
        initial_state="q0"
    )

    return {
        "Two's Complement Generator (Forces State Splitting)": twos_comp,
        "Multi-State Splitter (Comprehensive Split)": splitter,
        "Transient Initial State with Self-Loops": transient_init
    }


def get_moore_examples() -> Dict[str, MooreMachine]:
    """
    Returns a dictionary of curated Moore machine presets:
    1. Even/Odd '1's Parity Detector (2-state binary)
    2. Residue Modulo 3 Counter (Distinct outputs on all states: 0, 1, 2)
    3. Substring '101' Detector (4 states with loops and cross transitions)
    """
    # Preset 1: Even/Odd '1's Parity Detector
    # q_even: even number of 1s (out: 0)
    # q_odd: odd number of 1s (out: 1)
    parity = MooreMachine(
        states=["q_even", "q_odd"],
        input_alphabet=["0", "1"],
        output_alphabet=["0", "1"],
        transitions={
            ("q_even", "0"): "q_even",
            ("q_even", "1"): "q_odd",
            ("q_odd", "0"): "q_odd",
            ("q_odd", "1"): "q_even",
        },
        outputs={
            "q_even": "0",
            "q_odd": "1"
        },
        initial_state="q_even"
    )

    # Preset 2: Residue Modulo 3 Counter (Binary stream mod 3)
    # Computes (value * 2 + bit) mod 3:
    # 0 -> 0*2+0=0, 0*2+1=1
    # 1 -> 1*2+0=2, 1*2+1=3=0
    # 2 -> 2*2+0=4=1, 2*2+1=5=2
    # Outputs: state q0 -> '0', q1 -> '1', q2 -> '2'
    mod3 = MooreMachine(
        states=["q0", "q1", "q2"],
        input_alphabet=["0", "1"],
        output_alphabet=["0", "1", "2"],
        transitions={
            ("q0", "0"): "q0",
            ("q0", "1"): "q1",
            ("q1", "0"): "q2",
            ("q1", "1"): "q0",
            ("q2", "0"): "q1",
            ("q2", "1"): "q2",
        },
        outputs={
            "q0": "0",
            "q1": "1",
            "q2": "2"
        },
        initial_state="q0"
    )

    # Preset 3: Substring '101' Sequence Detector
    # S0: start / no match (out: 0)
    # S1: seen '1' (out: 0)
    # S2: seen '10' (out: 0)
    # S3: seen '101' (out: 1)
    seq_101 = MooreMachine(
        states=["S0", "S1", "S2", "S3"],
        input_alphabet=["0", "1"],
        output_alphabet=["0", "1"],
        transitions={
            ("S0", "0"): "S0",
            ("S0", "1"): "S1",
            ("S1", "0"): "S2",
            ("S1", "1"): "S1",
            ("S2", "0"): "S0",
            ("S2", "1"): "S3",
            ("S3", "0"): "S2",
            ("S3", "1"): "S1",
        },
        outputs={
            "S0": "0",
            "S1": "0",
            "S2": "0",
            "S3": "1"
        },
        initial_state="S0"
    )

    return {
        "Even/Odd '1's Parity Detector (2-State Binary)": parity,
        "Residue Modulo 3 Counter (Multi-Output Transducer)": mod3,
        "Substring '101' Detector (4-State with Loops)": seq_101
    }
