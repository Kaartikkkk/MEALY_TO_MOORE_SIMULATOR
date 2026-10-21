"""
Equivalence Testing and Verification Engine.
Performs structural and behavioral verification between Mealy and Moore machines.
Implements single-string testing, custom test suites, and bounded exhaustive testing.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import itertools
import pandas as pd
from .models import MealyMachine, MooreMachine
from .simulation import simulate_mealy, simulate_moore


@dataclass
class EquivalenceTestResult:
    """Outcome of testing a single input string on both machines."""
    input_string: str
    original_output: str
    converted_output: str
    alignment_applied: str
    aligned_original: str
    aligned_converted: str
    passed: bool
    details: str


@dataclass
class BatchEquivalenceResult:
    """Outcome of bounded or suite equivalence verification."""
    total_tested: int
    passed_count: int
    failed_count: int
    all_passed: bool
    max_length: Optional[int]
    results: List[EquivalenceTestResult] = field(default_factory=list)
    methodology_note: str = ""

    def to_dataframe(self) -> pd.DataFrame:
        rows = []
        for r in self.results:
            rows.append({
                "Test Input": f"'{r.input_string}'" if r.input_string else "ε (Empty)",
                "Original Output": r.original_output if r.original_output else "ε",
                "Converted Output": r.converted_output if r.converted_output else "ε",
                "Alignment Strategy": r.alignment_applied,
                "Comparison Target": f"'{r.aligned_original}' vs '{r.aligned_converted}'",
                "Status": "✅ PASS" if r.passed else "❌ FAIL"
            })
        return pd.DataFrame(rows)


def check_string_equivalence(
    mealy: MealyMachine,
    moore: MooreMachine,
    input_string: str,
    direction: str = "Mealy -> Moore"
) -> EquivalenceTestResult:
    """
    Tests equivalence of Mealy and Moore machines on a specific input string.
    
    Alignment rule:
    - In Moore machines, the initial state emits output y0 at t=0 before reading input.
    - An input string of length n causes Moore to emit n+1 outputs: y0 . z1...zn.
    - Mealy machine emits n outputs: z1...zn.
    - Behaviorally equivalent iff Moore's transition output suffix matches Mealy's output.
    """
    mealy_trace = simulate_mealy(mealy, input_string)
    moore_trace = simulate_moore(moore, input_string)

    mealy_out = mealy_trace.output_string
    moore_out = moore_trace.output_string
    y0 = moore_trace.initial_output or ""
    moore_trans_out = moore_trace.transition_output_string

    if direction == "Mealy -> Moore":
        orig_out = mealy_out
        conv_out = moore_out
        # Align by comparing Mealy output with Moore's transition output suffix (ignoring y0)
        aligned_orig = orig_out
        aligned_conv = moore_trans_out
        alignment_desc = f"Moore suffix comparison (Discarded initial Moore output '{y0}')"
        passed = (aligned_orig == aligned_conv) and (conv_out == (y0 + orig_out))
        details = (
            f"Original Mealy produced '{orig_out}'. "
            f"Converted Moore produced '{conv_out}' (initial '{y0}' + transitions '{moore_trans_out}')."
        )
    else:  # Moore -> Mealy
        orig_out = moore_out
        conv_out = mealy_out
        aligned_orig = moore_trans_out
        aligned_conv = conv_out
        alignment_desc = f"Moore suffix comparison (Excluded original Moore initial output '{y0}')"
        passed = (aligned_orig == aligned_conv) and (orig_out == (y0 + conv_out))
        details = (
            f"Original Moore produced '{orig_out}' (initial '{y0}' + transitions '{moore_trans_out}'). "
            f"Converted Mealy produced '{conv_out}'."
        )

    return EquivalenceTestResult(
        input_string=input_string,
        original_output=orig_out,
        converted_output=conv_out,
        alignment_applied=alignment_desc,
        aligned_original=aligned_orig,
        aligned_converted=aligned_conv,
        passed=passed,
        details=details
    )


# Alias with __test__ = False so pytest does not treat it as a test function
test_string_equivalence = check_string_equivalence
test_string_equivalence.__test__ = False


def run_bounded_exhaustive_equivalence(
    mealy: MealyMachine,
    moore: MooreMachine,
    max_length: int = 3,
    direction: str = "Mealy -> Moore"
) -> BatchEquivalenceResult:
    """
    Generates all strings over Sigma up to length `max_length` (Sigma^0 union ... union Sigma^k).
    Executes equivalence check on each string.
    Note: As per automata theory, bounded verification verifies behavioral equivalence up to
    length k, serving as strong empirical testing rather than an inductive general proof.
    """
    alphabet = sorted(list(mealy.input_alphabet))
    test_strings = [""]  # Include empty string epsilon

    for length in range(1, max_length + 1):
        for combo in itertools.product(alphabet, repeat=length):
            test_strings.append("".join(combo))

    results: List[EquivalenceTestResult] = []
    passed_count = 0
    failed_count = 0

    for s in test_strings:
        res = test_string_equivalence(mealy, moore, s, direction=direction)
        results.append(res)
        if res.passed:
            passed_count += 1
        else:
            failed_count += 1

    methodology = (
        f"Bounded Exhaustive Verification over Σ = {{{', '.join(alphabet)}}} for lengths 0 to {max_length}. "
        f"Total generated test cases: {len(test_strings)}. "
        f"Notice: This is bounded testing over Σ^≤{max_length}, demonstrating empirical equivalence for all inputs in this range."
    )

    return BatchEquivalenceResult(
        total_tested=len(test_strings),
        passed_count=passed_count,
        failed_count=failed_count,
        all_passed=(failed_count == 0),
        max_length=max_length,
        results=results,
        methodology_note=methodology
    )


def run_standard_test_suite(
    mealy: MealyMachine,
    moore: MooreMachine,
    direction: str = "Mealy -> Moore"
) -> BatchEquivalenceResult:
    """
    Runs a representative suite of test cases:
    - Empty input epsilon
    - Single symbols
    - Alternating symbols
    - Repeated symbols
    - Paths exploring various state transitions
    """
    alphabet = sorted(list(mealy.input_alphabet))
    a0 = alphabet[0] if alphabet else "0"
    a1 = alphabet[1] if len(alphabet) > 1 else a0

    candidate_strings = [
        "",
        a0,
        a1,
        a0 * 2,
        a1 * 2,
        a0 + a1,
        a1 + a0,
        a0 + a1 + a0,
        a1 + a0 + a1,
        a0 * 4,
        a1 * 4,
        (a0 + a1) * 2,
        a0 + a0 + a1 + a1,
        a1 + a1 + a0 + a0
    ]

    # Deduplicate preserving order
    unique_candidates = list(dict.fromkeys(candidate_strings))

    results: List[EquivalenceTestResult] = []
    passed_count = 0
    failed_count = 0

    for s in unique_candidates:
        res = test_string_equivalence(mealy, moore, s, direction=direction)
        results.append(res)
        if res.passed:
            passed_count += 1
        else:
            failed_count += 1

    return BatchEquivalenceResult(
        total_tested=len(unique_candidates),
        passed_count=passed_count,
        failed_count=failed_count,
        all_passed=(failed_count == 0),
        max_length=None,
        results=results,
        methodology_note="Representative Suite Testing across edge cases, repetitions, and path alternations."
    )
