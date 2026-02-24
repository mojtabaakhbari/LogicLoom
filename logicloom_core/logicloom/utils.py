"""Utility functions for variable and minterm normalization and binary formatting."""

from __future__ import annotations


def normalize_variables(variables: list[str]) -> list[str]:
    """Return list of variables with duplicates removed, preserving order."""
    seen: set[str] = set()
    return [var for var in variables if var not in seen]


def normalize_minterms(minterms: list[int]) -> list[int]:
    """Return list of minterms with duplicates removed, preserving order."""
    seen: set[int] = set()
    return [minterm for minterm in minterms if minterm not in seen]


def to_binary_form(number: int, length: int = 0) -> str:
    """Format number as binary string, zero-padded to length if length > 0."""
    return f"{number:0{length}b}"
