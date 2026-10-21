"""
Unit tests for Equivalence and Bounded Verification.
"""

import pytest
from src.examples import get_mealy_examples, get_moore_examples
from src.mealy_to_moore import convert_mealy_to_moore
from src.moore_to_mealy import convert_moore_to_mealy
from src.equivalence import (
    check_string_equivalence,
    run_bounded_exhaustive_equivalence,
    run_standard_test_suite
)


def test_mealy_to_moore_equivalence():
    """
    Test that every Mealy preset converted to Moore produces equivalent outputs
    under the standard Moore suffix alignment: Moore(w) = y0 . Mealy(w).
    """
    mealy_presets = get_mealy_examples()
    for name, mealy in mealy_presets.items():
        moore, _ = convert_mealy_to_moore(mealy)
        
        # Test standard suite
        suite_res = run_standard_test_suite(mealy, moore, direction="Mealy -> Moore")
        assert suite_res.all_passed, f"Standard suite failed on {name}: {suite_res.failed_count} failures"
        
        # Test bounded exhaustive testing up to length 3 (15 test strings for binary alphabet)
        bounded_res = run_bounded_exhaustive_equivalence(mealy, moore, max_length=3, direction="Mealy -> Moore")
        assert bounded_res.all_passed, f"Bounded testing failed on {name}: {bounded_res.failed_count} failures"


def test_moore_to_mealy_equivalence():
    """
    Test that every Moore preset converted to Mealy produces equivalent outputs
    under the standard Moore suffix alignment.
    """
    moore_presets = get_moore_examples()
    for name, moore in moore_presets.items():
        mealy, _ = convert_moore_to_mealy(moore)
        
        # Test standard suite
        suite_res = run_standard_test_suite(mealy, moore, direction="Moore -> Mealy")
        assert suite_res.all_passed, f"Standard suite failed on {name}: {suite_res.failed_count} failures"
        
        # Test bounded exhaustive testing up to length 3
        bounded_res = run_bounded_exhaustive_equivalence(mealy, moore, max_length=3, direction="Moore -> Mealy")
        assert bounded_res.all_passed, f"Bounded testing failed on {name}: {bounded_res.failed_count} failures"


def test_empty_string_equivalence():
    mealy_presets = get_mealy_examples()
    mealy = mealy_presets["Two's Complement Generator (Forces State Splitting)"]
    moore, _ = convert_mealy_to_moore(mealy)
    
    res = check_string_equivalence(mealy, moore, "", direction="Mealy -> Moore")
    assert res.passed
    assert res.aligned_original == ""
    assert res.aligned_converted == ""
