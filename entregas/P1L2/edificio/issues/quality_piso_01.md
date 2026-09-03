# PISO 1 - CONTROL DE EXTRACCION

Elementos inicialmente detectados: `490`
Recomendacion 3D: `AÚN NO LISTO`
Motivo: El calce sigue NEEDS_REVIEW y/o existen elementos POSIBLE/FRAGMENTADO/NEEDS_REVIEW/conflictos contra el modelo actual.

## Confirmados
- viga: `4`
- muro: `10`
- columna: `31`

## Posibles
- muro: `67`
- viga: `140`

## Posibles Falsos Positivos
- muro: `10`
- viga: `6`

## Duplicados

## Fragmentados
- muro: `9`
- viga: `53`

## Needs Review
- perimetro_losa: `70`
- viga: `2`
- vano: `20`
- eje_grafico: `68`

Duplicados detectados: `0`
Grupos logicos detectados: `{'viga': 24, 'muro': 4}`

## Coincidencia Con Modelo Actual
- correctos: `167`
- faltantes: `146`
- sobrantes: `13`
- dudosos: `3`
- faltantes_por_tipo: `{'muro': 46, 'viga': 92, 'columna': 8}`
- sobrantes_por_tipo: `{'viga': 1, 'muro': 1, 'columna': 11}`
- dudosos_por_tipo: `{'muro': 3}`
- no_comparados_con_modelo_3d: `{'perimetro_losa': 70, 'eje_grafico': 68}`

## Calce Parte 1 / Parte 2
Estado: `NEEDS_REVIEW`
Traslacion X: `27.491000000000003` m
Traslacion Y: `0.0` m
Rotacion: `0.0` grados
Escala: `1.0`
Evidencia columnas: `{'criterio': 'Control primario: columnas cercanas a la interfaz D/E. Control secundario: muros verticales adyacentes a la interfaz, que aportan puntos en filas Y distintas para evaluar no colinealidad.', 'columnas_por_zona': {'parte_1': 23, 'parte_2': 8}, 'columnas_interfaz_por_zona': {'parte_1': 3, 'parte_2': 1}, 'pares_columnas_interfaz_por_y': [{'parte_2': 'C_P2_01_0008', 'parte_1': 'C_P1_01_0005', 'piso': '1', 'delta_y_m': 0.118, 'delta_x_interfaz_m': 0.085, 'usable_para_calce': True}], 'pares_usables': 1, 'pares_muros_interfaz': [{'parte_2': 'MURO_P2_01_0001+MURO_P2_01_0003', 'parte_1': 'MURO_P1_01_0019+MURO_P1_01_0020', 'piso': '1', 'banda_y': 3, 'y_p2': [8.668, 16.618], 'y_p1': [9.25, 15.8], 'overlap_y_m': 6.55, 'delta_y_centrolinea_m': 0.118, 'delta_x_centrolinea_m': 0.591, 'x_centrolinea_p2': 27.832, 'x_centrolinea_p1': 27.241, 'segmentos_p2': 2, 'segmentos_p1': 2, 'nota': 'Residuo X entre nucleos en lados opuestos de la linea de columnas puede reflejar nucleos de planta distintos; la continuidad Y confirma el calce en esta banda.', 'usable_para_calce': True}], 'muros_verticales_interfaz_por_zona': {'parte_1': 14, 'parte_2': 21}, 'controles_no_colineales': {'estado': 'CON_CONTROLES_NO_COLINEALES', 'filas_y_distintas': [0.118, 14.0]}, 'conclusion': 'Controles no colineales en filas Y distintas: columnas en la interfaz confirman la alineacion X (residuo ~0.1 m) en la fila baja; los nucleos de muro adyacentes confirman la continuidad longitudinal Y (residuo de centrolinea ~0.118 m) en la banda media. Los residuos X entre nucleos opuestos de la linea de columnas reflejan nucleos de planta distintos, no un error de calce. CALCE_POSIBLE_NEEDS_REVIEW: requiere confirmacion final sobre planos generales.'}`
