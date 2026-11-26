"""Overlay pixel agreement between a binary annotation and a predicted mask.

Green marks true positives, magenta marks false positives, and orange marks
false negatives. Each overlay uses 50% opacity. True negatives retain the
source gray level. The output keeps the original image dimensions.
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

if __package__:
    from .mask_overlap import read_mask
else:
    from mask_overlap import read_mask


def read_grayscale(path):
    with Image.open(path) as image:
        if getattr(image, "n_frames", 1) != 1:
            raise ValueError(f"Expected a single grayscale frame: {path}")
        if image.mode in ("L", "1"):
            return np.array(image.convert("L"))
        if image.mode.startswith("I;16") or (image.mode == "I" and image.format == "PNG"):
            # Map the full 16-bit range to 8-bit display intensities.
            return ((np.asarray(image, dtype=np.uint32) + 128) // 257).astype(np.uint8)
        raise ValueError(f"Expected an 8-bit or 16-bit grayscale image: {path}")


def overlay_masks(frame, annotation, prediction, output):
    if output.suffix.lower() != ".png":
        raise ValueError("The output path must end in .png")
    gray = read_grayscale(frame)
    reference = read_mask(annotation)
    predicted = read_mask(prediction)
    if gray.shape != reference.shape or gray.shape != predicted.shape:
        raise ValueError("The source frame and both masks must have identical dimensions")

    rgb = np.repeat(gray[:, :, None], 3, axis=2)
    for pixels, color in (
        (reference & predicted, (0, 255, 0)),
        (~reference & predicted, (255, 0, 255)),
        (reference & ~predicted, (255, 165, 0)),
    ):
        rgb[pixels] = (gray[pixels, None].astype(np.uint16) + np.array(color, dtype=np.uint16) + 1) // 2

    # Exclusive creation also protects an input file passed as the output.
    with output.open("xb") as stream:
        try:
            Image.fromarray(rgb).save(stream, format="PNG")
        except OSError:
            stream.close()
            output.unlink()
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frame", type=Path, help="Single grayscale source image")
    parser.add_argument("annotation", type=Path, help="Binary annotation PNG (0/1 or 0/255)")
    parser.add_argument("prediction", type=Path, help="Binary prediction PNG (0/1 or 0/255)")
    parser.add_argument("output", type=Path, help="New RGB overlay PNG to create")
    args = parser.parse_args()
    try:
        overlay_masks(args.frame, args.annotation, args.prediction, args.output)
    except (OSError, ValueError) as error:
        parser.exit(2, f"{parser.prog}: {error}\n")


if __name__ == "__main__":
    main()
