"""Renderiza modelspace de un DXF a PNG para revision visual reproducible."""

from __future__ import annotations

import argparse
from pathlib import Path

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument("--dark", action="store_true")
    args = parser.parse_args()

    doc = ezdxf.readfile(args.input)
    modelspace = doc.modelspace()
    background = "#101318" if args.dark else "white"

    fig = plt.figure(figsize=(20, 14), facecolor=background)
    ax = fig.add_axes((0.01, 0.01, 0.98, 0.98), facecolor=background)
    context = RenderContext(doc)
    context.set_current_layout(modelspace)
    backend = MatplotlibBackend(ax)
    Frontend(context, backend).draw_layout(modelspace, finalize=True)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_axis_off()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=args.dpi, facecolor=background, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print(args.output)


if __name__ == "__main__":
    main()
