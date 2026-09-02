"""Convert DWG files to DXF with AutoCAD Core Console.

Usage:
    python tools/convert_dwg_to_dxf.py input.dwg output.dxf
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ACCORECONSOLE = Path(r"C:\Program Files\Autodesk\AutoCAD 2026\accoreconsole.exe")


def build_script(output_path: Path) -> str:
    # DXFOUT is used instead of SAVEAS because it is stable for command-line export.
    return "\n".join(
        [
            "FILEDIA",
            "0",
            "CMDDIA",
            "0",
            "_.DXFOUT",
            str(output_path),
            "16",
            "_.QUIT",
            "Y",
            "",
        ]
    )


def convert(input_path: Path, output_path: Path) -> None:
    if not ACCORECONSOLE.exists():
        raise FileNotFoundError(f"AutoCAD Core Console not found: {ACCORECONSOLE}")
    if not input_path.exists():
        raise FileNotFoundError(f"DWG not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    script_path = output_path.with_suffix(".scr")
    script_path.write_text(build_script(output_path), encoding="ascii")

    completed = subprocess.run(
        [str(ACCORECONSOLE), "/i", str(input_path), "/s", str(script_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)
    if not output_path.exists():
        raise RuntimeError("AutoCAD finished without creating the DXF. Output was:\n" + completed.stdout + completed.stderr)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    convert(args.input.resolve(), args.output.resolve())
    print(f"DXF generated: {args.output}")


if __name__ == "__main__":
    main()
