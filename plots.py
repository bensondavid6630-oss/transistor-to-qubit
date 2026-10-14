"""Optional matplotlib figures (saved as PNG). Requires matplotlib."""
from __future__ import annotations

import os

import numpy as np

from . import noise
from .quantum import QuantumSimulator
from .transistor import BJTSwitch


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def _save(fig, outdir, name):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    fig.savefig(path, dpi=140, bbox_inches="tight")
    return path


def transistor_curve(outdir="outputs"):
    plt = _plt()
    sw = BJTSwitch()
    d = sw.sweep()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(d["vin"], d["vout"], label="Vout (collector) [V]")
    ax.plot(d["vin"], d["ic"] * 1e3, label="Ic [mA]")
    ax.axvline(sw.vth, ls="--", c="gray", label="threshold")
    ax.set_xlabel("Vin [V]"); ax.set_title("Module A: BJT switch transfer curve")
    ax.legend(); ax.grid(alpha=.3)
    return _save(fig, outdir, "transistor_transfer_curve.png")


def hadamard_histogram(outdir="outputs"):
    plt = _plt()
    counts = QuantumSimulator(1, seed=3).h(0).measure(1024)
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(list(counts), list(counts.values()))
    ax.set_title("H|0>: 1024 shots"); ax.set_ylabel("counts")
    return _save(fig, outdir, "hadamard_histogram.png")


def classical_noise_waveform(outdir="outputs", sigma=0.8):
    plt = _plt()
    rng = np.random.default_rng(4)
    bits = rng.integers(0, 2, 24)
    ideal, noisy = noise.noisy_signal(bits, sigma, seed=5)
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(ideal, "--", c="gray", label="ideal"); ax.plot(noisy, lw=1, label="noisy")
    ax.axhline(2.5, c="r", lw=.8, label="threshold")
    ax.set_title(f"Vout = Videal + n(t), sigma = {sigma} V"); ax.legend(ncol=3)
    return _save(fig, outdir, "classical_noise.png")


def quantum_noise_decay(outdir="outputs", p=0.1, steps=30):
    plt = _plt()
    zero = noise.ket_to_rho([1, 0]); plus = noise.ket_to_rho([1, 1] / np.sqrt(2))
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.5), sharey=True)
    for ax, (name, rho0, probe) in zip(axs, [("|0>  (P0 in Z basis)", zero, noise.prob_zero),
                                              ("|+>  (P+ in X basis)", plus, noise.prob_plus)]):
        for ch in noise.CHANNELS:
            ax.plot([probe(noise.evolve(rho0, ch, p, n)) for n in range(steps + 1)], label=ch)
        ax.set_title(name); ax.set_xlabel("noise steps"); ax.grid(alpha=.3)
    axs[0].set_ylabel("probability"); axs[0].legend()
    return _save(fig, outdir, "quantum_noise_decay.png")


def repetition_code_curve(outdir="outputs"):
    plt = _plt()
    ps = np.linspace(0.01, 0.5, 50)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(ps, ps, label="unprotected"); ax.plot(ps, 3 * ps**2 - 2 * ps**3, label="3-qubit code")
    ax.set_xlabel("physical error p"); ax.set_ylabel("logical error"); ax.legend(); ax.grid(alpha=.3)
    return _save(fig, outdir, "repetition_code.png")


def all_plots(outdir="outputs"):
    return [f(outdir) for f in (transistor_curve, hadamard_histogram, classical_noise_waveform,
                                 quantum_noise_decay, repetition_code_curve)]
