"""Module B - Logic-gate simulator (Level 2).

Every gate is also built from NAND only, mirroring how transistor-level
CMOS logic is built (NAND is a universal gate).
"""
from __future__ import annotations

from itertools import product


# --- direct gate definitions -------------------------------------------------
def NOT(a): return 1 - a
def AND(a, b): return a & b
def OR(a, b): return a | b
def NAND(a, b): return 1 - (a & b)
def NOR(a, b): return 1 - (a | b)
def XOR(a, b): return a ^ b


GATES = {"NOT": NOT, "AND": AND, "OR": OR, "NAND": NAND, "NOR": NOR, "XOR": XOR}


# --- NAND-only constructions -------------------------------------------------
def not_from_nand(a): return NAND(a, a)
def and_from_nand(a, b): return not_from_nand(NAND(a, b))
def or_from_nand(a, b): return NAND(not_from_nand(a), not_from_nand(b))
def nor_from_nand(a, b): return not_from_nand(or_from_nand(a, b))


def xor_from_nand(a, b):
    t = NAND(a, b)
    return NAND(NAND(a, t), NAND(b, t))   # 4 NAND gates


NAND_ONLY = {
    "NOT": not_from_nand, "AND": and_from_nand, "OR": or_from_nand,
    "NAND": NAND, "NOR": nor_from_nand, "XOR": xor_from_nand,
}


def truth_table(name: str):
    """Return rows ``(inputs, output)`` for the gate called ``name``."""
    f = GATES[name]
    if name == "NOT":
        return [((a,), f(a)) for a in (0, 1)]
    return [((a, b), f(a, b)) for a, b in product((0, 1), repeat=2)]


def verify_universality() -> bool:
    """True if every NAND-only circuit matches the direct gate."""
    for name in GATES:
        for inputs, out in truth_table(name):
            if NAND_ONLY[name](*inputs) != out:
                return False
    return True


def format_truth_tables() -> str:
    lines = []
    for name in GATES:
        lines.append(f"{name}")
        for inputs, out in truth_table(name):
            lines.append("  " + " ".join(map(str, inputs)) + f"  ->  {out}")
    return "\n".join(lines)


def demo() -> None:
    print("Level 2 - logic gates")
    print(format_truth_tables())
    print("\nAll gates rebuilt from NAND only:", verify_universality())
