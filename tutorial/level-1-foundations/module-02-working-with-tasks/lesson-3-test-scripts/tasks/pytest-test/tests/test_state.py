"""
Pytest test file for the string_utils task.

This file is uploaded to /tests/ inside the container and run by test.sh.
Each test function verifies a specific behavior. Pytest collects results
and the CTRF plugin produces structured JSON output.
"""

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def string_utils():
    """Load the string_utils module from /app/string_utils.py."""
    spec = importlib.util.spec_from_file_location("string_utils", "/app/string_utils.py")
    assert spec is not None, "Could not find /app/string_utils.py"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestReverseString:
    def test_simple(self, string_utils):
        assert string_utils.reverse_string("hello") == "olleh"

    def test_empty(self, string_utils):
        assert string_utils.reverse_string("") == ""

    def test_palindrome(self, string_utils):
        assert string_utils.reverse_string("racecar") == "racecar"

    def test_spaces(self, string_utils):
        assert string_utils.reverse_string("a b c") == "c b a"


class TestCountVowels:
    def test_mixed_case(self, string_utils):
        assert string_utils.count_vowels("Hello World") == 3

    def test_all_vowels(self, string_utils):
        assert string_utils.count_vowels("aeiou") == 5

    def test_no_vowels(self, string_utils):
        assert string_utils.count_vowels("rhythm") == 0

    def test_empty(self, string_utils):
        assert string_utils.count_vowels("") == 0
