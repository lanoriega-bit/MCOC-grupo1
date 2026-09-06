# GOLDEN/Luis EDIFICIO_1 vs modelo combinado

- Estado: **SUPERSEDED_BY_LUIS_REFERENCE_DIFF**
- Estado comparacion geometrica legacy: **FAIL**
- Transformacion removida: dx=27.491000000000003 m, dy=0.0 m
- Solids: FAIL missing=22 extra=0
- Segments: PASS missing=0 extra=0
- Criterio obligatorio: **False**

## Conteos GOLDEN

- P1:beam: 108
- P1:column: 34
- P1:slab: 1
- P1:wall: 38
- P2:beam: 112
- P2:column: 29
- P2:slab: 1
- P2:wall: 12
- P3:beam: 124
- P3:column: 26
- P3:slab: 1
- P3:wall: 12
- P4:beam: 122
- P4:column: 26
- P4:slab: 1
- P4:wall: 12
- S1:beam: 79
- S1:column: 34
- S1:slab: 1
- S1:support: 94
- S1:wall: 60

## Conteos EDIFICIO_1 en combinado

- P1:beam: 108
- P1:column: 32
- P1:slab: 1
- P1:wall: 38
- P2:beam: 112
- P2:column: 29
- P2:slab: 1
- P2:wall: 12
- P3:beam: 124
- P3:column: 24
- P3:slab: 1
- P3:wall: 12
- P4:beam: 122
- P4:column: 26
- P4:slab: 1
- P4:wall: 12
- S1:beam: 79
- S1:column: 25
- S1:slab: 1
- S1:support: 85
- S1:wall: 60

La comparacion normaliza pisos legacy 1S/1/2/3/4/base a S1/P1/P2/P3/P4 y descuenta CALCE_A; no modifica Luis. Si golden_in_combined_required=false, una diferencia documentada por LUIS_REFERENCE_DIFF no es falla del pipeline.
