# Validacion de ejes y CALCE_A

- Estado: **AXIS_CONFIRMED**
- Transformacion: dx=27.491000000000003 m, dy=0.0 m, rotation=0.0 deg, scale=1.0
- Residuo D/E: **0.009 m**
- Residuales Y comunes: `{'1': 0.0, '2': 0.0, '3': 0.0}`

## Evidencia

- Etiquetas/lineas: ED2 D=27.500 m; ED1 E+dx=27.491 m; ejes Y 1/2/3 coinciden en 0/8.90/16.15; rotacion=0; escala=1.
- Cotas EDIFICIO_1: [3.9, 8.9, 16.15, 50.0]
- Cotas EDIFICIO_2: [7.5, 8.9, 10.0, 16.15]
- Columnas cerca D (ED2): {'S1': 1, 'P1': 1, 'P2': 1, 'P3': 1, 'P4': 1}
- Columnas cerca E transformado (ED1): {'S1': 3, 'P1': 3, 'P2': 3, 'P3': 3, 'P4': 3}
- Vigas/muros cerca interfaz: {'EDIFICIO_2_D': {'S1': {'wall': 4}, 'P1': {'wall': 4}, 'P2': {'wall': 4}, 'P3': {'wall': 4}, 'P4': {'wall': 4}}, 'EDIFICIO_1_E_transformed': {'S1': {'beam': 4, 'wall': 14}, 'P1': {'beam': 5, 'wall': 2}, 'P2': {'beam': 6}, 'P3': {'beam': 6}, 'P4': {'beam': 6}}}
- Perimetros/axis segments cerca interfaz: {'EDIFICIO_2_D': {'S1': {'slab_edge': 9, 'axis': 11}, 'P1': {'slab_edge': 7, 'axis': 6}, 'P2': {'slab_edge': 7, 'axis': 6}, 'P3': {'slab_edge': 7, 'axis': 6}, 'P4': {'slab_edge': 3, 'axis': 7}}, 'EDIFICIO_1_E_transformed': {'S1': {'axis': 4}, 'P1': {'slab_edge': 3, 'axis': 2}, 'P2': {'slab_edge': 4, 'axis': 1}, 'P3': {'slab_edge': 4, 'axis': 1}, 'P4': {'slab_edge': 4, 'axis': 1}}}
- Fuentes/plano general: cad_sources.md identifica 2017_67 como planos estructurales actuales y 2024_22 como especialidades/calculo LT2 del mismo Edificio de Ingenieria; la secuencia de ejes A-D/E-J respalda continuidad de alas.

## Decision

Se conserva dx=27.491 m; no se normaliza a 27.500 m. El residuo de 9 mm queda documentado como tolerancia CAD/extraccion hasta evidencia de cota que exija correccion exacta.
