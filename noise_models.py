"""Quantum noise vs classical noise: bit-flip, phase-flip, depolarizing + QEC.

Idle gates ('id') carry the noise. Compare the three channels on |0> and |+>.
"""
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, pauli_error

P, STEPS, SHOTS = 0.1, 5, 8192

CHANNELS = {
    "bit-flip":    pauli_error([("X", P), ("I", 1 - P)]),
    "phase-flip":  pauli_error([("Z", P), ("I", 1 - P)]),
    "depolarizing": depolarizing_error(P, 1),
}


def run(channel, prepare_plus):
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(CHANNELS[channel], ["id"])
    qc = QuantumCircuit(1, 1)
    if prepare_plus:
        qc.h(0)
    for _ in range(STEPS):
        qc.id(0)
    if prepare_plus:
        qc.h(0)                 # rotate X basis -> Z basis so P(+) shows up as P(0)
    qc.measure(0, 0)
    sim = AerSimulator(noise_model=nm)
    counts = sim.run(transpile(qc, sim, optimization_level=0), shots=SHOTS).result().get_counts()
    return counts.get("0", 0) / SHOTS


print(f"p = {P}, {STEPS} noisy steps")
print(f"{'channel':<14}{'P(0) from |0>':>16}{'P(+) from |+>':>16}")
for name in CHANNELS:
    print(f"{name:<14}{run(name, False):>16.3f}{run(name, True):>16.3f}")

# --- 3-qubit bit-flip code: encode, inject error, majority-vote correct -----------
qc = QuantumCircuit(3, 1)
qc.cx(0, 1); qc.cx(0, 2)        # encode |0> -> |000>
qc.x(1)                         # single bit-flip error on qubit 1
qc.cx(0, 1); qc.cx(0, 2)        # syndrome extraction
qc.ccx(2, 1, 0)                 # correct qubit 0 (majority)
qc.measure(0, 0)
print("\nRepetition code corrects a single flip:",
      AerSimulator().run(qc, shots=100).result().get_counts())
