"""
Validation module for Mealy and Moore machines.
Ensures mathematical correctness and structural completeness as deterministic finite transducers.
"""

from typing import Set, Tuple, List
from .models import MealyMachine, MooreMachine, ValidationResult


def validate_mealy(machine: MealyMachine) -> ValidationResult:
    """
    Validates a Mealy Machine M = (Q, Sigma, Gamma, delta, lambda, q0).
    Enforces deterministic completeness:
    - Q != emptyset
    - Sigma != emptyset
    - Gamma != emptyset
    - q0 in Q
    - For each q in Q, a in Sigma:
        delta(q, a) in Q is defined
        lambda(q, a) in Gamma is defined
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. State set validation
    if not machine.states:
        errors.append("State set Q cannot be empty. Define at least one state.")
    else:
        # Check for empty string state names
        for s in machine.states:
            if not s or not s.strip():
                errors.append("State name cannot be empty or pure whitespace.")

    # 2. Alphabets validation
    if not machine.input_alphabet:
        errors.append("Input alphabet Σ cannot be empty. Define at least one input symbol.")
    else:
        for a in machine.input_alphabet:
            if not a or not a.strip():
                errors.append("Input symbol cannot be empty or pure whitespace.")

    if not machine.output_alphabet:
        errors.append("Output alphabet Γ cannot be empty. Define at least one output symbol.")
    else:
        for z in machine.output_alphabet:
            if not z or not z.strip():
                errors.append("Output symbol cannot be empty or pure whitespace.")

    # 3. Initial state validation
    if not machine.initial_state:
        errors.append("Initial state q0 must be specified.")
    elif machine.initial_state not in machine.states:
        errors.append(f"Initial state '{machine.initial_state}' is not in the set of states Q: {machine.states}.")

    # If basic structure is broken, return early to avoid cascade errors
    if errors:
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    state_set: Set[str] = set(machine.states)
    input_set: Set[str] = set(machine.input_alphabet)
    output_set: Set[str] = set(machine.output_alphabet)

    # 4. Transitions & Output Completeness
    missing_transitions: List[Tuple[str, str]] = []
    invalid_next_states: List[Tuple[str, str, str]] = []
    missing_outputs: List[Tuple[str, str]] = []
    invalid_outputs: List[Tuple[str, str, str]] = []

    for q in machine.states:
        for a in machine.input_alphabet:
            key = (q, a)
            if key not in machine.transitions or not machine.transitions[key]:
                missing_transitions.append(key)
            else:
                nxt = machine.transitions[key]
                if nxt not in state_set:
                    invalid_next_states.append((q, a, nxt))

            if key not in machine.outputs or machine.outputs[key] is None or machine.outputs[key] == "":
                missing_outputs.append(key)
            else:
                out = machine.outputs[key]
                if out not in output_set:
                    invalid_outputs.append((q, a, out))

    if missing_transitions:
        formatted = ", ".join(f"δ({q}, {a})" for q, a in missing_transitions[:5])
        more = f" and {len(missing_transitions) - 5} more" if len(missing_transitions) > 5 else ""
        errors.append(f"Missing transition(s) for complete deterministic machine: {formatted}{more}.")

    if invalid_next_states:
        formatted = ", ".join(f"δ({q}, {a}) -> '{nxt}'" for q, a, nxt in invalid_next_states[:5])
        errors.append(f"Transition leads to undefined state(s): {formatted}.")

    if missing_outputs:
        formatted = ", ".join(f"λ({q}, {a})" for q, a in missing_outputs[:5])
        errors.append(f"Missing output(s) on transition(s): {formatted}.")

    if invalid_outputs:
        formatted = ", ".join(f"λ({q}, {a}) = '{out}' not in Γ" for q, a, out in invalid_outputs[:5])
        errors.append(f"Transition emits output not in Γ: {formatted}.")

    # 5. Check extraneous transitions/outputs (keys not in Q x Sigma)
    for (q, a) in machine.transitions.keys():
        if q not in state_set:
            errors.append(f"Transition defined for non-existent source state '{q}'.")
        if a not in input_set:
            errors.append(f"Transition defined for non-alphabet symbol '{a}'.")

    # 6. Reachability check (warning, not fatal error)
    if not errors and machine.initial_state in state_set:
        reachable: Set[str] = {machine.initial_state}
        queue = [machine.initial_state]
        while queue:
            curr = queue.pop(0)
            for a in machine.input_alphabet:
                nxt = machine.transitions.get((curr, a))
                if nxt and nxt in state_set and nxt not in reachable:
                    reachable.add(nxt)
                    queue.append(nxt)

        unreachable = state_set - reachable
        if unreachable:
            warnings.append(
                f"State(s) {sorted(list(unreachable))} are unreachable from initial state '{machine.initial_state}'."
            )

    return ValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)


def validate_moore(machine: MooreMachine) -> ValidationResult:
    """
    Validates a Moore Machine M = (Q, Sigma, Gamma, delta, lambda, q0).
    Enforces deterministic completeness:
    - Q != emptyset
    - Sigma != emptyset
    - Gamma != emptyset
    - q0 in Q
    - For each q in Q: lambda(q) in Gamma is defined
    - For each q in Q, a in Sigma: delta(q, a) in Q is defined
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. State set validation
    if not machine.states:
        errors.append("State set Q cannot be empty. Define at least one state.")
    else:
        for s in machine.states:
            if not s or not s.strip():
                errors.append("State name cannot be empty or pure whitespace.")

    # 2. Alphabets validation
    if not machine.input_alphabet:
        errors.append("Input alphabet Σ cannot be empty. Define at least one input symbol.")
    else:
        for a in machine.input_alphabet:
            if not a or not a.strip():
                errors.append("Input symbol cannot be empty or pure whitespace.")

    if not machine.output_alphabet:
        errors.append("Output alphabet Γ cannot be empty. Define at least one output symbol.")
    else:
        for z in machine.output_alphabet:
            if not z or not z.strip():
                errors.append("Output symbol cannot be empty or pure whitespace.")

    # 3. Initial state validation
    if not machine.initial_state:
        errors.append("Initial state q0 must be specified.")
    elif machine.initial_state not in machine.states:
        errors.append(f"Initial state '{machine.initial_state}' is not in the set of states Q: {machine.states}.")

    if errors:
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    state_set: Set[str] = set(machine.states)
    input_set: Set[str] = set(machine.input_alphabet)
    output_set: Set[str] = set(machine.output_alphabet)

    # 4. State Outputs validation
    missing_state_outputs: List[str] = []
    invalid_state_outputs: List[Tuple[str, str]] = []

    for q in machine.states:
        if q not in machine.outputs or machine.outputs[q] is None or machine.outputs[q] == "":
            missing_state_outputs.append(q)
        else:
            out = machine.outputs[q]
            if out not in output_set:
                invalid_state_outputs.append((q, out))

    if missing_state_outputs:
        errors.append(f"Missing state output for state(s): {', '.join(missing_state_outputs)}.")

    if invalid_state_outputs:
        formatted = ", ".join(f"λ({q}) = '{out}'" for q, out in invalid_state_outputs)
        errors.append(f"State output symbol not in Γ: {formatted}.")

    # 5. Transitions completeness
    missing_transitions: List[Tuple[str, str]] = []
    invalid_next_states: List[Tuple[str, str, str]] = []

    for q in machine.states:
        for a in machine.input_alphabet:
            key = (q, a)
            if key not in machine.transitions or not machine.transitions[key]:
                missing_transitions.append(key)
            else:
                nxt = machine.transitions[key]
                if nxt not in state_set:
                    invalid_next_states.append((q, a, nxt))

    if missing_transitions:
        formatted = ", ".join(f"δ({q}, {a})" for q, a in missing_transitions[:5])
        more = f" and {len(missing_transitions) - 5} more" if len(missing_transitions) > 5 else ""
        errors.append(f"Missing transition(s) for complete deterministic machine: {formatted}{more}.")

    if invalid_next_states:
        formatted = ", ".join(f"δ({q}, {a}) -> '{nxt}'" for q, a, nxt in invalid_next_states[:5])
        errors.append(f"Transition leads to undefined state(s): {formatted}.")

    # 6. Extraneous entries check
    for (q, a) in machine.transitions.keys():
        if q not in state_set:
            errors.append(f"Transition defined for non-existent source state '{q}'.")
        if a not in input_set:
            errors.append(f"Transition defined for non-alphabet symbol '{a}'.")

    # 7. Reachability check
    if not errors and machine.initial_state in state_set:
        reachable: Set[str] = {machine.initial_state}
        queue = [machine.initial_state]
        while queue:
            curr = queue.pop(0)
            for a in machine.input_alphabet:
                nxt = machine.transitions.get((curr, a))
                if nxt and nxt in state_set and nxt not in reachable:
                    reachable.add(nxt)
                    queue.append(nxt)

        unreachable = state_set - reachable
        if unreachable:
            warnings.append(
                f"State(s) {sorted(list(unreachable))} are unreachable from initial state '{machine.initial_state}'."
            )

    return ValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)
