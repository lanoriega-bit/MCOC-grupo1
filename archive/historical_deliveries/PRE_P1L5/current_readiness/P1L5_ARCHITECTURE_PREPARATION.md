# Preparación, no implementación de P1L5

## Superposición

`LinearBasisResponse.Combine` combina cuatro vectores firmados en el orden
G/Q/EX/EY con αG/αQ/αEX/αEY. Verifica tamaños y números finitos. No hay sliders
activos ni conexión con resultados históricos. Requiere idéntica rigidez K,
apoyos, geometría, orden de grados de libertad, ejes y patrones de referencia.
Primero combinar componentes/extremos; después calcular envolventes o máximos.
Nunca combinar valores absolutos ni máximos tomados de extremos distintos.

## Dos modificaciones recomendadas

1. Intensidad de carga de un patrón claramente delimitado. Escalar un patrón
   fijo en un sistema lineal permite reutilizar una base; cambiar distribución,
   receptores o masas exige regenerar los casos afectados. Para demostrar
   modificación + reanálisis, editar q de una zona y reconstruir su vector,
   conservando explícitamente la distinción respecto a cambiar αQ.
2. Sección de una viga/columna confirmada: recalcular A/I/J y rigidez; analizar
   nuevamente G/Q/EX/EY/R. Si cambia peso propio, actualizar G y masas; si afecta
   sección de capacidad, regenerar también P-M. No escalar esfuerzos antiguos.

Se prefieren a modificar apoyos o borrar miembros, que pueden crear mecanismos
y dificultar una demostración segura. Ninguna modificación se ha habilitado.

## Demanda-capacidad

El JSON de Luis `entregas/P1L4/demanda_capacidad/demanda_capacidad.json` contiene
dos elementos de estudio y demanda de CASE_R, no cuatro bases CURRENT. Las curvas
son separables de la demanda, con procedencia y puntos inválidos marcados: el muro
tiene 8 puntos válidos y 6 inválidos. No unir/extrapolar a través de intervalos
no validados. Mantener ASUMIDO_LAB y no convertir estas dos secciones en capacidad
certificada de todos los miembros del edificio.

Preparación necesaria: firma de geometría de sección/material/armadura,
identidad del eje de flexión y convención de P. Con bases compatibles, combinar
N/My/Mz firmados por extremo; convertir a la convención compresión-positiva de
capacidad; seleccionar el extremo gobernante después de combinar. Una curva
uniaxial no certifica interacción biaxial. Curva fija sólo si sección/material/
armadura y modelo constitutivo permanecen idénticos. Cambiar esos datos invalida
la curva y la demanda anterior; fuera del dominio, mostrar NO EVALUABLE.

## Masas / sismo actual: pendiente de generar

Masa por piso propuesta para el laboratorio: m=(W_G+η·W_Q)/g, η configurable
(0.5 como hipótesis del encargo), g=9.80665 m/s². W en N, m en kg. Separar PP de
miembros, PP_LOSA y PM_ADIC sin contarlos dos veces. La masa debe derivarse de
áreas netas y receptores actuales validados, no de la antigua Q uniforme.

Para EX/EY exportar centro de masa, aceleración/patrón, fuerza de piso, aplicación,
excentricidad y corte basal. El coeficiente 0.20 es parámetro del ejemplo de
laboratorio, no certificación normativa. No hay masas/sismo CURRENT calculados.
La ausencia de losas FE no justifica imponer un cuerpo rígido de seis DOF a todo
el piso: diafragma e idealización de muros requieren decisión física explícita.
