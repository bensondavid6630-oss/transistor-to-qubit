"""Module C - Quantum simulator (Levels 2-3), pure NumPy.

Qubit ordering is little-endian, the same convention as Qiskit: qubit 0 is the
least-significant bit and counts are printed as ``q(n-1) ... q1 q0``.
"""
from __future__ import annotations

import numpy as np

SQ2 = 1 / np.sqrt(2)
I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = SQ2 * np.array([[1, 1], [1, -1]], dtype=complex)

KET0 = np.array([1, 0], dtype=complex)
KET1 = np.array([0, 1], dtype=complex)


class QuantumSimulator:
    """State-vector simulator for a small register of qubits."""

    def __init__(self, n_qubits: int = 1, seed: int | None = None):
        self.n = n_qubits
        self.rng = np.random.default_rng(seed)
        self.reset()

    # ----- state -----------------------------------------------------------
    def reset(self):
        self.state = np.zeros(2 ** self.n, dtype=complex)
        self.state[0] = 1.0
        self.history: list[tuple] = []
        return self

    def set_basis_state(self, bits):
        """Initialise to a computational basis state. ``bits[k]`` is qubit k."""
        idx = sum(int(b) << k for k, b in enumerate(bits))
        self.state[:] = 0
        self.state[idx] = 1.0
        return self

    def set_single_qubit(self, alpha: complex, beta: complex):
        """Set a 1-qubit state alpha|0> + beta|1> (normalisation is checked)."""
        if self.n != 1:
            raise ValueError("set_single_qubit needs a 1-qubit simulator")
        if not np.isclose(abs(alpha) ** 2 + abs(beta) ** 2, 1.0):
            raise ValueError("|alpha|^2 + |beta|^2 must equal 1")
        self.state = np.array([alpha, beta], dtype=complex)
        return self

    # ----- gates -----------------------------------------------------------
    def apply(self, U: np.ndarray, qubit: int, label: str = "U"):
        axis = self.n - 1 - qubit
        psi = self.state.reshape((2,) * self.n)
        psi = np.moveaxis(np.tensordot(U, psi, axes=([1], [axis])), 0, axis)
        self.state = psi.reshape(-1)
        self.history.append((label, qubit))
        return self

    def x(self, q): return self.apply(X, q, "X")
    def y(self, q): return self.apply(Y, q, "Y")
    def z(self, q): return self.apply(Z, q, "Z")
    def h(self, q): return self.apply(H, q, "H")

    def cnot(self, control: int, target: int):
        idx = np.arange(2 ** self.n)
        flipped = np.where((idx >> control) & 1, idx ^ (1 << target), idx)
        self.state = self.state[flipped]
        self.history.append(("CNOT", control, target))
        return self

    # ----- read-out --------------------------------------------------------
    def amplitudes(self) -> np.ndarray:
        return self.state.copy()

    def probabilities(self) -> np.ndarray:
        return np.abs(self.state) ** 2

    def measure(self, shots: int = 1024) -> dict[str, int]:
        """Sample all qubits ``shots`` times (state is not collapsed)."""
        p = self.probabilities()
        draws = self.rng.multinomial(shots, p / p.sum())
        return {format(i, f"0{self.n}b"): int(c) for i, c in enumerate(draws) if c}

    def measure_qubit(self, qubit: int) -> int:
        """Projective measurement of one qubit; the state collapses."""
        idx = np.arange(2 ** self.n)
        mask1 = ((idx >> qubit) & 1) == 1
        p1 = float(np.sum(self.probabilities()[mask1]))
        outcome = int(self.rng.random() < p1)
        keep = mask1 if outcome else ~mask1
        self.state = np.where(keep, self.state, 0)
        self.state = self.state / np.linalg.norm(self.state)
        return outcome

    def bloch_vector(self, qubit: int = 0):
        """Bloch vector (x, y, z) of one qubit (reduced density matrix)."""
        psi = self.state.reshape((2,) * self.n)
        axis = self.n - 1 - qubit
        psi = np.moveaxis(psi, axis, 0).reshape(2, -1)
        rho = psi @ psi.conj().T
        return (
            float(2 * rho[0, 1].real),
            float(-2 * rho[0, 1].imag),
            float((rho[0, 0] - rho[1, 1]).real),
        )

    # ----- pretty printing -------------------------------------------------
    def describe(self) -> str:
        rows = []
        for i, a in enumerate(self.state):
            if abs(a) > 1e-12:
                rows.append(
                    f"  |{format(i, f'0{self.n}b')}>  amp={a.real:+.3f}{a.imag:+.3f}j  "
                    f"P={abs(a)**2:.3f}"
                )
        return "\n".join(rows)

    def draw(self) -> str:
        """ASCII circuit diagram of the gates applied so far."""
        lines = [f"q{k}: " for k in range(self.n)]
        for op in self.history:
            cells = ["---"] * self.n
            if op[0] == "CNOT":
                cells[op[1]], cells[op[2]] = "-o-", "-x-"
            else:
                cells[op[1]] = f"[{op[0]}]"
            for k in range(self.n):
                lines[k] += cells[k] + "-"
        return "\n".join(lines)


def demo() -> None:
    print("Level 2 - X gate (quantum NOT)")
    s = QuantumSimulator(1).x(0)
    print(s.describe(), "\n counts:", s.measure(1000))

    print("\nLevel 3 - Hadamard: superposition, P(0)=P(1)=50%")
    s = QuantumSimulator(1, seed=1).h(0)
    print(s.describe(), "\n counts:", s.measure(1000))

    print("\nZ gate on |+> gives |->  (phase flip, invisible in Z-basis counts)")
    s = QuantumSimulator(1).h(0).z(0)
    print(s.describe(), "\n Bloch vector:", np.round(s.bloch_vector(), 3))

    print("\nBell state: H on q0, CNOT q0 -> q1")
    s = QuantumSimulator(2, seed=2).h(0).cnot(0, 1)
    print(s.draw())
    print(s.describe(), "\n counts:", s.measure(1000))
