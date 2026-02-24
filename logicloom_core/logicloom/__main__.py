"""CLI entry point for LogicLoom: boolean minimization from command-line arguments."""

from __future__ import annotations

import argparse

from . import __app_name__, __version__
from .simplifier import LogicGateSimplifier


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for LogicLoom CLI."""
    parser = argparse.ArgumentParser(
        prog=__app_name__,
        description="Boolean logic minimization toolkit.",
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit.")
    parser.add_argument(
        "-v",
        "--vars",
        dest="variables",
        metavar="A,B,C",
        help="Comma-separated variable names.",
    )
    parser.add_argument(
        "-m",
        "--minterms",
        metavar="0,1,2",
        help="Comma-separated minterm numbers.",
    )
    parser.add_argument(
        "--output",
        choices=["string", "latex", "both"],
        default="string",
        help="Choose output format.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Print all minimal covers.",
    )
    parser.add_argument(
        "--pichart",
        choices=["terminal", "latex"],
        help="Print prime implicant chart.",
    )
    parser.add_argument(
        "--pitable",
        choices=["terminal"],
        help="Print prime implicants table (binary and literal form).",
    )
    parser.add_argument(
        "--essentials",
        choices=["terminal"],
        help="Print essential prime implicants table (binary and literal form).",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run bundled demo problems.",
    )
    return parser


def _print_equations(equations: list[dict[str, str]], output: str) -> None:
    """Print equation dicts to stdout according to output format (string, latex, or both)."""
    for idx, equation in enumerate(equations, start=1):
        if len(equations) > 1:
            print(f"Cover {idx}")
        if output in ("string", "both"):
            print(equation["string"])
        if output in ("latex", "both"):
            print(equation["latex"])
        if idx < len(equations):
            print()


def _run_problem(
    variables_str: str,
    minterms_str: str,
    output: str,
    show_all: bool,
    pichart: str | None,
    pitable: str | None,
    essentials: str | None,
) -> None:
    """Build simplifier, simplify, print equations and optional PI table/essentials/chart."""
    simplifier = LogicGateSimplifier.from_strings(variables_str, minterms_str)
    simplifier.simplify()
    equations = simplifier.get_all_equations()
    if not show_all:
        equations = equations[:1]
    _print_equations(equations, output)

    if pitable == "terminal":
        print()
        print("Prime implicants")
        print(simplifier.get_prime_implicants_terminal())
    if essentials == "terminal":
        print()
        print("Essential prime implicants")
        print(simplifier.get_essentials_terminal())
    if pichart == "terminal":
        print()
        print(simplifier.get_pichart_terminal(tick="x"))
    elif pichart == "latex":
        print()
        print(simplifier.get_pichart_latex())


def main() -> None:
    """Parse CLI args and run demo or single problem; print version and exit if --version."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.version:
        print(__version__)
        raise SystemExit(0)

    demo_problems = [
        ("w,x,y,z", "1,4,5,6,12,14,15"),
        ("A,B,C,D", "2,3,6,7,12,13,14"),
        ("w,x,y,z", "1,3,4,5,6,7,9,11,13,15"),
        ("A,B,C,D", "0,2,4,5,6,7,8,10,13,15"),
    ]

    if args.demo:
        for variables_str, minterms_str in demo_problems:
            _run_problem(
                variables_str,
                minterms_str,
                args.output,
                args.all,
                args.pichart,
                args.pitable,
                args.essentials,
            )
            print()
        return

    if not args.variables or not args.minterms:
        parser.error("Provide --vars and --minterms, or use --demo.")

    _run_problem(
        args.variables,
        args.minterms,
        args.output,
        args.all,
        args.pichart,
        args.pitable,
        args.essentials,
    )


if __name__ == "__main__":
    main()
