#!/usr/bin/env python3
"""Transistor-to-Qubit learning framework - command-line entry point.

    python main.py all          run every demo (A, B, C, D, noise)
    python main.py transistor   Module A
    python main.py logic        Module B
    python main.py quantum      Module C
    python main.py compare      Module D
    python main.py noise        classical vs quantum noise, error correction
    python main.py plots        save PNG figures to ./outputs (needs matplotlib)
    python main.py quiz         interactive pre/post assessment
"""
import argparse

from t2q import assessment, compare, logic, noise, quantum, transistor


def run_plots():
    try:
        from t2q import plots
    except ImportError:
        print("matplotlib is required: pip install matplotlib")
        return
    for path in plots.all_plots("outputs"):
        print("saved", path)


def run_quiz():
    pre = assessment.run_cli("PRE-assessment (before the modules)")
    input("\nWork through the modules, then press Enter for the post-test...")
    post = assessment.run_cli("POST-assessment")
    print(f"\nPre {pre}  Post {post}  normalised gain = {assessment.normalised_gain(pre, post):.2f}")


COMMANDS = {
    "transistor": transistor.demo,
    "logic": logic.demo,
    "quantum": quantum.demo,
    "compare": compare.demo,
    "noise": noise.demo,
    "plots": run_plots,
    "quiz": run_quiz,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("command", choices=["all", *COMMANDS], nargs="?", default="all")
    cmd = ap.parse_args().command
    if cmd == "all":
        for name in ("transistor", "logic", "quantum", "compare", "noise"):
            print("\n" + "=" * 72 + f"\n{name.upper()}\n" + "=" * 72)
            COMMANDS[name]()
    else:
        COMMANDS[cmd]()


if __name__ == "__main__":
    main()
