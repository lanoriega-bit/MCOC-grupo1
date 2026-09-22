# Qué aprendimos de Cáceres

P1L4: [b4a7bd8](https://github.com/jpCaceres123/Proyecto-1-MCOC/tree/b4a7bd8).
Nuevo contraste: [93fba4a](https://github.com/jpCaceres123/Proyecto-1-MCOC/tree/93fba4a524193404d63a21e7696db135097d9678).
Clones separados, solo lectura, push deshabilitado. No ejecutar código externo.

## Inventario técnico

- P1L2: `Edificio/documentation/README_P1L2.md`, `CARGAS_LOSAS.md`,
  `model/builders/generar_modelo_manual.py`, `data/loads/`, modelo JSON manual.
  Geometría por ejes, división de muros por nivel, paños/huecos y cargas.
- P1L3: `README_P1L3.md`, resultados/casos OpenSees, masas/sismo,
  compatibilidad de deformaciones, refuerzo y capacidad de muros por piso.
- P1L4: `POSTPROCESO_SEMANA4.md`, Unity, ejes locales y seis DOF,
  diagramas, deformada Hermite y `verification/tests/test_postproceso.py`.
- Reciente: f3afa7a/93fba4a amplían SQ4/carga móvil a 652 losas. NO es una
  función PRE-P1L5 solicitada. `modelo_3d_manual.json` y `data` sin diferencias
  b4a7bd8→93fba4a; sus fuentes no resuelven por sí solas nuevos perímetros.

## Ideas útiles y adopción

| Hallazgo | Fuente | Clasificación | Decisión |
|---|---|---|---|
| Equilibrio local por barra y caso | verification/tests/test_postproceso.py | USEFUL_AND_CORRECT para carga nodal | ADOPTADO en script propio, 6560 PASS |
| Triadas ortonormales, mano derecha, x=i→j | mismo test | USEFUL_AND_CORRECT | ADOPTADO, 1312 PASS |
| Área bruta − huecos = área neta | CARGAS_LOSAS / convertir_cargas_losas | USEFUL_NEEDS_ADAPTATION | Mantener como requisito de futuro cierre de losas; no inferir huecos |
| ID padre del muro y segmentos por piso | generar_modelo_manual | USEFUL_NEEDS_ADAPTATION | Nuestro crosswalk ya conserva origen; no copiar fragmentación |
| Convención de corte normal +x | POSTPROCESO_SEMANA4 | USEFUL_AND_CORRECT | Documentar equilibrio y diferencias end action/cut force |
| Hermite usando rotaciones | postproceso | USEFUL_NEEDS_ADAPTATION | No adoptado aún; exige contrato seis DOF compatible |
| Refuerzo por eje/piso | data/reinforcement | USEFUL_NEEDS_ADAPTATION | Pistas hacia planos, no valores universales |
| Carga móvil verificada | commits recientes | NOT_RELEVANT | No empezar P1L5 |

## Propiedades y limitaciones

- El ejemplo 70×70 / 16Ø22, fc35/fy420 no se copia. Su pista condujo a releer
  notas primarias 100: G35_10 y A630-420H sí existen, con distinto alcance ED1/ED2.
- `generar_modelo_manual.py` da a vigas VAR propiedades equivalentes
  A=.21, Iy=.005, Iz=.0015, J=.0004. No son una altura de plano recuperada.
- La tabla de refuerzo contiene entradas del eje 1'' E/Ec con separación H/V
  intercambiada entre registros. Necesita resolver ámbito/revisión original.
- ShellMITC4, malla y vínculos frame-shell no son equivalentes a nuestros
  muros de barra; no importar demanda/capacidad sin un modelo común.
- Penalización elevada y vínculos geométricos exigen estudiar condicionamiento
  y cinemática: que exporte resultados no valida esas conexiones en nuestro FE.
- 652 paños no prueban un perímetro real: regiones manuales, recortes y vacíos
  deben comprobarse contra plantas/cortes. Lo mismo vale para LT2B.
- README P1L2 contiene rutas/conteos de etapas anteriores. El manifiesto y
  commit de un archivo son más fiables para seleccionar el snapshot actual.

## Alcance

Se reimplementó el principio de QA, no se importó su código. La nueva prueba
propia no ejecuta OpenSees, no toca resultados y guarda hashes de los cinco
archivos leídos. Cero cambios/push/PR/issues en repos externos.
