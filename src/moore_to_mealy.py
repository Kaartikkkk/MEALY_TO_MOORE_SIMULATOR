"""
Moore to Mealy Conversion Algorithm.
Implements the destination-state output mapping:
In a Moore machine, output is associated with states: lambda_O: Q -> Gamma.
In a Mealy machine, output is associated with transitions: lambda_M: Q x Sigma -> Gamma.
For every Moore transition q --a--> p, the corresponding Mealy transition is:
q --a/lambda_O(p)--> p.
The number of states is strictly preserved: |Q_Mealy| = |Q_Moore|.
"""

from typing import Dict, List, Tuple
import pandas as pd
from .models import MealyMachine, MooreMachine, ConversionStep
from .validation import validate_moore, validate_mealy


def convert_moore_to_mealy(moore: MooreMachine) -> Tuple[MealyMachine, List[ConversionStep]]:
    """
    Converts a deterministic Moore Machine to an equivalent Mealy Machine.
    
    Parameters:
        moore: Validated MooreMachine instance.
        
    Returns:
        (mealy_machine, conversion_steps)
    """
    # Step 1: Validation
    val_res = validate_moore(moore)
    if not val_res.is_valid:
        raise ValueError(f"Cannot convert invalid Moore Machine: {'; '.join(val_res.errors)}")

    steps: List[ConversionStep] = []

    # Step 1 Artifact
    orig_df = moore.to_dataframe()
    steps.append(ConversionStep(
        step_number=1,
        title="Input Machine Validation & Formal Definition",
        description=(
            f"Validated Moore Machine M = (Q, Σ, Γ, δ, λ, q₀) with "
            f"|Q| = {len(moore.states)}, |Σ| = {len(moore.input_alphabet)}, |Γ| = {len(moore.output_alphabet)}. "
            f"Initial state: '{moore.initial_state}' with initial output λ('{moore.initial_state}') = '{moore.outputs[moore.initial_state]}'."
        ),
        details={
            "states": moore.states,
            "input_alphabet": moore.input_alphabet,
            "output_alphabet": moore.output_alphabet,
            "initial_state": moore.initial_state,
            "initial_output": moore.outputs[moore.initial_state],
            "warnings": val_res.warnings
        },
        table_data=orig_df
    ))

    # Step 2: State Output Inspection
    state_out_rows = []
    for q in moore.states:
        is_start = (q == moore.initial_state)
        state_out_rows.append({
            "State": f"-> {q}" if is_start else q,
            "Associated Output λ(q)": moore.outputs[q],
            "Role": "Initial State (Emits output at t=0)" if is_start else "Standard State"
        })
    state_out_df = pd.DataFrame(state_out_rows)

    steps.append(ConversionStep(
        step_number=2,
        title="Inspect Associated Output for Every Moore State",
        description=(
            "In Moore machines, every state q has a fixed output λ(q). "
            "When converting to Mealy, any transition that enters state q will emit λ(q)."
        ),
        details={"state_outputs": moore.outputs},
        table_data=state_out_df
    ))

    # Step 3: Transition and Output Assignment
    # For each transition q --a--> p in Moore:
    # Set Mealy transition: delta_M(q, a) = p
    # Set Mealy output: lambda_M(q, a) = lambda_O(p)
    mealy_transitions: Dict[Tuple[str, str], str] = {}
    mealy_outputs: Dict[Tuple[str, str], str] = {}
    trans_mapping_rows = []

    for q in moore.states:
        for a in moore.input_alphabet:
            p = moore.transitions[(q, a)]
            out_p = moore.outputs[p]
            mealy_transitions[(q, a)] = p
            mealy_outputs[(q, a)] = out_p

            trans_mapping_rows.append({
                "Source State q": q,
                "Input Symbol a": a,
                "Destination State p = δ(q, a)": p,
                "Destination State Output λ(p)": out_p,
                "Assigned Mealy Transition": f"δ({q}, '{a}') -> {p}",
                "Assigned Mealy Output": f"λ({q}, '{a}') = '{out_p}'"
            })
    trans_mapping_df = pd.DataFrame(trans_mapping_rows)

    steps.append(ConversionStep(
        step_number=3,
        title="Map Destination State Outputs to Mealy Transitions",
        description=(
            "For every state q and input a, let destination state be p = δ(q, a). "
            "Assign the output of the destination state λ(p) as the output of the transition: λ_Mealy(q, a) = λ_Moore(p)."
        ),
        details={"total_transitions_processed": len(trans_mapping_rows)},
        table_data=trans_mapping_df
    ))

    # Step 4: Construct Converted Mealy Machine
    mealy_machine = MealyMachine(
        states=list(moore.states),
        input_alphabet=list(moore.input_alphabet),
        output_alphabet=list(moore.output_alphabet),
        transitions=mealy_transitions,
        outputs=mealy_outputs,
        initial_state=moore.initial_state
    )

    mealy_df = mealy_machine.to_dataframe()

    steps.append(ConversionStep(
        step_number=4,
        title="Construct Final Mealy Machine Transition Table",
        description=(
            f"The converted Mealy Machine retains all {len(mealy_machine.states)} states (|Q| preserved). "
            f"Initial state remains '{mealy_machine.initial_state}'."
        ),
        details={
            "states_count": len(mealy_machine.states),
            "state_count_delta": 0,
            "initial_state": mealy_machine.initial_state
        },
        table_data=mealy_df
    ))

    # Step 5: Initial Output Difference & Equivalence Note
    init_state_out = moore.outputs[moore.initial_state]
    steps.append(ConversionStep(
        step_number=5,
        title="Initial Output Alignment Analysis",
        description=(
            f"Crucial Equivalence Note: The original Moore machine emits an initial output "
            f"λ('{moore.initial_state}') = '{init_state_out}' at time t=0 before any input symbol is processed. "
            f"A Mealy machine only produces outputs upon consuming an input symbol. "
            f"Therefore, for any input string w = a₁a₂...aₙ:\n"
            f"- Moore Output: '{init_state_out}' · z₁z₂...zₙ (length n + 1)\n"
            f"- Mealy Output: z₁z₂...zₙ (length n)\n"
            f"The two machines are behaviorally equivalent upon discarding or accounting for the initial Moore state output."
        ),
        details={
            "initial_moore_output": init_state_out,
            "alignment_rule": "Moore_output(w) = y0 . Mealy_output(w)"
        }
    ))

    # Step 6: Structural Verification
    mealy_val = validate_mealy(mealy_machine)
    steps.append(ConversionStep(
        step_number=6,
        title="Structural Validation of Converted Mealy Machine",
        description=(
            "Validating the newly generated Mealy Machine against deterministic completeness rules: "
            + ("All structural checks passed successfully." if mealy_val.is_valid else f"Validation failed: {'; '.join(mealy_val.errors)}")
        ),
        details={
            "is_valid": mealy_val.is_valid,
            "errors": mealy_val.errors,
            "warnings": mealy_val.warnings
        }
    ))

    return mealy_machine, steps
