# HIST-1 — Entregas y estado del proyecto

2026-09-22. Compilación Windows64 desde el Unity canónico: PASS.
Prueba en ejecución `StructuralReview.exe --ux-review`: PASS en 1366×768 y
1920×1080. No se ejecuta OpenSees.

- Se conserva la interfaz semántica y se agregan Entregas y Estado del proyecto.
- Cada entrega es retraíble; abrirla no carga otro modelo ni activa resultados.
- Conteos y commits históricos se extraen de snapshots Git, no se escriben a mano.
- P1L3/P1L4 requieren opt-in explícito y muestran incompatibilidad con CURRENT.
- La prueba fuerza capas históricas sin opt-in: ninguna puede renderizarse.
- Filtros, ejes, diagramas históricos My/N/P-M, modo presentación y fullscreen: PASS.
- Revisión visual de Entregas a 1366×768: texto legible con scroll; sin solape.
- Los 909 sólidos coinciden con la metadata; cuatro resúmenes disponibles.

Implementación: `ViewerDeliveries.cs`, `ViewerCurrentUI.cs`, `ViewerReviewQA.cs`.
Datos: `project_state.json`, generado con `scripts/build_project_state.py`.
Las capturas seleccionadas están en `qa/`; las pruebas completas se regeneran
en `Builds/CurrentReview/QA` (no versionado).

Esta prueba acredita interfaz/aislamiento, no validez resistente del candidato.

## EXT-7 / UX-5

Se recompila y repite QA después de agregar material de plano, fuente/alcance
en inspector y filtro PROPERTY_UPDATED. Se verifica E2-P1-C-001: fc=35 MPa,
CONFIRMED_FROM_PLAN. La metadata incorpora el nuevo QA histórico (6560 casos).
La nota de material no cambia la capacidad histórica ni habilita resultados.

Unity Editor reabierto en Assets/Main.unity / Play al cierre. Verificación
visual real: edificio actual visible, paneles retraíbles y pie CURRENT / FE
NOT RUN / resultados NONE. La habilidad computer-use se utilizó para comprobar
la ventana real, además del QA automatizado del ejecutable.
