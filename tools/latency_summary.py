"""Summarize recorded latency samples in milliseconds."""

import argparse
import csv
import json
import math
from pathlib import Path


def read_durations(path, column):
    durations = []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        if not reader.fieldnames or reader.fieldnames.count(column) != 1:
            raise ValueError(f"expected exactly one header named {column!r}")
        for row in reader:
            if None in row:
                raise ValueError(f"line {reader.line_num}: extra CSV fields")
            try:
                duration = float(row[column])
            except (TypeError, ValueError):
                raise ValueError(f"line {reader.line_num}: missing or invalid {column!r}") from None
            if not math.isfinite(duration) or duration < 0:
                raise ValueError(f"line {reader.line_num}: expected a finite, nonnegative latency")
            durations.append(duration)
    if not durations:
        raise ValueError("no latency samples in the CSV")
    return sorted(durations)


def percentile(sorted_values, percent):
    """Interpolate linearly at zero-based rank (n - 1) * percent / 100."""
    index, remainder = divmod((len(sorted_values) - 1) * percent, 100)
    lower = sorted_values[index]
    if remainder == 0:
        return lower
    return lower + (sorted_values[index + 1] - lower) * (remainder / 100)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Median and p95 use linear interpolation at rank (n - 1) * p for p = 0.50 and 0.95.",
    )
    parser.add_argument("csv_file", type=Path, help="UTF-8 CSV with one sample per row")
    parser.add_argument("--column", default="latency_ms", help="duration column (default: latency_ms)")
    args = parser.parse_args()
    try:
        values = read_durations(args.csv_file, args.column)
    except (OSError, ValueError, csv.Error) as exc:
        parser.error(str(exc))
    print(json.dumps({
        "observations": len(values),
        "median_ms": percentile(values, 50),
        "p95_ms": percentile(values, 95),
    }))


if __name__ == "__main__":
    main()
