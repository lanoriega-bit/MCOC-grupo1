# Unity Play QA

Fecha: 2026-09-29  
Unity: 6000.6.0f1  
Escena: `Assets/Main.unity`

## Resultado

`PASS`

- Compilación C#: PASS, retorno 0.
- Capas y pisos ON/OFF: PASS.
- Diagnóstico FE, filtros y crosswalk 1:N: PASS.
- G/Q/EX/EY/R CURRENT, 619 segmentos, 1.100 nodos, ejes locales y
  superposición: PASS.
- Selección, casos, deformada, My/Mz/N/Vy/Vz, sliders y R instantánea:
  PASS.
- Modelo CURRENT con histórico apagado: PASS.
- Ciclo Play/Edit automatizado: completo.

La prueba se ejecutó en modo batch, abrió la escena real, entró en Play,
esperó los chequeos de runtime, volvió a Edit y cerró Unity con retorno 0.
