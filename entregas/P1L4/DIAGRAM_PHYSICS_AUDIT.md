# Auditoría física de diagramas P1L4

Estado: `PASS`

## Aplicación real de cargas

El modelo usa `B_NODAL_LOADS`. G/Q se convierten en P/2 nodal mediante `ops.load`; EX/EY también son nodales. No existe `ops.eleLoad` ni carga distribuida interior.

## Forma por componente

| Componente | Forma coherente en este FE | Clasificación |
| --- | --- | --- |
| N | constante | END_FORCES_INTERPOLATION |
| Vy | constante | END_FORCES_INTERPOLATION |
| Vz | constante | END_FORCES_INTERPOLATION |
| T | constante | END_FORCES_INTERPOLATION |
| My | lineal, asociado a Vz | END_FORCES_INTERPOLATION |
| Mz | lineal, asociado a Vy | END_FORCES_INTERPOLATION |

Las acciones OpenSees de i/j actúan sobre caras opuestas. Para una cara interna común: `i=end1`, `j=-end2`. No se fabrican estaciones ni curvas parabólicas.

## Comprobación manual E2-P1-V-056 / R

- L = 4.709565 m; tag 10473; analysis_id `A-V-0473`.
- x local = [0.9979690828636266, 0.06370015422533802, 0.0]; z local = [0.0, -0.0, 1.0] (vertical global).
- My crudo OpenSees: i=846.089242, j=-48.227209 kN·m.
- My interno cara común: i=846.089242, j=48.227209 kN·m.
- Vz interno = -169.413115 kN; residual My=0.000e+00 N·m.
- Residual máximo entre 1312 elementos y cinco casos: 1.863e-09 en unidades SI; PASS.
- Esta viga no recibe una entrada G/Q directa en el enrutamiento A7; responde a las cargas nodales de la estructura conectada.
