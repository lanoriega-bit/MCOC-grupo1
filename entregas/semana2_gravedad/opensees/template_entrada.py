"""Template de entrada para el modelo estructural (DATOS DEMO).

ESTE ARCHIVO CONTIENE DATOS FICTICIOS PARA MOSTRAR EL FORMATO DE
ENTRADA. NO SON DATOS DEL EDIFICIO REAL.

El modelo estructural de mi companero debe construir un
StructuralModelInput con este formato cuando este listo.

Los datos DEMO usan un rectangulo ficticio de 6m x 4m correspondiente
a un "paho de ejemplo" sin relacion con los planos reales.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from integracion import StructuralModelInput, StructuralSlab, StructuralBeam, StructuralWall


def construir_modelo_demo() -> StructuralModelInput:
    """Construye un StructuralModelInput con datos DEMO ficticios.

    Retorna:
        StructuralModelInput DEMO. NO usar para el edificio real.
    """
    # ------------------------------------------------------------------
    # NODOS: dict[int, (x, y, z)]  -- coordenadas en metros
    # ------------------------------------------------------------------
    nodes = {
        # Piso 3 (planta ficticia)
        1001: (0.0, 0.0, 9.0),   # A (esquina inferior-izquierda)
        1002: (6.0, 0.0, 9.0),   # B
        1003: (6.0, 4.0, 9.0),   # C
        1004: (0.0, 4.0, 9.0),   # D
        # Piso 2 (soporte inferior)
        2001: (0.0, 0.0, 6.0),
        2002: (6.0, 0.0, 6.0),
        2003: (6.0, 4.0, 6.0),
        2004: (0.0, 4.0, 6.0),
    }

    # ------------------------------------------------------------------
    # LOSAS: poligono XY + espesor + terminaciones
    # ------------------------------------------------------------------
    slabs = [
        StructuralSlab(
            building_id="DEMO",
            floor_id=3,
            slab_id="DEMO_L3_01",
            vertices=[
                (0.0, 0.0),
                (6.0, 0.0),
                (6.0, 4.0),
                (0.0, 4.0),
            ],
            thickness_m=0.20,
            finishes_kN_m2=1.5,
        ),
    ]

    # ------------------------------------------------------------------
    # VIGAS: tags de nodos + losas que descargan + (opcional) tributarias
    # ------------------------------------------------------------------
    beams = [
        StructuralBeam(
            building_id="DEMO",
            beam_id="DEMO_L3_B01",
            node_i_tag=1001,
            node_j_tag=1002,
            slab_ids=["DEMO_L3_01"],       # losa del piso que descarga
        ),
        StructuralBeam(
            building_id="DEMO",
            beam_id="DEMO_L3_B02",
            node_i_tag=1002,
            node_j_tag=1003,
            slab_ids=["DEMO_L3_01"],
        ),
        StructuralBeam(
            building_id="DEMO",
            beam_id="DEMO_L3_B03",
            node_i_tag=1003,
            node_j_tag=1004,
            slab_ids=["DEMO_L3_01"],
        ),
        StructuralBeam(
            building_id="DEMO",
            beam_id="DEMO_L3_B04",
            node_i_tag=1004,
            node_j_tag=1001,
            slab_ids=["DEMO_L3_01"],
        ),
    ]

    # ------------------------------------------------------------------
    # MUROS: (opcional)
    # ------------------------------------------------------------------
    walls = [
        StructuralWall(
            building_id="DEMO",
            wall_id="DEMO_L3_M01",
            node_i_tag=2001,
            node_j_tag=2002,
            axial_load_N=0.0,
        ),
    ]

    return StructuralModelInput(
        building_id="DEMO",
        nodes=nodes,
        slabs=slabs,
        beams=beams,
        walls=walls,
    )


if __name__ == "__main__":
    model = construir_modelo_demo()
    print("Modelo DEMO construido:")
    print(f"  building_id = {model.building_id}")
    print(f"  nodos       = {len(model.nodes)}")
    print(f"  losas       = {len(model.slabs)}")
    print(f"  vigas       = {len(model.beams)}")
    print(f"  muros       = {len(model.walls)}")
    print("\nADVERTENCIA: estos son datos DEMO ficticios, no del edificio real.")
