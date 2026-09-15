# P1L4 — Estado final

`P1L4 STATUS: COMPLETE`

- Rama evaluable: `codex/p1l4-unity-integration`.
- Tag evaluable: `P1L4_FINAL_AUDITED`.
- Proyecto Unity canónico: `entregas/P1L3/José/viewer_unity`.
- Escena: `Assets/Main.unity`.
- Unity verificado: `6000.6.0f1`.

## Integración de los tres integrantes

- Matías: visor canónico, contrato, inspector, casos, deformada, diagramas
  3D/2D, cargas, apoyos, tributarias, contexto físico, QA y UX de defensa.
- José: export reproducible JSON/CSV de cinco casos, 813 nodos, 1312 miembros,
  106 apoyos, cargas y tributarias; integrado como fuente directa del visor.
- Luis: P-M de columna y muro, punto de demanda, DENTRO/FUERA, trazabilidad y
  nota obligatoria `ASUMIDO_LAB` para armadura del muro.

## Estado funcional

El visor permite seleccionar elementos; consultar identidad, nodos, sección,
material, ejes, restricciones y resultados; cambiar G/Q/EX/EY/R; mostrar
deformada; diagramas 3D y gráficos 2D My/Mz/N/Vy/Vz; ver cargas, apoyos y
tributarias; y revisar P-M/demanda de columna y muro.

Los gráficos derivados solo de fuerzas de extremo se identifican como
`END_FORCES_INTERPOLATION`. El extremo `j` se cambia de signo para expresar
ambos extremos en una convención común de cara interna. El pipeline auditado
usa cargas nodales y no contiene cargas interiores de elemento; por equilibrio,
N/V/T son constantes y My/Mz lineales. Los 33 crosswalk 1:N pertenecen al FE
candidato no ejecutado y se muestran solo como trazabilidad; no reciben ni
combinan resultados históricos. Un cero explícito se dibuja como cero; una
ausencia se muestra como `N/A`.

## QA final

- Export José reproducido: PASS.
- Validador de contratos: PASS_WITH_NOTES.
- Auditoría física de 1312 miembros × 5 casos: PASS; residual máximo
  `1.862645149e-09` en unidades SI.
- Compilación Unity: PASS.
- Play: PASS.
- Secuencia de demostración viga/columna/muro/global: PASS.
- Archivo original de Luis `entregas/P1L2/unity_export/model_viewer.json`: intacto.
- DWG/DXF originales, temporales y backups: no incluidos en el cierre.

## Limitaciones declaradas

- G/Q/EX/EY/R son resultados verificados de P1L3 exportados para P1L4; no se
  presentan como una corrida posterior sobre la geometría consolidada.
- Las cargas 700 están auditadas y visibles, pero siguen `NOT_APPLIED`; no se
  mezclan con los resultados históricos.
- 192 tributarias sin polígono y cargas puntuales sin posición inequívoca se
  informan sin inventar geometría.
- La armadura del muro de estudio es `ASUMIDO_LAB` y se muestra siempre.

Estas limitaciones no bloquean los requisitos funcionales de visualización P1L4.

## Cómo abrir y demostrar

1. Abrir la carpeta `entregas/P1L3/José/viewer_unity` con Unity 6000.6.0f1.
2. Abrir `Assets/Main.unity` y presionar Play.
3. Seguir `DEMO EN VIVO` en `entregas/P1L4/README.md`.
4. Para repetir el QA automático usar `MCOC > Probar interfaz en Play`.

## Qué debe saber el grupo

- Por qué Unity no recalcula: OpenSees es dueño del análisis y JSON es el contrato.
- Cómo leer signos, unidades, extremos i/j y ejes locales.
- Por qué no se suman miembros de un crosswalk 1:N.
- Por qué la recta del diagrama es una interpolación visual.
- Diferencia entre demanda y capacidad y efecto de P sobre M resistente.
- Qué datos son confirmados, derivados, históricos o `ASUMIDO_LAB`.
