"""Configuracion de cargas de P1L3 Parte A.

q_G = PP.LOSA (espesor x densidad x g) + PM.ADIC (terminaciones).
q_Q = sobrecarga de uso (SC). El default uniforme de 250 kgf/m2 se conserva
sin cambios exclusivamente como LEGACY_UNIFORM_Q_VALIDATION para demostrar la
conservacion del motor tributario. No representa la zonificacion real de las
laminas 700 y no debe promoverse a carga de proyecto sin el mapeo aprobado.

Unidades SI (m, N, Pa).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from p1l3.rutas import FLOORS
from carga_gravedad import GRAVITY, CONCRETE_DENSITY


@dataclass
class CargasConfig:
    q_Q_case_status: str = "LEGACY_UNIFORM_Q_VALIDATION"
    q_Q_N_m2: dict = field(default_factory=dict)        # por piso -> SC
    thickness_m: dict = field(default_factory=dict)      # por piso -> espesor losa
    finishes_kN_m2: dict = field(default_factory=dict)   # por piso -> PM.ADIC
    q_Q_default_N_m2: float = 250.0 * GRAVITY
    thickness_default_m: float = 0.15
    finishes_default_kN_m2: float = 260.0 * GRAVITY / 1000.0  # 260 kgf/m2, lamina 700
    concrete_density_kg_m3: float = CONCRETE_DENSITY

    def __post_init__(self):
        for fl in FLOORS:
            self.q_Q_N_m2.setdefault(fl, self.q_Q_default_N_m2)
            self.thickness_m.setdefault(fl, self.thickness_default_m)
            self.finishes_kN_m2.setdefault(fl, self.finishes_default_kN_m2)

    def qG_kN_m2(self, floor: str) -> float:
        """qG en kN/m2 para un piso con los valores configurados."""
        t = self.thickness_m[floor]
        pp = t * self.concrete_density_kg_m3 * GRAVITY / 1000.0  # kN/m2
        return pp + self.finishes_kN_m2[floor]

    def qQ_N_m2(self, floor: str) -> float:
        return float(self.q_Q_N_m2[floor])


def config_por_defecto() -> CargasConfig:
    return CargasConfig()
