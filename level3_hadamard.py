"""Level 3: bit -> qubit. H|0> = (|0> + |1>)/sqrt(2) gives P(0)=P(1)=50%."""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

qc = QuantumCircuit(1)
qc.h(0)
print("State vector (alpha, beta):", Statevector(qc).data)

qc.measure_all()
counts = AerSimulator().run(qc, shots=4096).result().get_counts()
print("Counts:", counts)
total = sum(counts.values())
print({k: f"{100 * v / total:.1f}%" for k, v in counts.items()})
