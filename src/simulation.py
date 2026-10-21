"""
String Simulation Engine for Mealy and Moore Machines.
Executes input strings symbol-by-symbol, producing detailed execution traces,
state paths, and step-by-step emitted outputs.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd
from .models import MealyMachine, MooreMachine


@dataclass
class SimulationStep:
    """Represents a single consumed input symbol and transition."""
    step_num: int
    current_state: str
    input_symbol: str
    next_state: str
    emitted_output: str
    accumulated_output: str


@dataclass
class SimulationTrace:
    """Complete execution trace of a string simulation."""
    machine_type: str  # "Mealy" or "Moore"
    input_string: str
    initial_state: str
    initial_output: Optional[str]  # Non-None for Moore (emitted at t=0)
    steps: List[SimulationStep] = field(default_factory=list)
    final_state: str = ""
    output_string: str = ""
    transition_output_string: str = ""  # For Moore, excludes initial output
    state_path: List[str] = field(default_factory=list)

    def to_dataframe(self) -> pd.DataFrame:
        """Converts steps to a displayable DataFrame."""
        if not self.steps:
            # Empty input case
            if self.machine_type == "Moore":
                return pd.DataFrame([{
                    "Step": 0,
                    "Current State": self.initial_state,
                    "Input Symbol": "ε (Empty)",
                    "Next State": self.initial_state,
                    "Emitted Output": self.initial_output,
                    "Accumulated Output": self.output_string,
                    "Phase": "Initial State Output (t=0)"
                }])
            else:
                return pd.DataFrame([{
                    "Step": 0,
                    "Current State": self.initial_state,
                    "Input Symbol": "ε (Empty)",
                    "Next State": self.initial_state,
                    "Emitted Output": "ε",
                    "Accumulated Output": "ε",
                    "Phase": "No Transitions"
                }])

        rows = []
        # For Moore, show step 0 (initial state output)
        if self.machine_type == "Moore" and self.initial_output is not None:
            rows.append({
                "Step": 0,
                "Current State": self.initial_state,
                "Input Symbol": "- (t=0)",
                "Next State": self.initial_state,
                "Emitted Output": self.initial_output,
                "Accumulated Output": self.initial_output,
                "Phase": "Initial State Output (t=0)"
            })

        for s in self.steps:
            rows.append({
                "Step": s.step_num,
                "Current State": s.current_state,
                "Input Symbol": s.input_symbol,
                "Next State": s.next_state,
                "Emitted Output": s.emitted_output,
                "Accumulated Output": s.accumulated_output,
                "Phase": "Transition Step"
            })
        return pd.DataFrame(rows)


def simulate_mealy(machine: MealyMachine, input_string: str) -> SimulationTrace:
    """
    Simulates a Mealy machine on an input string.
    Raises ValueError if input_string contains symbols not in Sigma.
    """
    # Alphabet check
    valid_symbols = set(machine.input_alphabet)
    for idx, char in enumerate(input_string):
        if char not in valid_symbols:
            raise ValueError(
                f"Invalid symbol '{char}' at index {idx}. Valid input alphabet Σ = {machine.input_alphabet}."
            )

    curr_state = machine.initial_state
    state_path = [curr_state]
    accumulated_output = ""
    steps: List[SimulationStep] = []

    # Handle empty string
    if not input_string:
        return SimulationTrace(
            machine_type="Mealy",
            input_string="",
            initial_state=curr_state,
            initial_output=None,
            steps=[],
            final_state=curr_state,
            output_string="",
            transition_output_string="",
            state_path=state_path
        )

    for i, char in enumerate(input_string, start=1):
        key = (curr_state, char)
        if key not in machine.transitions:
            raise RuntimeError(f"Missing transition for state '{curr_state}' on input '{char}'.")

        nxt_state = machine.transitions[key]
        out_sym = machine.outputs[key]
        accumulated_output += out_sym

        steps.append(SimulationStep(
            step_num=i,
            current_state=curr_state,
            input_symbol=char,
            next_state=nxt_state,
            emitted_output=out_sym,
            accumulated_output=accumulated_output
        ))

        curr_state = nxt_state
        state_path.append(curr_state)

    return SimulationTrace(
        machine_type="Mealy",
        input_string=input_string,
        initial_state=machine.initial_state,
        initial_output=None,
        steps=steps,
        final_state=curr_state,
        output_string=accumulated_output,
        transition_output_string=accumulated_output,
        state_path=state_path
    )


def simulate_moore(machine: MooreMachine, input_string: str) -> SimulationTrace:
    """
    Simulates a Moore machine on an input string.
    Emits initial output lambda(q0) at t=0, followed by transition outputs.
    Raises ValueError if input_string contains symbols not in Sigma.
    """
    valid_symbols = set(machine.input_alphabet)
    for idx, char in enumerate(input_string):
        if char not in valid_symbols:
            raise ValueError(
                f"Invalid symbol '{char}' at index {idx}. Valid input alphabet Σ = {machine.input_alphabet}."
            )

    curr_state = machine.initial_state
    initial_output = machine.outputs.get(curr_state, "")
    state_path = [curr_state]
    accumulated_output = initial_output
    trans_output = ""
    steps: List[SimulationStep] = []

    if not input_string:
        return SimulationTrace(
            machine_type="Moore",
            input_string="",
            initial_state=curr_state,
            initial_output=initial_output,
            steps=[],
            final_state=curr_state,
            output_string=initial_output,
            transition_output_string="",
            state_path=state_path
        )

    for i, char in enumerate(input_string, start=1):
        key = (curr_state, char)
        if key not in machine.transitions:
            raise RuntimeError(f"Missing transition for state '{curr_state}' on input '{char}'.")

        nxt_state = machine.transitions[key]
        out_sym = machine.outputs.get(nxt_state, "")
        accumulated_output += out_sym
        trans_output += out_sym

        steps.append(SimulationStep(
            step_num=i,
            current_state=curr_state,
            input_symbol=char,
            next_state=nxt_state,
            emitted_output=out_sym,
            accumulated_output=accumulated_output
        ))

        curr_state = nxt_state
        state_path.append(curr_state)

    return SimulationTrace(
        machine_type="Moore",
        input_string=input_string,
        initial_state=machine.initial_state,
        initial_output=initial_output,
        steps=steps,
        final_state=curr_state,
        output_string=accumulated_output,
        transition_output_string=trans_output,
        state_path=state_path
    )
