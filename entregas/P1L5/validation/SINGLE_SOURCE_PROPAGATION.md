# Prueba controlada de fuente única

Estado: **PASS**

Se ensayó en memoria `E2-P4-V-001` / `SEC_BEAM_RECT_0.200x0.900`: ancho 0.200 → 0.201 m.
El cambio llegó al derivado Unity y al input OpenSees; los cuatro JSON canónicos quedaron byte a byte intactos.
La corrida CURRENT separada confirma que el adaptador OpenSees produce resultados G/Q/EX/EY; el ensayo en memoria no reescribe la fuente.

| Etapa | Estado |
|---|---|
| `sections.json` → Unity | PASS |
| `sections.json` → input OpenSees | PASS |
| Restauración del valor original | PASS (nunca se escribió el ensayo) |
| OpenSees → resultado CURRENT | PASS |
