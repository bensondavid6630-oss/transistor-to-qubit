"""Run with:  python -m pytest -q   (or: python tests/test_framework.py)"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from t2q import assessment, compare, logic, noise
from t2q.quantum import QuantumSimulator
from t2q.transistor import BJTSwitch


# ---- Module A ---------------------------------------------------------------
def test_transistor_off_and_on():
    sw = BJTSwitch()
    off, on = sw.solve(0.0), sw.solve(5.0)
    assert off["region"] == "cutoff" and not off["led_on"] and off["output_bit"] == 1
    assert on["region"] == "saturation" and on["led_on"] and on["output_bit"] == 0
    assert math.isclose(on["vout"], sw.vce_sat)


def test_transistor_is_inverter_and_monotonic():
    d = BJTSwitch().sweep()
    assert np.all(np.diff(d["vout"]) <= 1e-12)
    assert np.all(np.diff(d["ic"]) >= -1e-12)


def test_load_resistance_sets_saturation_current():
    assert BJTSwitch(rc=100).i_sat > BJTSwitch(rc=1000).i_sat


# ---- Module B ---------------------------------------------------------------
def test_truth_tables():
    assert [logic.NAND(a, b) for a in (0, 1) for b in (0, 1)] == [1, 1, 1, 0]
    assert [logic.XOR(a, b) for a in (0, 1) for b in (0, 1)] == [0, 1, 1, 0]
    assert [logic.NOR(a, b) for a in (0, 1) for b in (0, 1)] == [1, 0, 0, 0]


def test_nand_universal():
    assert logic.verify_universality()


# ---- Module C ---------------------------------------------------------------
def test_x_gate_is_quantum_not():
    for a in (0, 1):
        s = QuantumSimulator(1).set_basis_state([a]).x(0)
        assert s.measure_qubit(0) == 1 - a


def test_hadamard_superposition():
    s = QuantumSimulator(1).h(0)
    assert np.allclose(s.probabilities(), [0.5, 0.5])
    counts = QuantumSimulator(1, seed=0).h(0).measure(10_000)
    assert abs(counts["0"] - 5000) < 300


def test_h_twice_is_identity_and_z_flips_phase():
    assert np.allclose(QuantumSimulator(1).h(0).h(0).amplitudes(), [1, 0])
    assert np.allclose(QuantumSimulator(1).h(0).z(0).amplitudes(), [2 ** -.5, -2 ** -.5])


def test_cnot_and_bell_state():
    s = QuantumSimulator(2).set_basis_state([1, 0]).cnot(0, 1)
    assert np.allclose(s.probabilities(), [0, 0, 0, 1])          # |11>
    bell = QuantumSimulator(2, seed=1).h(0).cnot(0, 1)
    assert set(bell.measure(500)) == {"00", "11"}


def test_normalisation_check():
    try:
        QuantumSimulator(1).set_single_qubit(1, 1)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


# ---- Module D ---------------------------------------------------------------
def test_classical_equals_quantum():
    assert all(r["match"] for r in compare.compare_functions())


# ---- Noise ------------------------------------------------------------------
def test_classical_ber_matches_theory():
    for s in (0.8, 1.5, 2.5):
        assert abs(noise.classical_ber(s, n_bits=200_000) - noise.theoretical_ber(s)) < 0.005


def test_bit_flip_and_phase_flip_effects():
    zero = noise.ket_to_rho([1, 0])
    plus = noise.ket_to_rho([2 ** -.5, 2 ** -.5])
    p, n = 0.1, 5
    # bit flip: z -> (1-2p)^n z, |+> untouched
    assert math.isclose(noise.bloch(noise.evolve(zero, "bit", p, n))[2], (1 - 2 * p) ** n)
    assert math.isclose(noise.prob_plus(noise.evolve(plus, "bit", p, n)), 1.0)
    # phase flip: |0> untouched, |+> loses coherence
    assert math.isclose(noise.prob_zero(noise.evolve(zero, "phase", p, n)), 1.0)
    assert math.isclose(noise.bloch(noise.evolve(plus, "phase", p, n))[0], (1 - 2 * p) ** n)
    # depolarizing: shrink factor 1 - 4p/3
    assert math.isclose(noise.bloch(noise.evolve(zero, "dep", p, n))[2], (1 - 4 * p / 3) ** n)


def test_repetition_code_helps_below_half():
    bare, prot = noise.repetition_code_error_rate(0.1, trials=200_000)
    assert prot < bare
    assert abs(prot - noise.repetition_code_theory(0.1)) < 0.005


# ---- Assessment -------------------------------------------------------------
def test_assessment():
    perfect = [c for _, _, c in assessment.QUESTIONS]
    assert assessment.grade(perfect) == len(perfect)
    assert math.isclose(assessment.normalised_gain(4, 8, 8), 1.0)


if __name__ == "__main__":      # tiny runner so pytest is optional
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for f in fns:
        f()
        print("PASS", f.__name__)
    print(f"{len(fns)} tests passed")
