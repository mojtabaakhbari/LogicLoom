"""Data types for prime implicant chart and terms."""

from __future__ import annotations

from dataclasses import dataclass

from .utils import to_binary_form


@dataclass
class PIChartRow:
    """One row of the PI chart: a minterm and the set of prime implicants covering it."""

    minterm: Term
    prime_implicants: set[Term]
    is_remaining: bool


@dataclass
class PIChartData:
    """Structured data for the prime implicant chart: minterm numbers, PI labels, and coverage matrix."""

    minterm_numbers: list[int | None]
    prime_implicants: list[str]
    matrix: list[list[bool]]


class Term:
    """A single term (minterm or prime implicant) with binary form and optional decimal number."""

    def __init__(self, binary_form: str, number: int | None = None) -> None:
        self.binary_form: str = binary_form
        self.number: int | None = number
        self.is_used: bool = False

    @classmethod
    def from_number(cls, number: int, length: int = 0) -> Term:
        """Create a Term from a decimal minterm number and optional bit length."""
        return cls(to_binary_form(number, length), number)

    @classmethod
    def from_binary_form(cls, binary_form: str) -> Term:
        """Create a Term from a binary string (e.g. '01-0')."""
        return cls(binary_form)

    def __eq__(self, other: object) -> bool:
        """Two terms are equal if their binary_form strings are equal."""
        if not isinstance(other, Term):
            return NotImplemented
        return self.binary_form == other.binary_form

    def __hash__(self) -> int:
        """Hash by binary_form for use in sets."""
        return hash(self.binary_form)

    def __getitem__(self, ind: int) -> str:
        """Return the character at index ind in binary_form."""
        return self.binary_form[ind]

    def __add__(self, other: Term) -> Term | None:
        """Combine two terms if they differ in exactly one bit; return combined term with '-' or None."""
        res_list: list[str] = []
        diff: bool = False
        for i, j in zip(self.binary_form, other.binary_form):
            if i == j:
                res_list.append(i)
            elif diff:
                return None
            else:
                res_list.append("-")
                diff = True
        return Term.from_binary_form("".join(res_list))

    def cover(self, other: Term) -> bool:
        """Return True if this term (e.g. implicant) covers the other term (minterm)."""
        return all(
            i == j or i == "-" for i, j in zip(self.binary_form, other.binary_form)
        )

    def __repr__(self) -> str:
        """Return binary_form string."""
        return self.binary_form

    def to_normal_expression(self, variables: list[str]) -> str:
        """Return product-of-literals string (e.g. xy'z) for this term using the given variable names."""
        parts: list[str] = []
        for bit, var in zip(self.binary_form, variables):
            if bit == "1":
                parts.append(var)
            elif bit == "0":
                parts.append(var + "'")
        return "".join(parts) if parts else "1"

    def to_latex_expression(self, variables: list[str]) -> str:
        """Return LaTeX product expression (e.g. x \\bar{y} z) for this term."""
        parts: list[str] = []
        for bit, var in zip(self.binary_form, variables):
            if bit == "1":
                parts.append(var)
            elif bit == "0":
                parts.append(r"\bar{" + var + "}")
        return r" \cdot ".join(parts) if parts else "1"
