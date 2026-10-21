"""
Mealy to Moore Conversion Algorithm.
Implements standard state-splitting construction:
In a Mealy machine, output depends on (state, input): lambda_M: Q x Sigma -> Gamma.
In a Moore machine, output depends only on state: lambda_O: Q' -> Gamma.
Hence, when multiple transitions enter state q with different output symbols,
q must be split into multiple Moore states (q, z), one for each distinct incoming output z.
"""

from typing import Dict, List, Set, Tuple, Optional
import pandas as pd
from .models import MealyMachine, MooreMachine, ConversionStep
from .validation import validate_mealy, validate_moore


def convert_mealy_to_moore(
    mealy: MealyMachine,
    initial_output: Optional[str] = None
) -> Tuple[MooreMachine, List[ConversionStep]]:
    """
    Converts a deterministic Mealy Machine to an equivalent Moore Machine.
    
    Parameters:
        mealy: Validated MealyMachine instance.
        initial_output: Desired output for the initial Moore state at t=0.
                        If None, defaults to the first incoming output of q0 if available,
                        or the first symbol in Gamma.
                        
    Returns:
        (moore_machine, conversion_steps)
    """
    # Step 1: Validation
    val_res = validate_mealy(mealy)
    if not val_res.is_valid:
        raise ValueError(f"Cannot convert invalid Mealy Machine: {'; '.join(val_res.errors)}")

    steps: List[ConversionStep] = []

    # Step 1 Artifact
    orig_df = mealy.to_dataframe()
    steps.append(ConversionStep(
        step_number=1,
        title="Input Machine Validation & Formal Definition",
        description=(
            f"Validated Mealy Machine M = (Q, Σ, Γ, δ, λ, q₀) with "
            f"|Q| = {len(mealy.states)}, |Σ| = {len(mealy.input_alphabet)}, |Γ| = {len(mealy.output_alphabet)}. "
            f"Initial state: '{mealy.initial_state}'."
        ),
        details={
            "states": mealy.states,
            "input_alphabet": mealy.input_alphabet,
            "output_alphabet": mealy.output_alphabet,
            "initial_state": mealy.initial_state,
            "warnings": val_res.warnings
        },
        table_data=orig_df
    ))

    # Step 2: Incoming Transition Outputs Analysis
    # For each state p in Q, incoming_outputs[p] = { lambda(q, a) | delta(q, a) == p }
    incoming_outputs: Dict[str, Set[str]] = {q: set() for q in mealy.states}
    incoming_transitions: Dict[str, List[Tuple[str, str, str]]] = {q: [] for q in mealy.states}

    for (q, a), nxt in mealy.transitions.items():
        out = mealy.outputs.get((q, a), "")
        incoming_outputs[nxt].add(out)
        incoming_transitions[nxt].append((q, a, out))

    incoming_rows = []
    for q in mealy.states:
        outs = sorted(list(incoming_outputs[q]))
        trans_str = ", ".join(f"δ({src}, '{sym}') -> {q} [out: '{o}']" for src, sym, o in incoming_transitions[q]) or "None (Unentered)"
        incoming_rows.append({
            "Destination State": q,
            "Incoming Transitions Count": len(incoming_transitions[q]),
            "Incoming Outputs Set": "{" + ", ".join(f"'{o}'" for o in outs) + "}" if outs else "∅ (None)",
            "Distinct Outputs Count": len(outs),
            "Incoming Transitions Detail": trans_str
        })
    incoming_df = pd.DataFrame(incoming_rows)

    steps.append(ConversionStep(
        step_number=2,
        title="Analyze Incoming Transition Outputs for Each State",
        description=(
            "In Moore machines, output is tied solely to the state. We inspect every transition entering "
            "each state to see what output symbols are produced upon entry."
        ),
        details={"incoming_outputs": {k: sorted(list(v)) for k, v in incoming_outputs.items()}},
        table_data=incoming_df
    ))

    # Step 3: State Splitting Decision
    split_decisions = []
    for q in mealy.states:
        outs = sorted(list(incoming_outputs[q]))
        count = len(outs)
        if count > 1:
            decision = f"SPLIT REQUIRED: State '{q}' is entered with {count} distinct outputs ({', '.join(outs)}). It must split into {count} Moore states."
        elif count == 1:
            decision = f"Single output: State '{q}' is only entered with output '{outs[0]}'. No splitting required."
        else:
            decision = f"Initial / Unreached: State '{q}' has 0 incoming transitions. Requires designated initial output."
        split_decisions.append({
            "State": q,
            "Distinct Outputs": count,
            "Decision": decision
        })
    split_df = pd.DataFrame(split_decisions)

    steps.append(ConversionStep(
        step_number=3,
        title="Determine State Splitting Requirements",
        description=(
            "Whenever transitions entering a state produce distinct output symbols, that state must be split into "
            "multiple Moore states (one for each distinct incoming output)."
        ),
        details={"decisions": split_decisions},
        table_data=split_df
    ))

    # Step 4: Resolve Initial State & Output Convention
    # Determine the output for the start state at time t=0 before any transition
    q0 = mealy.initial_state
    q0_incoming = sorted(list(incoming_outputs[q0]))

    if initial_output is not None:
        if initial_output not in mealy.output_alphabet:
            raise ValueError(f"Requested initial_output '{initial_output}' is not in Γ: {mealy.output_alphabet}")
        selected_init_out = initial_output
    elif q0_incoming:
        # Default to first incoming output of q0 to minimize superfluous state creation
        selected_init_out = q0_incoming[0]
    else:
        # q0 has no incoming transitions; use first symbol of output alphabet
        selected_init_out = mealy.output_alphabet[0]

    # Generate Moore states (q, z)
    moore_state_tuples: List[Tuple[str, str]] = []  # (original_state, output_symbol)
    for q in mealy.states:
        outs = sorted(list(incoming_outputs[q]))
        if not outs:
            # If no incoming transitions, it needs at least one state with selected_init_out (for q0)
            # or default output
            out = selected_init_out if q == q0 else mealy.output_alphabet[0]
            moore_state_tuples.append((q, out))
        else:
            for out in outs:
                moore_state_tuples.append((q, out))

    # If q0's selected_init_out is not in its incoming outputs, we must add a fresh initial state copy
    if (q0, selected_init_out) not in moore_state_tuples:
        moore_state_tuples.insert(0, (q0, selected_init_out))

    # Generate clean state names for Moore machine
    # If state q was split (|copies| > 1), name as q_out.
    # If state q was not split (|copies| == 1), we can still use q_out or q.
    # To keep names predictable and consistent: name as q_out, or if no conflict, format cleanly.
    # Standard academic representation: q_z or (q, z). Let's use clean name: f"{q}_{z}" or f"({q},{z})"
    state_copies_count = {q: 0 for q in mealy.states}
    for (q, z) in moore_state_tuples:
        state_copies_count[q] += 1

    moore_state_names: Dict[Tuple[str, str], str] = {}
    for (q, z) in moore_state_tuples:
        if state_copies_count[q] > 1 or (q == q0 and (q, z) == (q0, selected_init_out)):
            moore_state_names[(q, z)] = f"{q}_{z}"
        else:
            # Single incoming output and not split
            moore_state_names[(q, z)] = f"{q}_{z}"

    # Ensure uniqueness of state names
    final_moore_states = [moore_state_names[tup] for tup in moore_state_tuples]
    moore_outputs = {moore_state_names[tup]: tup[1] for tup in moore_state_tuples}
    start_moore_state = moore_state_names[(q0, selected_init_out)]

    state_gen_rows = []
    for tup in moore_state_tuples:
        m_name = moore_state_names[tup]
        is_start = (m_name == start_moore_state)
        state_gen_rows.append({
            "Moore State": f"-> {m_name}" if is_start else m_name,
            "Original Mealy State": tup[0],
            "Associated Incoming Output": tup[1],
            "State Output λ_Moore": tup[1],
            "Role": "Initial State (t=0)" if is_start else "Standard Split State"
        })
    state_gen_df = pd.DataFrame(state_gen_rows)

    steps.append(ConversionStep(
        step_number=4,
        title="Generate Moore States & Assign State Outputs",
        description=(
            f"Created {len(final_moore_states)} Moore states from {len(mealy.states)} original states. "
            f"Initial state set to '{start_moore_state}' with initial output λ('{start_moore_state}') = '{selected_init_out}'."
        ),
        details={
            "initial_state": start_moore_state,
            "initial_output": selected_init_out,
            "state_count_original": len(mealy.states),
            "state_count_moore": len(final_moore_states),
            "split_delta": len(final_moore_states) - len(mealy.states)
        },
        table_data=state_gen_df
    ))

    # Step 5: Transition Calculation
    # For each Moore state (q, z) and input symbol a:
    # Look up Mealy transition: delta_M(q, a) = p, lambda_M(q, a) = z'
    # Converted transition: delta_O((q, z), a) = (p, z')
    moore_transitions: Dict[Tuple[str, str], str] = {}
    trans_calc_rows = []

    for tup in moore_state_tuples:
        src_moore = moore_state_names[tup]
        orig_q = tup[0]
        for a in mealy.input_alphabet:
            nxt_orig = mealy.transitions[(orig_q, a)]
            out_orig = mealy.outputs[(orig_q, a)]
            nxt_moore = moore_state_names[(nxt_orig, out_orig)]
            moore_transitions[(src_moore, a)] = nxt_moore

            trans_calc_rows.append({
                "From Moore State": src_moore,
                "Input Symbol": a,
                "Original Mealy Transition": f"δ({orig_q}, '{a}') -> {nxt_orig}",
                "Emitted Mealy Output": out_orig,
                "Target Moore Copy": f"({nxt_orig}, '{out_orig}')",
                "Next Moore State": nxt_moore
            })
    trans_calc_df = pd.DataFrame(trans_calc_rows)

    steps.append(ConversionStep(
        step_number=5,
        title="Calculate Converted Transitions",
        description=(
            "For every Moore state (q, z) and input symbol a, find Mealy transition δ(q, a) = p with output λ(q, a) = z'. "
            "The Moore transition is δ'((q, z), a) = (p, z')."
        ),
        details={"transitions_count": len(moore_transitions)},
        table_data=trans_calc_df
    ))

    # Step 6: Construct Final Moore Machine
    moore_machine = MooreMachine(
        states=final_moore_states,
        input_alphabet=list(mealy.input_alphabet),
        output_alphabet=list(mealy.output_alphabet),
        transitions=moore_transitions,
        outputs=moore_outputs,
        initial_state=start_moore_state
    )

    moore_df = moore_machine.to_dataframe()

    steps.append(ConversionStep(
        step_number=6,
        title="Construct Final Moore Transition Table & Output Convention",
        description=(
            "The converted Moore Machine is assembled. Note the output alignment convention: "
            "For an input string of length n, the Moore machine outputs n + 1 symbols "
            "(the initial output at t=0 followed by the n transition outputs). "
            "The last n symbols correspond exactly to the Mealy machine's output."
        ),
        details={
            "initial_state": start_moore_state,
            "initial_output": selected_init_out,
            "alignment_rule": "Moore_output(w) = y0 . Mealy_output(w)"
        },
        table_data=moore_df
    ))

    # Step 7: Structural Verification of Converted Machine
    moore_val = validate_moore(moore_machine)
    steps.append(ConversionStep(
        step_number=7,
        title="Structural Validation of Converted Moore Machine",
        description=(
            "Validating the newly generated Moore Machine against deterministic completeness rules: "
            + ("All structural checks passed successfully." if moore_val.is_valid else f"Validation failed: {'; '.join(moore_val.errors)}")
        ),
        details={
            "is_valid": moore_val.is_valid,
            "errors": moore_val.errors,
            "warnings": moore_val.warnings
        }
    ))

    return moore_machine, steps
