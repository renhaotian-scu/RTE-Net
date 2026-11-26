"""High-level data flow of RTE-Net, from input frames to a reference-frame mask."""

from typing import NamedTuple


class Stage(NamedTuple):
    name: str
    inputs: tuple[str, ...]
    description: str


RTE_NET = (
    Stage("frames", (), "Five chronological observations ending with the reference frame"),
    Stage("primary", ("frames",), "Primary prediction branch"),
    Stage("companion", ("frames",), "Independently trained reference-conditioned companion"),
    Stage("prediction", ("primary", "companion"), "Foreground mask on the reference frame"),
)


if __name__ == "__main__":
    for stage in RTE_NET:
        inputs = ", ".join(stage.inputs) or "input"
        print(f"{stage.name} ({inputs}): {stage.description}")
