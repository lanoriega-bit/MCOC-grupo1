# Lista exacta pendiente de autorización conjunta

Lista de 116 exclusiones propuesta antes de aplicar. **Actualización: aprobada expresamente por Matías y aplicada el 2026-09-23.** No son errores CAD: son cambios de alcance.
Las dos fusiones de vigas se tramitan aparte y no forman parte de estas 116.
Riesgo: retirar muros y columnas puede eliminar caminos de carga. El candidato se debe regenerar y NO se ejecutará OpenSees.

En las listas siguientes, cada sufijo se combina exclusivamente con el prefijo de su fila. No son rangos.

| Prefijo | Sufijos exactos |
|---|---|
| E1-P1-C- | 007, 009, 016, 017, 018, 019, 020 |
| E1-P1-V- | 068, 071, 072, 073, 082, 084, 089, 091, 093, 098 |
| E1-P2-V- | 053, 055, 069, 075, 082 |
| E1-P1-M- | 003, 004, 010, 027, 028, 029 |
| E1-S1-M- | 001, 007, 026, 027, 029, 051, 052, 053, 060 |
| E1-P2-M- | 002, 007, 008 |
| E1-P3-M- | 002, 007, 008 |
| E1-P4-M- | 002, 007, 008 |
| E2-S1-M- | 007, 008, 009, 010, 011 |
| E2-P1-M- | 007, 008, 009, 010, 011 |
| E2-P2-M- | 007, 008, 009, 010, 011 |
| E2-P3-M- | 007, 008, 009, 010, 011 |
| E2-P4-M- | 007, 008, 009, 010 |
| E1-S1-A- | 001, 010, 030, 057, 058, 059, 070 |
| E1-S1-V- | 001, 006, 007, 008, 010, 013, 014, 015, 016, 017, 027, 028, 029, 031, 032, 033, 037, 040, 041, 042, 046, 047, 048, 049, 050, 051, 056, 057, 058, 063, 064, 065, 066, 070, 071, 072, 073, 077, 079 |

S1 sur: 7 muros + 7 apoyos + 39 vigas = 53 elementos, delimitados entre M001 y M060, al sur del eje 1. Los otros 2 muros S1 de la tabla son las cadenas del núcleo, no parte del sector sur.

ED2 conserva todos los M001–M006 de cada piso: extremos occidentales asociados a M002/M003 y vecinos. Los muros orientales M007–M011 existen en CAD; la exclusión no implica que sean inexistentes ni que su ausencia sea resistente segura.

C007/C009 P1: las columnas P2 se conservan por aclaración expresa. Su transferencia pendiente debe quedar visible.
M028/M029 P1: paños interiores del eje I; se propone retirarlos por confirmación expresa, no clasificarlos falsamente como exteriores.

Planos y coordenadas: `confirmed_removal_chains.json`, `S1_EXTERIOR_REMOVAL_PROPOSAL.md`, `review_proposal.json`.
Overlays: `ED2_WALL_SCOPE.png`, `ED1_P1_SCOPE.png`, `S1_EXTERIOR.png`.
