"""Check sequence and window separation in two NUDT-MIRSDT split lists."""

import argparse
from pathlib import Path
import re


WINDOW = re.compile(r"Sequence([0-9]+)(?:/Mix/|_)([0-9]+)\.(?:mat|png)")


def read_windows(path):
    windows = {}
    with path.open(encoding="utf-8-sig") as stream:
        for line_number, line in enumerate(stream, start=1):
            entry = line.strip()
            if not entry:
                continue
            match = WINDOW.fullmatch(entry)
            if match is None:
                raise ValueError(f"{path}:{line_number}: invalid window name {entry!r}")
            identity = tuple(map(int, match.groups()))
            if identity in windows:
                raise ValueError(
                    f"{path}:{line_number}: duplicate window {entry!r} "
                    f"(first listed on line {windows[identity]})"
                )
            windows[identity] = line_number
    if not windows:
        raise ValueError(f"{path}: empty split")
    return set(windows)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Use one window per line, e.g. Sequence12/Mix/00042.mat or "
            "Sequence12_00042.png. Sequence and frame numbers identify each "
            "window across both formats. Exit codes: 0 for disjoint sequences, "
            "1 for overlap, 2 for invalid input."
        ),
    )
    parser.add_argument("train", type=Path, help="training window list (UTF-8)")
    parser.add_argument("evaluation", type=Path, help="evaluation window list (UTF-8)")
    args = parser.parse_args()
    try:
        train = read_windows(args.train)
        evaluation = read_windows(args.evaluation)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    train_sequences = {sequence for sequence, _ in train}
    eval_sequences = {sequence for sequence, _ in evaluation}
    shared = sorted(train_sequences & eval_sequences)
    print(f"Training: {len(train)} windows in {len(train_sequences)} sequences")
    print(f"Evaluation: {len(evaluation)} windows in {len(eval_sequences)} sequences")
    print(f"Shared windows: {len(train & evaluation)}")
    print(f"Shared sequences: {len(shared)}")
    if shared:
        print("Overlapping sequences: " + ", ".join(f"Sequence{s}" for s in shared))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
