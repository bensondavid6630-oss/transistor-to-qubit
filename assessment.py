"""Pre- and post-learning assessment with a normalised-gain metric."""
from __future__ import annotations

QUESTIONS = [
    ("A transistor used as a switch is in cutoff. The load current is:",
     ["Maximum", "Almost zero (switch OFF)", "Equal to the base current", "Negative"], 1),
    ("Which quantum gate is the counterpart of a classical NOT gate?",
     ["H", "Z", "X", "CNOT"], 2),
    ("Measuring the state H|0> many times gives:",
     ["Always 0", "Always 1", "50% 0 and 50% 1", "A value between 0 and 1"], 2),
    ("|alpha|^2 + |beta|^2 = 1 because:",
     ["Amplitudes are real", "Outcome probabilities must sum to 1",
      "The qubit must be |0> or |1>", "Voltage is limited to Vcc"], 1),
    ("Which noise process swaps |0> and |1> with probability p?",
     ["Phase-flip", "Bit-flip", "Amplifier gain error", "Thermal drift only"], 1),
    ("What does a digital circuit have that a bare qubit lacks?",
     ["A threshold that restores noisy levels to 0 or 1", "Superposition", "Gates", "Outputs"], 0),
    ("A CNOT with control = 1 and target = 0 produces target =",
     ["0", "1", "Superposition", "Undefined"], 1),
    ("Why can't classical error correction by copying be used for qubits?",
     ["Qubits are too fast", "No-cloning theorem", "Qubits have no noise", "Gates are irreversible"], 1),
]


def grade(answers: list[int]) -> int:
    """``answers[i]`` is the chosen option index (0-based) or -1 if skipped."""
    return sum(1 for (q, opts, correct), a in zip(QUESTIONS, answers) if a == correct)


def normalised_gain(pre: int, post: int, maximum: int | None = None) -> float:
    """Hake gain g = (post - pre) / (max - pre)."""
    maximum = maximum or len(QUESTIONS)
    return 0.0 if pre >= maximum else (post - pre) / (maximum - pre)


def run_cli(label: str = "assessment") -> int:
    print(f"\n=== {label} ===")
    answers = []
    for i, (q, opts, _) in enumerate(QUESTIONS, 1):
        print(f"\nQ{i}. {q}")
        for j, o in enumerate(opts, 1):
            print(f"   {j}) {o}")
        raw = input("Answer (1-4, Enter to skip): ").strip()
        answers.append(int(raw) - 1 if raw.isdigit() and 1 <= int(raw) <= len(opts) else -1)
    score = grade(answers)
    print(f"\nScore: {score}/{len(QUESTIONS)}")
    return score
