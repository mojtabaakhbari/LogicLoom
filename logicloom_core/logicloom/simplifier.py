"""Boolean minimization: prime implicants, essentials, and minimal covers."""

from __future__ import annotations

from collections import defaultdict
from itertools import pairwise
import math

from .utils import normalize_variables, normalize_minterms

from .types import PIChartData, PIChartRow, Term


class LogicGateSimplifier:
    """Minimizes a boolean function given variable names and minterm list; supports PI chart and Petrick."""

    @classmethod
    def from_strings(
        cls, variables_str: str, minterms_str: str
    ) -> "LogicGateSimplifier":
        """Build a LogicGateSimplifier from comma-separated variable and minterm strings."""
        variables = [v.strip() for v in variables_str.split(",") if v.strip()]
        minterm_nums = [int(m.strip()) for m in minterms_str.split(",") if m.strip()]
        return cls(minterms=minterm_nums, variables=variables)

    def __init__(
        self,
        minterms: list[int],
        variables: list[str],
    ) -> None:
        """Initialize with minterm numbers and variable names; validates variable count vs max minterm."""
        self.variables: list[str] = normalize_variables(variables)
        num_vars = len(variables)
        if num_vars != int(math.log2(max(minterms))) + 1:
            raise ValueError(
                f"Number of variables ({num_vars}) does not match max minterm ({max(minterms)})."
            )
        minterms = normalize_minterms(minterms)
        self.main_minterms: list[Term] = [
            Term.from_number(n, num_vars) for n in minterms
        ]
        self._function_string: str = f"F({','.join(str(i) for i in self.variables)}) = "
        self.prime_implicants: set[Term] = set()
        self.essentials: list[Term] = list()
        self.pichart: list[PIChartRow] = list()
        self._minimal_cover: list[Term] = []
        self._all_minimal_covers: list[list[Term]] = []
        self._has_run: bool = False

    def simplify(self) -> list[Term]:
        """Run grouping and Petrick; return one minimal cover and populate prime_implicants/essentials/pichart."""
        groups: list[list[Term]] = self._make_groups_by_count_of_1(self.main_minterms)
        self._get_prime_implicants(groups)
        self._get_essentials(self.prime_implicants, self.main_minterms)

        remaining_rows: list[PIChartRow] = [
            row for row in self.pichart if row.is_remaining
        ]
        if remaining_rows:
            petrick_solutions: list[set[Term]] = self._petrick_solution(remaining_rows)
            self._all_minimal_covers = [
                [*self.essentials, *sol] for sol in petrick_solutions
            ]
            self._minimal_cover = self._all_minimal_covers[0]
        else:
            self._minimal_cover = self.essentials.copy()
            self._all_minimal_covers = [self._minimal_cover]

        self._has_run = True
        return self._minimal_cover

    def get_all_minimal_covers(self) -> list[list[Term]]:
        """Return all minimal covers (each a list of Terms); runs simplify() if not yet run."""
        if not self._has_run:
            self.simplify()
        return self._all_minimal_covers

    def get_equation_latex(self) -> str:
        """Return LaTeX string for the first minimal cover; runs simplify() if not yet run."""
        if not self._has_run:
            self.simplify()
        terms_latex = [
            term.to_latex_expression(self.variables) for term in self._minimal_cover
        ]
        return self._get_boolean_function_expression(terms_latex)

    def _get_boolean_function_expression(self, terms: list[str]) -> str:
        """Format the boolean function header plus sum of the given term strings."""
        return f"{self._function_string}{' + '.join(terms)}"

    def get_all_equations(
        self,
    ) -> list[dict[str, str]]:
        """Return list of dicts with 'string' and 'latex' keys for each minimal cover; runs simplify() if needed."""
        if not self._has_run:
            self.simplify()
        result: list[dict[str, str]] = []
        for cover in self._all_minimal_covers:
            terms_str = [term.to_normal_expression(self.variables) for term in cover]
            terms_latex = [term.to_latex_expression(self.variables) for term in cover]

            result.append(
                {
                    "string": self._get_boolean_function_expression(terms_str),
                    "latex": self._get_boolean_function_expression(terms_latex),
                }
            )
        return result

    def get_pichart_data(self) -> PIChartData:
        """Return PIChartData (minterm numbers, PI labels, coverage matrix); runs simplify() if not yet run."""
        if not self._has_run:
            self.simplify()
        pis_sorted = sorted(self.prime_implicants, key=lambda t: t.binary_form)
        minterm_nums = [row.minterm.number for row in self.pichart]
        matrix = [
            [pi in row.prime_implicants for pi in pis_sorted] for row in self.pichart
        ]
        return PIChartData(
            minterm_numbers=minterm_nums,
            prime_implicants=[t.binary_form for t in pis_sorted],
            matrix=matrix,
        )

    def get_pichart_latex(self, tick: str = r"$\checkmark$") -> str:
        """Return LaTeX tabular for the prime implicant chart; runs simplify() if not yet run."""
        if not self._has_run:
            self.simplify()
        data = self.get_pichart_data()
        cols = "|" + "c|" * (len(data.prime_implicants) + 1)

        binary_minterms = [row.minterm.binary_form for row in self.pichart]
        binary_minterms.sort()
        header = "Minterm & " + " & ".join(data.prime_implicants) + r" \\"
        hline = r"\hline"
        rows = []
        for i, bin_m in enumerate(binary_minterms):
            marks = [
                tick if data.matrix[i][j] else ""
                for j in range(len(data.prime_implicants))
            ]
            rows.append(bin_m + " & " + " & ".join(marks) + r" \\")
        body = (
            hline
            + "\n"
            + header
            + "\n"
            + hline
            + "\n"
            + (hline + "\n").join(rows)
            + "\n"
            + hline
        )
        return r"\begin{tabular}" + f"{{{cols}}}\n" + body + r"\end{tabular}"

    def get_pichart_terminal(self, tick: str = "x") -> str:
        """Return box-drawing PI chart as a string for terminal output; runs simplify() if not yet run."""
        if not self._has_run:
            self.simplify()
        data = self.get_pichart_data()

        binary_minterms = [row.minterm.binary_form for row in self.pichart]
        binary_minterms.sort()
        headers = ["Minterm"] + data.prime_implicants
        all_rows = [headers] + [
            [binary_minterms[i]]
            + [
                tick if data.matrix[i][j] else ""
                for j in range(len(data.prime_implicants))
            ]
            for i in range(len(data.minterm_numbers))
        ]
        col_widths = [
            max(len(str(all_rows[r][c])) for r in range(len(all_rows)))
            for c in range(len(headers))
        ]
        col_widths = [max(w, 2) for w in col_widths]

        def pad(s: str, w: int) -> str:
            return str(s).center(w)

        top = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
        mid = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        bot = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

        lines = [top]
        for ri, row in enumerate(all_rows):
            cells = [pad(row[c], col_widths[c]) for c in range(len(headers))]
            lines.append("│ " + " │ ".join(cells) + " │")
            if ri < len(all_rows) - 1:
                lines.append(mid)
        lines.append(bot)
        return "\n".join(lines)

    def _terminal_table(self, headers: list[str], rows: list[list[str]]) -> str:
        """Build a box-drawing terminal table from headers and row cells."""
        all_rows = [headers] + rows
        col_widths = [
            max(len(str(all_rows[r][c])) for r in range(len(all_rows)))
            for c in range(len(headers))
        ]
        col_widths = [max(w, 2) for w in col_widths]

        def pad(s: str, w: int) -> str:
            return str(s).center(w)

        top = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
        mid = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        bot = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"
        lines = [top]
        for ri, row in enumerate(all_rows):
            cells = [pad(row[c], col_widths[c]) for c in range(len(headers))]
            lines.append("│ " + " │ ".join(cells) + " │")
            if ri < len(all_rows) - 1:
                lines.append(mid)
        lines.append(bot)
        return "\n".join(lines)

    def get_prime_implicants_terminal(self) -> str:
        """Return prime implicants table (binary and literal form) as a terminal string."""
        if not self._has_run:
            self.simplify()
        pis_sorted = sorted(self.prime_implicants, key=lambda t: t.binary_form)
        rows = [
            [t.binary_form, t.to_normal_expression(self.variables)]
            for t in pis_sorted
        ]
        return self._terminal_table(["Binary", "Literal"], rows)

    def get_essentials_terminal(self) -> str:
        """Return essential prime implicants table (binary and literal form) as a terminal string."""
        if not self._has_run:
            self.simplify()
        rows = [
            [t.binary_form, t.to_normal_expression(self.variables)]
            for t in self.essentials
        ]
        return self._terminal_table(["Binary", "Literal"], rows)

    def _product_two_sets(self, set1: set[Term], set2: set[Term]) -> list[set[Term]]:
        """Return list of sets each being set1 union one element of set2."""
        return [set1 | {j} for j in set2]

    def _is_superset(self, set1: set[Term], set2: set[Term]) -> bool:
        """Return True if set1 is a superset of set2."""
        return len(set1) >= len(set2) and set2.issubset(set1)

    def _remove_supersets(self, list_of_sets: list[set[Term]]) -> list[set[Term]]:
        """Return list with any set that is a superset of another removed."""
        if len(list_of_sets) <= 1:
            return list_of_sets
        sorted_sets = sorted(list_of_sets, key=len)
        result: list[set[Term]] = []
        for i, current_set in enumerate(sorted_sets):
            is_superset_of_other = False
            for j in range(i):
                if self._is_superset(current_set, sorted_sets[j]):
                    is_superset_of_other = True
                    break
            if not is_superset_of_other:
                result.append(current_set)
        return result

    def _product_all_sets(self, sets: list[set[Term]]) -> list[set[Term]]:
        """Expand product of sets and remove supersets; used for Petrick sum-of-products."""
        if len(sets) == 1:
            return [{pi} for pi in sets[0]]
        result: list[set[Term]] = [{i, j} for i in sets[0] for j in sets[1]]
        result = self._remove_supersets(result)
        for i in range(2, len(sets)):
            temp: list[set[Term]] = []
            for term in result:
                temp.extend(self._product_two_sets(term, sets[i]))
            result = self._remove_supersets(temp)
        return result

    def _get_least_products_sets(
        self, list_of_sets: list[set[Term]]
    ) -> list[set[Term]]:
        """Return those sets with minimum cardinality."""
        if len(list_of_sets) == 1:
            return list_of_sets
        least_products_set_length = len(min(list_of_sets, key=len))
        return [st for st in list_of_sets if len(st) == least_products_set_length]

    def _compute_count(self, _set: set[Term]) -> int:
        """Return total literal count (0s + 1s) in binary forms of terms in the set."""
        return sum(pi.binary_form.count("0") + pi.binary_form.count("1") for pi in _set)

    def _compute_literal_counts(self, list_of_sets: list[set[Term]]) -> list[int]:
        """Return list of literal counts for each set."""
        return [self._compute_count(st) for st in list_of_sets]

    def _get_least_literals_sets(
        self, list_of_sets: list[set[Term]]
    ) -> list[set[Term]]:
        """Return those sets with minimum total literal count."""
        if len(list_of_sets) == 1:
            return list_of_sets
        literal_counts = self._compute_literal_counts(list_of_sets)
        min_length = min(literal_counts)

        return [st for lc, st in zip(literal_counts, list_of_sets) if lc == min_length]

    def _petrick_solution(
        self,
        table: list[PIChartRow],
    ) -> list[set[Term]]:
        """Apply Petrick's method to remaining chart rows; return minimal cover sets (least literals)."""
        all_remains_pis: list[set[Term]] = [row.prime_implicants for row in table]
        all_products = self._product_all_sets(all_remains_pis)
        all_least_products = self._get_least_products_sets(all_products)
        return self._get_least_literals_sets(all_least_products)

    def _marked_once(self, row: PIChartRow) -> Term | None:
        """Return the single prime implicant covering this row if exactly one, else None."""
        pis: set[Term] = row.prime_implicants
        if len(pis) == 1:
            return next(iter(pis))
        return None

    def _mark_terms(
        self, prime_implicants: set[Term], main_minterms: list[Term]
    ) -> list[PIChartRow]:
        """Build PI chart rows: for each minterm, set of covering prime implicants; all is_remaining True."""
        result: list[PIChartRow] = []
        for minterm in main_minterms:
            covering_pis = {pi for pi in prime_implicants if pi.cover(minterm)}
            result.append(PIChartRow(minterm, covering_pis, True))
        return result

    def _mark_all_minterms_covered_by_pi(
        self, table: list[PIChartRow], pi: Term
    ) -> None:
        """Set is_remaining False for every row that contains pi."""
        for row in table:
            if pi in row.prime_implicants:
                row.is_remaining = False

    def _get_essentials(
        self, prime_implicants: set[Term], main_minterms: list[Term]
    ) -> None:
        """Build pichart and extract essential prime implicants by iteratively marking single-covered minterms."""
        table: list[PIChartRow] = self._mark_terms(prime_implicants, main_minterms)
        self.pichart = table
        essentials: list[Term] = list()

        while True:
            for row in table:
                if row.is_remaining and (pi := self._marked_once(row)):
                    essentials.append(pi)
                    self._mark_all_minterms_covered_by_pi(table, pi)
                    break
            else:
                break
        self.essentials = essentials

    def _make_groups_by_count_of_1(self, minterms: list[Term]) -> list[list[Term]]:
        """Group minterms by number of 1s in binary form; return list of groups in order of count."""
        groups: dict[int, list[Term]] = defaultdict(list)
        for m in minterms:
            count = m.binary_form.count("1")
            groups[count].append(m)

        return [group for _, group in sorted(groups.items())]

    def _combine_groups(self, gp1: list[Term], gp2: list[Term]) -> list[Term]:
        """Combine adjacent groups: terms that differ in one bit are merged (marked used); return new terms."""
        combined_groups: list[Term] = []
        for term1 in gp1:
            for term2 in gp2:
                if match_term := term1 + term2:
                    term1.is_used = term2.is_used = True
                    combined_groups.append(match_term)
        return combined_groups

    def _get_prime_implicants(self, groups: list[list[Term]]) -> None:
        """Run grouping until no more combinations; set prime_implicants to unused terms."""
        prime_implicants: set[Term] = set()

        while True:
            stop: bool = True
            new_group: list[list[Term]] = []
            for g1, g2 in pairwise(groups):
                if combined_terms := self._combine_groups(g1, g2):
                    stop = False
                    new_group.append(combined_terms)
            prime_implicants.update(pi for gp in groups for pi in gp if not pi.is_used)
            if stop:
                break
            groups = new_group
        self.prime_implicants = prime_implicants
