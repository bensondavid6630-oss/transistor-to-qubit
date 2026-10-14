"""Module D - Classical vs quantum comparison (Level 4).

The same logical function is implemented twice:

    Classical : transistors -> logic gates   -> digital output
    Quantum   : qubits      -> quantum gates -> measurement
"""
from __future__ import annotations

from itertools import product

from . import logic
from .quantum import QuantumSimulator

COMPARISON_TABLE = [
    ("Bit", "Qubit"),
    ("0 / 1", "alpha, beta (complex amplitudes)"),
    ("NOT", "X"),
    ("Logic operation", "Quantum gate (unitary, reversible)"),
    ("Output", "Measurement"),
    ("Noise", "Quantum noise / decoherence"),
    ("Deterministic", "Probabilistic measurement"),
]


def quantum_not(a: int) -> int:
    """NOT(a) using one qubit and an X gate."""
    sim = QuantumSimulator(1)
    sim.set_basis_state([a])
    sim.x(0)
    return sim.measure_qubit(0)


def quantum_xor(a: int, b: int) -> int:
    """XOR(a, b) using two qubits and a CNOT (result lands on qubit 1)."""
    sim = QuantumSimulator(2)
    sim.set_basis_state([a, b])
    sim.cnot(0, 1)
    return sim.measure_qubit(1)


def compare_functions() -> list[dict]:
    """Truth-table comparison of NOT and XOR, classical vs quantum."""
    rows = []
    for a in (0, 1):
        rows.append({"fn": "NOT", "in": (a,), "classical": logic.NOT(a),
                     "quantum": quantum_not(a)})
    for a, b in product((0, 1), repeat=2):
        rows.append({"fn": "XOR", "in": (a, b), "classical": logic.XOR(a, b),
                     "quantum": quantum_xor(a, b)})
    for r in rows:
        r["match"] = r["classical"] == r["quantum"]
    return rows


def format_comparison() -> str:
    out = [f"{'Classical':<22}| Quantum", "-" * 60]
    out += [f"{c:<22}| {q}" for c, q in COMPARISON_TABLE]
    return "\n".join(out)


def demo() -> None:
    print("Level 4 - same function, two implementations\n")
    print(format_comparison())
    print("\nfunction  inputs  classical  quantum  match")
    for r in compare_functions():
        print(f"{r['fn']:<9} {str(r['in']):<7} {r['classical']:^9}  {r['quantum']:^7}  {r['match']}")
