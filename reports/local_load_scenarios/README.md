# Cierre — escenarios locales desktop

Fecha: 2026-10-07. Rama: `codex/local-load-scenarios`.
**LOCAL LOAD SCENARIOS — READY**.

## Arquitectura y uso

Guía completa: [LOCAL_LOAD_SCENARIOS](../../docs/LOCAL_LOAD_SCENARIOS.md).
OpenSees analiza únicamente el incremento Q_LOCAL mediante el motor existente;
Unity clona R_BASE y suma vectores SI una vez. Reutiliza capacidades/evaluador
D/C. Los escenarios se escriben solo en `results/scenarios/`, ignorado por Git.
No añade masas, nodos, apoyos, secciones ni casos sísmicos.

Main → Play → CARGA LOCAL → Zona demo · ED1 P2 → ANALIZAR ESCENARIO.
Seleccionar E1-P2-V-048, abrir Resultados y desplazar la ficha hasta
BASE/ESCENARIO/Δ. RESTAURAR BASE vuelve sin solver; las salidas locales
no reemplazan ningún dataset. También se puede dibujar un rectángulo en TOP.

## Evidencia numérica

Zona ED1/P2 XY (45,4)–(52,9) m, 35 m², receptores físicos
E1-P2-V-045/048/058/060. R_BASE de QA = G+0,5Q.

| Personas ×68 kg | P adicional [kN] | Máximo desplazamiento Q_LOCAL [mm] |
|---|---:|---:|
| 0 | 0 | 0 |
| 1 | 0,66708 | 0,000827755 |
| 10 | 6,6708 | 0,00827755 |
| 20 | 13,3416 | 0,0165551 |

10 personas: qLocal=0,1905942857 kN/m², suma receptores=6670,8 N,
reacción vertical=6670,8 N, residual relativo=2,0654e-16.
Fuerzas, momentos y desplazamientos incrementales escalan linealmente;
comparación R_BASE+Q_LOCAL con corrida explícita equivalente PASS.
ED2, estructuralmente independiente, sin respuesta incremental significativa.

E1-P2-V-048: máximo |My de Q_LOCAL|=0,089026 kN·m;
máximo desplazamiento incremental de sus nodos=0,002555 mm;
D/C BASE=0,013778942 → SCENARIO=0,013778469.
Una combinación firmada puede reducir una demanda; no se fuerza su incremento.
Ningún miembro con D/C BASE<0,50 saltó a excedido con 10 personas.
E1-P3-V-109 ya estaba excedido en BASE (≈1,045); no es causado por esta carga.

Búsqueda incremental extrema solo QA: 10240 personas equivalentes,
6830,8992 kN /35 m²; E1-P2-V-058 D/C 0,414194→1,702513.
Colores renderizados naranja/rojo comprobados contra el evaluador existente.
Default sigue siendo 10 personas. No es un aforo admisible ni un ensayo post-falla.

## QA automático y manual

- Python: `python -B tests/loads/test_local_scenarios.py`, 5 tests PASS.
  Incluye entradas inválidas, unidades, conservación, equilibrio, 0/1/10/20,
  masa/superficie equivalentes, huecos, exterior, partición en 9 pisos,
  linealidad, corrida explícita y rechazo por identidad BASE distinta.
- Unity: última compilación y Main/Play; menú MCOC → Validar carga local en
  Main Play, 49 comprobaciones PASS en [UNITY_PLAY_QA.json](UNITY_PLAY_QA.json).
  Incluye selección, inspector, My/axial, deformada, sliders R, BASE G/Q/EX/EY/R,
  seis componentes 3D/2D, colores reales, restauración y contexto pasivo.
- Arrastre manual rápido sobre losa: 44,772775 m², 8 receptores, análisis real
  R_SCENARIO, reacción vertical=6670,8 N. Ficha de comparación visible y legible.
  Se corrigió la captura del arrastre usando eventos de inicio/fin, no polling.
- Arrastre manual parcialmente exterior: dibujada 36,019540 m² → efectiva
  16,813154 m², 3 receptores; el exterior queda excluido de la carga.
- Arrastre manual dentro del hueco visible del núcleo P2: rechazo explícito
  «La selección no intersecta una superficie estructural válida», sin solver.
- Un clic sin área se rechaza; Escape/restauración retiran la zona temporal.
- Diferencias pequeñas del inspector usan cifras significativas/notación científica;
  no se redondea a cero un incremento D/C pequeño pero no nulo.

Las capturas muestran el área, comparación/deformada y carga extrema de QA;
no representan una alteración de la estructura física.

- [Zona efectiva TOP](01_selection_top.png).
- [10 personas, My y resultados del escenario](02_ten_persons_comparison.png).
- [Carga extrema: estados de capacidad reales](04_high_load_capacity.png).
- [Hashes de protección BASE](BASE_PROTECTION.json).

## Protección y alcance

42 archivos de fuentes BASE, configuración, respuestas, capacidades y payloads
desktop fijados por bytes; digest agregado antes/después idéntico:
`7642c332fed41cc09439f47e94d7c2a4587264992179613a86ed90a4d10fd59a`.
Los tests también comparan sus hashes antes/después. AR y referencia original
Luis: cero cambios. Main sigue `c243a7bcccb21134e0bb7b1cdbd1203faacc2b9d`;
tags sin escritura. No se ejecutaron pruebas ni escenas AR.

Había 20 archivos CURRENT modificados y `entregas/P1L3/` sin seguimiento
antes de esta tarea. Se preservaron, no se resetearon ni se incluyeron en commits.
Por eso no se declara el árbol de trabajo global «limpio».

Esta regresión verifica las funciones citadas; no equivale a probar cada
combinación posible de filtros/UI. No se reejecutó la edición qQ base porque
reescribe CURRENT, expresamente protegido; su ruta existente se conserva y
restaura el escenario antes de una edición explícita del usuario.
Advertencias editor preexistentes permanecen, sin errores de compilación nuevos.

## Límites conocidos

Modelo lineal educativo, losas sin FE, tributarias originales de celdas 0,50 m,
carga nodal equivalente P/2 por viga física, una selección activa a la vez.
Diagramas conservan la representación CURRENT de fuerzas de extremos.
Python/OpenSees del repositorio necesarios; no solver incorporado en standalone.
Capacidades/D-C conservan hipótesis CURRENT; no certifican seguridad de uso.
Selección inválida, sin cobertura o BASE distinto: rechazo, nunca datos fabricados.

## Commits

- `6c5bd5d`: worker read-only, distribución tributaria y QA OpenSees.
- `d53d6cd`: selección/UI, superposición, comparación, D/C y QA Main/Play.
- Checkpoint final: documentación, evidencia y métricas QA; consultar `git log`
  de esta rama para el hash del commit que contiene este informe.
