"""Compare two directories of binary PNG masks with matching relative paths.

Pixel IoU pools intersections and unions across all images. Mean image IoU
weights each image equally. Both values are fractions in [0, 1]; a zero
union scores 0, including when every mask in both directories is empty.
"""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def png_files(root):
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() == ".png"
    }


def read_mask(path):
    with Image.open(path) as image:
        if image.format != "PNG" or getattr(image, "n_frames", 1) != 1:
            raise ValueError(f"Expected a single-frame PNG: {path}")
        pixels = np.asarray(image)
        if pixels.ndim != 2:
            raise ValueError(f"Expected a single-channel mask: {path}")
        # For indexed PNGs, the palette indices themselves are the labels.
        binary = (pixels == 0) | (pixels == 1)
        if not binary.all() and not ((pixels == 0) | (pixels == 255)).all():
            raise ValueError(f"Expected labels drawn from {{0, 1}} or {{0, 255}}: {path}")
        return pixels != 0


def compare_masks(reference_dir, prediction_dir):
    references = png_files(Path(reference_dir))
    predictions = png_files(Path(prediction_dir))
    if references.keys() != predictions.keys():
        missing = sorted(references.keys() - predictions.keys())
        extra = sorted(predictions.keys() - references.keys())
        raise ValueError(
            f"PNG paths differ. Missing predictions ({len(missing)}): {missing[:5]}. "
            f"Extra predictions ({len(extra)}): {extra[:5]}."
        )
    if not references:
        raise ValueError("The directories contain no PNG masks.")

    intersection = 0
    union = 0
    image_iou_sum = 0.0
    empty_pairs = 0
    for name in sorted(references):
        ref = read_mask(references[name])
        pred = read_mask(predictions[name])
        if ref.shape != pred.shape:
            raise ValueError(f"Shape mismatch for {name}: {ref.shape} versus {pred.shape}")
        common = int(np.count_nonzero(ref & pred))
        combined = int(np.count_nonzero(ref | pred))
        intersection += common
        union += combined
        if combined:
            image_iou_sum += common / combined
        else:
            empty_pairs += 1

    return {
        "image_count": len(references),
        "empty_union_count": empty_pairs,
        "intersection_pixels": intersection,
        "union_pixels": union,
        "pixel_iou": intersection / union if union else 0.0,
        "mean_image_iou": image_iou_sum / len(references),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference_dir", type=Path, help="Root directory of reference masks")
    parser.add_argument("prediction_dir", type=Path, help="Root directory of predicted masks")
    args = parser.parse_args()
    try:
        result = compare_masks(args.reference_dir, args.prediction_dir)
    except (OSError, ValueError) as error:
        parser.exit(2, f"{parser.prog}: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
