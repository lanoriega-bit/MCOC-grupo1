# CONTROL GLOBAL DEL EDIFICIO

Recomendacion: `AÚN NO LISTO PARA MODELADO 3D`

## Planos
- total_analizados: `12`
- utilizados_como_planta: `7`
- problematicos: `1`

## Sistema Global
- origen: `Eje A-1 de Parte 2 / LT2 = (0, 0, 0)`
- unidades: `m`
- transformacion_parte_1_parte_2: `NEEDS_REVIEW`
- laminas_calibradas_por_columnas: `4`
- error_maximo_calibracion_laminas_m: `0.127`
- evidencia_calce: `{'criterio': 'Control primario: columnas cercanas a la interfaz D/E. Control secundario: muros verticales adyacentes a la interfaz, que aportan puntos en filas Y distintas para evaluar no colinealidad.', 'columnas_por_zona': {'parte_1': 49, 'parte_2': 23}, 'columnas_interfaz_por_zona': {'parte_1': 6, 'parte_2': 3}, 'pares_columnas_interfaz_por_y': [{'parte_2': 'C_P2_01_0008', 'parte_1': 'C_P1_01_0005', 'piso': '1', 'delta_y_m': 0.118, 'delta_x_interfaz_m': 0.085, 'usable_para_calce': True}, {'parte_2': 'C_P2_02_0008', 'parte_1': 'C_P1_02_0001', 'piso': '2', 'delta_y_m': 0.118, 'delta_x_interfaz_m': 0.108, 'usable_para_calce': True}], 'pares_usables': 2, 'pares_muros_interfaz': [{'parte_2': 'MURO_P2_01_0001+MURO_P2_01_0003', 'parte_1': 'MURO_P1_01_0019+MURO_P1_01_0020', 'piso': '1', 'banda_y': 3, 'y_p2': [8.668, 16.618], 'y_p1': [9.25, 15.8], 'overlap_y_m': 6.55, 'delta_y_centrolinea_m': 0.118, 'delta_x_centrolinea_m': 0.591, 'x_centrolinea_p2': 27.832, 'x_centrolinea_p1': 27.241, 'segmentos_p2': 2, 'segmentos_p1': 2, 'nota': 'Residuo X entre nucleos en lados opuestos de la linea de columnas puede reflejar nucleos de planta distintos; la continuidad Y confirma el calce en esta banda.', 'usable_para_calce': True}, {'parte_2': 'MURO_P2_02_0001+MURO_P2_02_0003', 'parte_1': 'MURO_P1_02_0006+MURO_P1_02_0008', 'piso': '2', 'banda_y': 3, 'y_p2': [8.668, 16.618], 'y_p1': [12.266, 13.945], 'overlap_y_m': 1.679, 'delta_y_centrolinea_m': 0.463, 'delta_x_centrolinea_m': 3.608, 'x_centrolinea_p2': 27.828, 'x_centrolinea_p1': 24.221, 'segmentos_p2': 2, 'segmentos_p1': 2, 'nota': 'Residuo X entre nucleos en lados opuestos de la linea de columnas puede reflejar nucleos de planta distintos; la continuidad Y confirma el calce en esta banda.', 'usable_para_calce': False}, {'parte_2': 'MURO_P2_02_0001+MURO_P2_02_0003', 'parte_1': 'MURO_P1_02_0006+MURO_P1_02_0008', 'piso': '2', 'banda_y': 3, 'y_p2': [8.668, 16.618], 'y_p1': [12.266, 13.945], 'overlap_y_m': 1.679, 'delta_y_centrolinea_m': 0.463, 'delta_x_centrolinea_m': 3.608, 'x_centrolinea_p2': 27.828, 'x_centrolinea_p1': 24.221, 'segmentos_p2': 2, 'segmentos_p1': 2, 'nota': 'Residuo X entre nucleos en lados opuestos de la linea de columnas puede reflejar nucleos de planta distintos; la continuidad Y confirma el calce en esta banda.', 'usable_para_calce': False}, {'parte_2': 'MURO_P2_FUNDACION_0001+MURO_P2_FUNDACION_0003', 'parte_1': 'MURO_P1_02_0006+MURO_P1_02_0008', 'piso': 'fundacion', 'banda_y': 3, 'y_p2': [8.668, 16.618], 'y_p1': [12.266, 13.945], 'overlap_y_m': 1.679, 'delta_y_centrolinea_m': 0.463, 'delta_x_centrolinea_m': 3.611, 'x_centrolinea_p2': 27.832, 'x_centrolinea_p1': 24.221, 'segmentos_p2': 2, 'segmentos_p1': 2, 'nota': 'Residuo X entre nucleos en lados opuestos de la linea de columnas puede reflejar nucleos de planta distintos; la continuidad Y confirma el calce en esta banda.', 'usable_para_calce': False}], 'muros_verticales_interfaz_por_zona': {'parte_1': 33, 'parte_2': 57}, 'controles_no_colineales': {'estado': 'CON_CONTROLES_NO_COLINEALES', 'filas_y_distintas': [0.118, 14.0]}, 'conclusion': 'Controles no colineales en filas Y distintas: columnas en la interfaz confirman la alineacion X (residuo ~0.1 m) en la fila baja; los nucleos de muro adyacentes confirman la continuidad longitudinal Y (residuo de centrolinea ~0.118 m) en la banda media. Los residuos X entre nucleos opuestos de la linea de columnas reflejan nucleos de planta distintos, no un error de calce. CALCE_POSIBLE_NEEDS_REVIEW: requiere confirmacion final sobre planos generales.'}`

## Pisos
- fundacion: segmentos CAD vigas `112`, muros `75`, columnas `9`; entidades logicas vigas `40`, muros `52`, columnas `9`, losas/perimetros `11`, categorias `{'CONFIRMADA': 44, 'POSIBLE': 57}`
- piso_01: segmentos CAD vigas `205`, muros `96`, columnas `31`; entidades logicas vigas `170`, muros `58`, columnas `31`, losas/perimetros `70`, categorias `{'CONFIRMADA': 162, 'CONFIRMADO': 37, 'POSIBLE': 60}`
- piso_02: segmentos CAD vigas `278`, muros `45`, columnas `23`; entidades logicas vigas `172`, muros `31`, columnas `23`, losas/perimetros `71`, categorias `{'CONFIRMADA': 149, 'CONFIRMADO': 20, 'POSIBLE': 57}`
- piso_03: segmentos CAD vigas `52`, muros `3`, columnas `9`; entidades logicas vigas `42`, muros `3`, columnas `9`, losas/perimetros `9`, categorias `{'CONFIRMADA': 37, 'CONFIRMADO': 1, 'POSIBLE': 16}`

## Vigas
- segmentos_cad_originales: `647`
- vigas_logicas_activas: `424`
- falsos_positivos_segmentos: `19`
- grupos_fragmentacion_detectados: `107`

## Muros
- segmentos_cad_originales: `219`
- muros_logicos_activos: `144`
- falsos_positivos_segmentos: `20`

## Columnas
- columnas_logicas: `72`
- grupos_verticales: `39`
- grupos_con_continuidad: `21`

## Relaciones Verticales
- grupos_columnas: `39`
- grupos_muros_multinivel: `26`

## Conflictos
- CRITICAL: `0`
- HIGH: `0`
- MEDIUM: `7`
- LOW: `4`

## Calidad General
- confirmada: `70.3%`
- probable: `29.7%`
- pendiente_revision_principal: `0.0%`

## Recomendacion Final
`AÚN NO LISTO PARA MODELADO 3D`
