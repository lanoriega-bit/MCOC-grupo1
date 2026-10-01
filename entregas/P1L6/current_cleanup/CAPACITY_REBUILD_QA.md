# Capacidad y demanda CURRENT

Se corrigió la lectura de demanda: el export de Unity contiene solo G/Q/EX/EY, nunca una fila R precomputada. El contrato de capacidad ahora lee los cuatro resultados OpenSees recién verificados y forma primero las fuerzas de extremo **con signo** con la combinación inicial `R = 1,0 G + 0,5 Q + 0 EX + 0 EY`; después toma la envolvente absoluta entre segmentos y extremos. La configuración de coeficientes se comparte con el export de Unity. Los sliders pueden generar otras R en tiempo de ejecución; los D/C almacenados corresponden únicamente a la R inicial.

Cobertura: 639/639 miembros activos (442 vigas, 143 columnas, 54 muros) con capacidad aproximada y demanda no nula; cero vectores de demanda falsamente vacíos. Para columnas y muros se interpola la curva P–M académica en `|P|` y se verifica My y Mz por separado. Para vigas se calcula D/C de My, Mz, Vy y Vz; N y T quedan como demanda visible sin una capacidad normativa inventada.

Control manual: en `E1-P2-V-041`, la envolvente My de extremos para `G + 0,5Q` calculada directamente desde los JSON de OpenSees es **402,427201 kN·m**, igual al valor almacenado en `current_capacity.json`.

El screening académico señala cinco vigas con D/C >1 (`E1-P3-V-109`, `E2-P4-V-064`, `E2-P4-V-065`, `E2-P4-V-074`, `E2-P4-V-076`) y una columna fuera de la envolvente P–M (`E2-P4-C-007`). Son alertas de laboratorio, no dictámenes de diseño: `fc'`/`fy` se toman del catálogo donde su alcance lo respalda, mientras cuantías, recubrimiento, φ y la forma P–M son `ASSUMED_FOR_LAB`. Las 79 asignaciones ED1/P4 siguen bajo revisión de alcance.

La exportación final de resultados/contrato Unity terminó con `CURRENT_VERIFIED`; resta confirmar compilación y Play de la escena canónica. El contrato enlaza la geometría, FE, cargas y payload mediante hashes.
