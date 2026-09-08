"""Rutas y constantes del entregable P1L3 Parte A.

Convencion SI: m, N, Pa.
"""

from __future__ import annotations

from pathlib import Path

P1L3_ROOT = Path(__file__).resolve().parents[1]  # entregas/P1L3
REPO_ROOT = P1L3_ROOT.parents[1]

COMBINED_VIEWER_JSON = REPO_ROOT / "entregas" / "P1L2" / "unity_export" / "model_combined_viewer.json"
RESULTS_DIR = P1L3_ROOT / "results"
GRAVEDAD_DIR = P1L3_ROOT / "gravedad"

# Niveles estructurales: z (m) de la cara superior de losa por piso.
# Derivados del modelo (columnas S1 de 0.0 a 3.96, etc.) y consistentes con
# enrich_response.py de semana2_gravedad.
LEVELS_Z_M = {"base": 0.0, "S1": 3.96, "P1": 7.92, "P2": 11.88, "P3": 15.84, "P4": 19.80}
FLOOR_INDEX = {"S1": 1, "P1": 2, "P2": 3, "P3": 4, "P4": 5}
FLOOR_LABEL = {v: k for k, v in FLOOR_INDEX.items()}
FLOORS = ["S1", "P1", "P2", "P3", "P4"]

BUILDING_SHORT = {"EDIFICIO_1": "E1", "EDIFICIO_2": "E2"}