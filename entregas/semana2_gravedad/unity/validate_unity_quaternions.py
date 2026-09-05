"""Static validation of m_LocalRotation quaternions in the E1 Unity scene.

Checks every serialized Transform's m_LocalRotation in E1GravityViewer.unity:
  - all components are finite numbers
  - the quaternion norm is ~1 (within tolerance)
  - no quaternion is (0,0,0,0)
Prints counts and any offending objects.
"""

from __future__ import annotations

import math
import sys
import re
from pathlib import Path

UNITY_ROOT = Path(__file__).resolve().parent
SCENE = UNITY_ROOT / "Assets" / "Scenes" / "E1GravityViewer.unity"
TOL = 1e-3  # allowed |norm - 1| (absolute)

ROT_RE = re.compile(
    r"m_LocalRotation:\s*\{\s*x:\s*([^\s,]+)"
    r"\s*,\s*y:\s*([^\s,]+)"
    r"\s*,\s*z:\s*([^\s,]+)"
    r"\s*,\s*w:\s*([^\s,]+)\s*\}"
)


def fail(message: str) -> None:
    print(f"quaternion_validation FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not SCENE.exists():
        fail(f"no existe escena {SCENE}")

    text = SCENE.read_text(encoding="utf-8")
    matches = list(ROT_RE.finditer(text))
    total = len(matches)
    invalid = []

    for m in matches:
        try:
            x, y, z, w = (float(g) for g in m.groups())
        except ValueError:
            invalid.append((m.group(0), "(no numérico / NaN / inf)"))
            continue
        if not all(math.isfinite(v) for v in (x, y, z, w)):
            invalid.append((m.group(0), "componentes no finitos"))
            continue
        norm = math.sqrt(x * x + y * y + z * z + w * w)
        if abs(norm - 1.0) > TOL:
            invalid.append((m.group(0), f"norma={norm:.9f} (fuera de tolerancia)"))
            continue
        if x == 0.0 and y == 0.0 and z == 0.0:
            invalid.append((m.group(0), "quaternion (0,0,0,0)"))

    if invalid:
        for rot, reason in invalid:
            print(f"  INVALID m_LocalRotation {rot}  -> {reason}")
        fail(f"{len(invalid)} rotacion(es) invalida(s) de {total} transform(s)")

    print(
        f"quaternion_validation OK: {total} transform(s) revisadas, "
        "todas las m_LocalRotation finitas, norma==1, ninguna (0,0,0,0)"
    )


if __name__ == "__main__":
    main()
