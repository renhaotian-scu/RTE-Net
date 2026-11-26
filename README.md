# RTE-Net

Reference-Guided Temporal Evidence Network for Multi-Frame Infrared Small-Target Detection.

This repository contains an inspectable architecture outline and four standalone tools for working with evaluation data. The model implementation and trained weights are private.

## Architecture

[architecture.py](architecture.py) describes the inputs and outputs of the primary and companion networks. Both branches use the same five frames to predict the foreground on the last frame. To print the outline, run `python architecture.py`.

## Tools

Use Python 3.9 or later. For the two mask tools, install the dependencies with `python -m pip install -r requirements.txt`.

| Tool | Example | Output |
| --- | --- | --- |
| [Check a data split](tools/check_split.py) | `python tools/check_split.py train.txt test.txt` | Counts shared sequences and windows in NUDT-MIRSDT lists and flags duplicate entries. |
| [Measure mask overlap](tools/mask_overlap.py) | `python tools/mask_overlap.py annotations/ predictions/` | Reports pooled pixel IoU, mean per-image IoU, and the number of empty mask pairs. |
| [View mask differences](tools/view_masks.py) | `python tools/view_masks.py frame.png annotation.png prediction.png comparison.png` | Saves an overlay of correctly predicted, extra, and missed foreground pixels. |
| [Summarize latency](tools/latency_summary.py) | `python tools/latency_summary.py timings.csv` | Reports the median and 95th percentile of the recorded durations in milliseconds. |

Split lists contain one window per line, for example `Sequence12/Mix/00042.mat` or `Sequence12_00042.png`. The split check detects shared sequences even when frame numbers differ.

For overlap evaluation, store each annotation and prediction at the same relative path under their respective directories. Use single-channel PNGs with labels in {0, 1} or {0, 255} at the same resolution. IoU values are reported as fractions. A pair with empty union contributes zero to the per-image mean.

The latency tool reads the `latency_ms` column by default. Pass `--column` to select another column of millisecond measurements.
