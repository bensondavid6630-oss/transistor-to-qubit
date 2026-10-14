# From Transistors to Qubits

A hybrid learning framework that starts from familiar semiconductor concepts (transistor switching, logic gates, digital circuits, noise) and moves step by step to quantum computing (qubits, quantum gates, superposition, measurement, decoherence). Built for **EDC Assignment #2**.

**Student:** _your name / student ID_

## The four levels

| Level | Classical idea | Quantum counterpart | Where |
|---|---|---|---|
| 1. Transistor | Vin 0/1 -> OFF/ON -> classical bit | Qubit as information unit | `t2q/transistor.py`, `arduino/` |
| 2. Logic gate | NOT: 0 <-> 1 | X gate: X\|0> = \|1> | `t2q/logic.py`, `t2q/quantum.py` |
| 3. Bit -> Qubit | b in {0,1} | \|psi> = a\|0> + b\|1>, H gate gives 50/50 | `t2q/quantum.py` |
| 4. Circuit vs circuit | Transistors -> gates -> output | Qubits -> gates -> measurement | `t2q/compare.py` |

Then: transistor noise `Vout = Videal + n(t)` vs bit-flip, phase-flip and depolarizing noise, plus a 3-qubit error-correcting code (`t2q/noise.py`), and a pre/post assessment with normalised gain (`t2q/assessment.py`).

## Project modules

| Module | File | What it does |
|---|---|---|
| A: Transistor simulator | `t2q/transistor.py` | BJT switch; vary base voltage, threshold, load resistance; see cutoff/active/saturation |
| B: Logic-gate simulator | `t2q/logic.py` | NOT, AND, OR, NAND, NOR, XOR, all rebuilt from NAND only |
| C: Quantum simulator | `t2q/quantum.py` | NumPy state-vector simulator: \|0>, \|1>, X, Y, Z, H, CNOT, measurement |
| D: Comparison | `t2q/compare.py` | Same function (NOT, XOR) classical vs quantum, comparison table |

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements-core.txt                  # NumPy + matplotlib + pytest
python main.py all          # run every demo
python main.py plots        # save figures to ./outputs
python main.py quiz         # interactive pre/post assessment
python -m pytest -q         # run the tests (or: python tests/test_framework.py)
```

Qiskit / IBM simulator (optional):

```bash
pip install -r requirements.txt
python qiskit_examples/level2_not_vs_x.py
python qiskit_examples/level3_hadamard.py
python qiskit_examples/level4_xor_bell.py
python qiskit_examples/noise_models.py
```

You can also paste any circuit into the [IBM Quantum Composer](https://quantum.ibm.com/composer).

## Hardware (Level 1)

BJT/MOSFET, breadboard, resistors, LED, Arduino/ESP32. Upload `arduino/transistor_switch.ino`, build the circuit described at the top of the file, and watch the Serial Monitor: Vin = 0 -> LED OFF, Vin = 1 -> LED ON.

## Interactive website

`docs/index.html` is a self-contained interactive version of all modules (no build step). To publish it with GitHub Pages:

1. Push this repository to GitHub.
2. **Settings -> Pages -> Build and deployment -> Source: Deploy from a branch**, branch `main`, folder `/docs`.
3. After a minute it is live at `https://<your-username>.github.io/<repo-name>/`.

## Deploy to GitHub

```bash
git init
git add .
git commit -m "Transistor-to-Qubit learning framework"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

The workflow in `.github/workflows/ci.yml` runs the tests on every push.

## Evaluation

* **Pre/post assessment:** `python main.py quiz` (or the Assessment tab on the website), reported as score and Hake normalised gain g = (post - pre) / (max - pre).
* **Circuit implementation tasks:** Level 2 and Level 4 programs in `qiskit_examples/` and `t2q/compare.py` (NOT and XOR implemented both ways and checked against each other).
* **Conceptual metrics:** noise experiments show that classical noise is removed by the digital threshold, whereas quantum noise acts on amplitudes and phases and needs error correction.
