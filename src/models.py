"""
Data models for Mealy and Moore Finite-State Transducers.
Formal definitions:
- Mealy Machine: M = (Q, Sigma, Gamma, delta, lambda, q0)
  where lambda: Q x Sigma -> Gamma
- Moore Machine: M = (Q, Sigma, Gamma, delta, lambda, q0)
  where lambda: Q -> Gamma
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd


@dataclass
class ValidationResult:
    """Represents the outcome of machine structural validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.is_valid:
            if self.warnings:
                return f"Valid with {len(self.warnings)} warning(s)."
            return "Machine definition is mathematically valid."
        return f"Validation failed with {len(self.errors)} error(s)."


@dataclass
class ConversionStep:
    """Represents a single step in the step-by-step conversion pipeline."""
    step_number: int
    title: str
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    table_data: Optional[pd.DataFrame] = None


@dataclass
class MealyMachine:
    """
    Formal Mealy Machine model:
    M = (Q, Sigma, Gamma, delta, lambda, q0)
    
    Q: finite set of states
    Sigma: input alphabet
    Gamma: output alphabet
    delta: transition function (Q x Sigma -> Q)
    lambda_: output function (Q x Sigma -> Gamma)
    initial_state: q0 in Q
    """
    states: List[str]
    input_alphabet: List[str]
    output_alphabet: List[str]
    transitions: Dict[Tuple[str, str], str]  # (state, input_symbol) -> next_state
    outputs: Dict[Tuple[str, str], str]      # (state, input_symbol) -> output_symbol
    initial_state: str

    def __post_init__(self):
        # Normalize to lists with preserved order without duplicates
        self.states = list(dict.fromkeys(self.states))
        self.input_alphabet = list(dict.fromkeys(self.input_alphabet))
        self.output_alphabet = list(dict.fromkeys(self.output_alphabet))

    def copy(self) -> "MealyMachine":
        return MealyMachine(
            states=list(self.states),
            input_alphabet=list(self.input_alphabet),
            output_alphabet=list(self.output_alphabet),
            transitions=dict(self.transitions),
            outputs=dict(self.outputs),
            initial_state=self.initial_state,
        )

    def to_dataframe(self) -> pd.DataFrame:
        """
        Generates a standard state transition table:
        Row: Current State
        Columns: For each symbol 'a' in Sigma, columns 'Next State (a)' and 'Output (a)'
        """
        rows = []
        for q in self.states:
            row: Dict[str, Any] = {"Current State": f"-> {q}" if q == self.initial_state else q}
            for a in self.input_alphabet:
                nxt = self.transitions.get((q, a), "-")
                out = self.outputs.get((q, a), "-")
                row[f"Next State (input={a})"] = nxt
                row[f"Output (input={a})"] = out
            rows.append(row)
        return pd.DataFrame(rows)

    def to_flat_table(self) -> pd.DataFrame:
        """
        Generates a row-by-row transition list:
        Current State | Input Symbol | Next State | Output Symbol
        """
        rows = []
        for q in self.states:
            for a in self.input_alphabet:
                nxt = self.transitions.get((q, a), "")
                out = self.outputs.get((q, a), "")
                rows.append({
                    "Current State": q,
                    "Input Symbol": a,
                    "Next State": nxt,
                    "Output Symbol": out
                })
        return pd.DataFrame(rows)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes machine to a JSON-compatible dictionary."""
        trans_list = []
        for (q, a), nxt in self.transitions.items():
            out = self.outputs.get((q, a), "")
            trans_list.append({
                "from_state": q,
                "input_symbol": a,
                "next_state": nxt,
                "output_symbol": out
            })
        return {
            "type": "Mealy",
            "states": self.states,
            "input_alphabet": self.input_alphabet,
            "output_alphabet": self.output_alphabet,
            "initial_state": self.initial_state,
            "transitions": trans_list
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MealyMachine":
        states = list(data.get("states", []))
        input_alphabet = list(data.get("input_alphabet", []))
        output_alphabet = list(data.get("output_alphabet", []))
        initial_state = data.get("initial_state", states[0] if states else "")

        transitions: Dict[Tuple[str, str], str] = {}
        outputs: Dict[Tuple[str, str], str] = {}
        for item in data.get("transitions", []):
            q = item.get("from_state", "")
            a = item.get("input_symbol", "")
            nxt = item.get("next_state", "")
            out = item.get("output_symbol", "")
            if q and a:
                transitions[(q, a)] = nxt
                outputs[(q, a)] = out

        return cls(
            states=states,
            input_alphabet=input_alphabet,
            output_alphabet=output_alphabet,
            transitions=transitions,
            outputs=outputs,
            initial_state=initial_state
        )


@dataclass
class MooreMachine:
    """
    Formal Moore Machine model:
    M = (Q, Sigma, Gamma, delta, lambda, q0)
    
    Q: finite set of states
    Sigma: input alphabet
    Gamma: output alphabet
    delta: transition function (Q x Sigma -> Q)
    lambda_: output function (Q -> Gamma)
    initial_state: q0 in Q
    """
    states: List[str]
    input_alphabet: List[str]
    output_alphabet: List[str]
    transitions: Dict[Tuple[str, str], str]  # (state, input_symbol) -> next_state
    outputs: Dict[str, str]                  # state -> output_symbol
    initial_state: str

    def __post_init__(self):
        self.states = list(dict.fromkeys(self.states))
        self.input_alphabet = list(dict.fromkeys(self.input_alphabet))
        self.output_alphabet = list(dict.fromkeys(self.output_alphabet))

    def copy(self) -> "MooreMachine":
        return MooreMachine(
            states=list(self.states),
            input_alphabet=list(self.input_alphabet),
            output_alphabet=list(self.output_alphabet),
            transitions=dict(self.transitions),
            outputs=dict(self.outputs),
            initial_state=self.initial_state,
        )

    def to_dataframe(self) -> pd.DataFrame:
        """
        Generates standard Moore transition table:
        Row: Current State
        Column: State Output, and Next State for each input symbol 'a' in Sigma
        """
        rows = []
        for q in self.states:
            row: Dict[str, Any] = {
                "Current State": f"-> {q}" if q == self.initial_state else q,
                "State Output": self.outputs.get(q, "-")
            }
            for a in self.input_alphabet:
                nxt = self.transitions.get((q, a), "-")
                row[f"Next State (input={a})"] = nxt
            rows.append(row)
        return pd.DataFrame(rows)

    def to_flat_table(self) -> pd.DataFrame:
        """
        Generates a flat transition list:
        Current State | State Output | Input Symbol | Next State
        """
        rows = []
        for q in self.states:
            out = self.outputs.get(q, "")
            for a in self.input_alphabet:
                nxt = self.transitions.get((q, a), "")
                rows.append({
                    "Current State": q,
                    "State Output": out,
                    "Input Symbol": a,
                    "Next State": nxt
                })
        return pd.DataFrame(rows)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes machine to a JSON-compatible dictionary."""
        trans_list = []
        for (q, a), nxt in self.transitions.items():
            trans_list.append({
                "from_state": q,
                "input_symbol": a,
                "next_state": nxt
            })
        return {
            "type": "Moore",
            "states": self.states,
            "input_alphabet": self.input_alphabet,
            "output_alphabet": self.output_alphabet,
            "initial_state": self.initial_state,
            "state_outputs": self.outputs,
            "transitions": trans_list
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MooreMachine":
        states = list(data.get("states", []))
        input_alphabet = list(data.get("input_alphabet", []))
        output_alphabet = list(data.get("output_alphabet", []))
        initial_state = data.get("initial_state", states[0] if states else "")
        outputs = dict(data.get("state_outputs", {}))

        transitions: Dict[Tuple[str, str], str] = {}
        for item in data.get("transitions", []):
            q = item.get("from_state", "")
            a = item.get("input_symbol", "")
            nxt = item.get("next_state", "")
            if q and a:
                transitions[(q, a)] = nxt

        return cls(
            states=states,
            input_alphabet=input_alphabet,
            output_alphabet=output_alphabet,
            transitions=transitions,
            outputs=outputs,
            initial_state=initial_state
        )
