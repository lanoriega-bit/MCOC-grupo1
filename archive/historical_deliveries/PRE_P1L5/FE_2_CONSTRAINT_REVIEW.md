# FE-2 — revisión de restricciones, no análisis

Estado: `ALGEBRAIC_PROPOSAL_NOT_APPLIED`.

El candidato vigente continúa intacto: 856 miembros, 43 residuales y 22
componentes flotantes. No se crea un FE aprobado ni se ejecuta OpenSees.

## Resultado verificable

1482 brazos existentes pueden representarse mediante 946 enlaces estrella
dentro de los mismos componentes, suponiendo vínculos de cuerpo rígido completos
y pequeñas rotaciones. Se verifica con seis movimientos base: residual máximo
3.552713678800501e-15. Es equivalencia cinemática bajo hipótesis, no aprobación
de la estructura ni prueba de rango del sistema global.

## Por qué no se aplica

El cluster con raíz 162 reúne 41 nodos, extensión 11.875×26.448 m en planta.
Otros alcanzan 10.175×16.6 m o 13.524 m. Debe justificarse qué parte del muro,
encuentro o cuerpo representa esa rigidez, y si está rigidizando vanos enteros.
La normalización no elimina una hipótesis física equivocada: la conserva.

Los nodos múltiples/encadenados y los posibles apoyos dentro de clusters
necesitan tratamiento coherente de condiciones SP/MP. La documentación oficial
de [Transformation](https://opensees.github.io/OpenSeesDocumentation/user/manual/analysis/constraint/TransformationMethod.html)
advierte sobre nodos retenidos que a su vez están restringidos.
La matriz usada para la prueba procede de
[rigidLink beam](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidLink.html).

## Siguiente decisión estructural

Revisar físicamente esos clusters contra los miembros/encuentros primarios,
definir la idealización de los muros y después formular vínculos sin cadenas.
No fijar componentes aislados, no añadir apoyos, no declarar conectados los
muros solo por intersección de huellas. Los cuatro redondeos de 0.1 mm quedan
identificados para una corrección del adaptador dentro de esa formulación.

Artefacto separado: `constraint_normalization_proposal.json`, regenerado por
`scripts/audit_remaining.py`. El candidato y los resultados históricos no se
modifican. Esta propuesta NO es el FE canónico de PRE-P1L5.
