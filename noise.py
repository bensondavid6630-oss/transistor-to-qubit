"""Noise: classical transistor noise vs quantum noise / decoherence.

Classical :  Vout = Videal + n(t)          (continuous perturbation of a voltage;
                                            the digital threshold removes small noise)
Quantum   :  rho -> sum_k K_k rho K_k^dag  (Kraus channels: bit flip, phase flip,
                                            depolarizing) + error correction
"""
from __future__ import annotations

import math

import numpy as np

from .quantum import I2, X, Y, Z


# =============================================================================
# Classical noise
# =============================================================================
def noisy_signal(bits, sigma: float, vcc: float = 5.0, samples_per_bit: int = 8,
                 seed: int | None = None):
    """Return (ideal, noisy) waveforms for a bit stream: Vout = Videal + n(t)."""
    rng = np.random.default_rng(seed)
    ideal = np.repeat(np.asarray(bits) * vcc, samples_per_bit).astype(float)
    return ideal, ideal + rng.normal(0.0, sigma, ideal.size)


def decode(noisy, samples_per_bit: int = 8, vcc: float = 5.0):
    """Threshold decoder: sample once per bit and compare to Vcc/2."""
    return (np.asarray(noisy)[::samples_per_bit] > vcc / 2).astype(int)


def classical_ber(sigma: float, vcc: float = 5.0, n_bits: int = 100_000,
                  seed: int | None = 0) -> float:
    """Monte-Carlo bit error rate of a 0 V / Vcc signal in Gaussian noise."""
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, n_bits)
    received = bits * vcc + rng.normal(0.0, sigma, n_bits)
    return float(np.mean((received > vcc / 2).astype(int) != bits))


def theoretical_ber(sigma: float, vcc: float = 5.0) -> float:
    """Q(Vcc / (2 sigma)) = 0.5 * erfc(Vcc / (2 sigma sqrt(2)))."""
    if sigma == 0:
        return 0.0
    return 0.5 * math.erfc(vcc / (2 * sigma * math.sqrt(2)))


# =============================================================================
# Quantum noise (single qubit, density matrix + Kraus operators)
# =============================================================================
def ket_to_rho(ket) -> np.ndarray:
    ket = np.asarray(ket, dtype=complex).reshape(2, 1)
    return ket @ ket.conj().T


def kraus_bit_flip(p):      return [math.sqrt(1 - p) * I2, math.sqrt(p) * X]
def kraus_phase_flip(p):    return [math.sqrt(1 - p) * I2, math.sqrt(p) * Z]
def kraus_depolarizing(p):  return [math.sqrt(1 - p) * I2] + [math.sqrt(p / 3) * P for P in (X, Y, Z)]

CHANNELS = {"bit": kraus_bit_flip, "phase": kraus_phase_flip, "dep": kraus_depolarizing}


def apply_channel(rho: np.ndarray, kraus) -> np.ndarray:
    return sum(K @ rho @ K.conj().T for K in kraus)


def evolve(rho: np.ndarray, channel: str, p: float, steps: int) -> np.ndarray:
    kraus = CHANNELS[channel](p)
    for _ in range(steps):
        rho = apply_channel(rho, kraus)
    return rho


def bloch(rho: np.ndarray):
    return (float(2 * rho[0, 1].real), float(-2 * rho[0, 1].imag),
            float((rho[0, 0] - rho[1, 1]).real))


def purity(rho: np.ndarray) -> float:
    return float(np.trace(rho @ rho).real)


def prob_zero(rho):   return float(rho[0, 0].real)             # Z-basis P(0)
def prob_plus(rho):   return float((1 + bloch(rho)[0]) / 2)    # X-basis P(+)


# =============================================================================
# Quantum error correction: 3-qubit repetition code (bit-flip)
# =============================================================================
def repetition_code_error_rate(p: float, trials: int = 100_000,
                               seed: int | None = 0) -> tuple[float, float]:
    """Return (unprotected, protected) logical error rates by Monte Carlo."""
    rng = np.random.default_rng(seed)
    bare = float(np.mean(rng.random(trials) < p))
    flips = (rng.random((trials, 3)) < p).sum(axis=1)
    protected = float(np.mean(flips >= 2))          # majority vote fails
    return bare, protected


def repetition_code_theory(p: float) -> float:
    return 3 * p ** 2 - 2 * p ** 3


def demo() -> None:
    print("Classical: Vout = Videal + n(t)")
    for s in (0.3, 0.8, 1.5, 2.5):
        print(f"  sigma={s:3.1f} V  BER sim={classical_ber(s):.4f}  theory={theoretical_ber(s):.4f}")

    print("\nQuantum noise on |0> (z=+1) and |+> (x=+1), p=0.1, 5 steps")
    zero = ket_to_rho([1, 0])
    plus = ket_to_rho([1 / math.sqrt(2), 1 / math.sqrt(2)])
    for ch in CHANNELS:
        r0, rp = evolve(zero, ch, 0.1, 5), evolve(plus, ch, 0.1, 5)
        print(f"  {ch:<6} |0>: P(0)={prob_zero(r0):.3f}   |+>: P(+)={prob_plus(rp):.3f}  "
              f"purity(|+>)={purity(rp):.3f}")

    print("\n3-qubit repetition code (bit flips)")
    for p in (0.05, 0.1, 0.2, 0.4):
        bare, prot = repetition_code_error_rate(p)
        print(f"  p={p:4.2f}  bare={bare:.4f}  protected={prot:.4f}  theory={repetition_code_theory(p):.4f}")
