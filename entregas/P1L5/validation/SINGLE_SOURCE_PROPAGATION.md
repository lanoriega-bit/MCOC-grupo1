# Prueba controlada de fuente única

Estado: **PASS_INPUT_PROPAGATION_ANALYSIS_BLOCKED**

Se ensayó en memoria `E2-P4-V-001` / `SEC_BEAM_RECT_0.200x0.900`: ancho 0.200 → 0.201 m.
El cambio llegó al derivado Unity y al input OpenSees; los cuatro JSON canónicos quedaron byte a byte intactos.
No se ejecutó OpenSees ni se afirmó un cambio de resultados porque los gates estructurales CURRENT siguen bloqueados.

| Etapa | Estado |
|---|---|
| `sections.json` → Unity | PASS |
| `sections.json` → input OpenSees | PASS |
| Restauración del valor original | PASS (nunca se escribió el ensayo) |
| OpenSees → resultado nuevo | BLOCKED_NOT_RUN |
