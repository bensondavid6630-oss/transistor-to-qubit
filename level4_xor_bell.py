"""Level 4: the same function (XOR) classically and with qubits, plus a Bell state."""
from itertools import product

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

sim = AerSimulator()

print("a b | classical a^b | quantum (CNOT)")
for a, b in product((0, 1), repeat=2):
    qc = QuantumCircuit(2, 1)
    if a: qc.x(0)
    if b: qc.x(1)
    qc.cx(0, 1)                # q1 <- a XOR b
    qc.measure(1, 0)
    out = max(sim.run(qc, shots=100).result().get_counts().items(), key=lambda kv: kv[1])[0]
    print(f"{a} {b} |       {a ^ b}       |  {out}")

bell = QuantumCircuit(2, 2)
bell.h(0)
bell.cx(0, 1)
bell.measure([0, 1], [0, 1])
print("\nBell state counts:", sim.run(bell, shots=1024).result().get_counts())   # only 00 and 11
