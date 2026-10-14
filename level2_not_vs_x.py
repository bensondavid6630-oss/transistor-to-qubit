"""Level 2: classical NOT gate  <->  quantum X gate (Qiskit + Aer)."""
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

sim = AerSimulator()

for start in (0, 1):
    qc = QuantumCircuit(1, 1)
    if start:
        qc.x(0)            # prepare |1>
    qc.x(0)                # the NOT operation: X|0> = |1>, X|1> = |0>
    qc.measure(0, 0)
    counts = sim.run(qc, shots=1024).result().get_counts()
    print(f"input |{start}>  ->  counts {counts}")
