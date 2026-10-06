# Unity CURRENT Play QA

Fecha: 2026-09-24  
Escena: `Assets/Main.unity`  
Unity: 6000.6.0f1

## Resultado

- Compilación C#: **PASS** (sin errores CS).
- Play con dataset `P1L5_CURRENT_ZONED_V2`: **PASS**.
- `[P1L5 QA] PASS`: G/Q/EX/EY/R, 629 segmentos analizados, 1.110 nodos, ejes locales y superposición.
- `[P1L5 DEMO QA] PASS`: selección, casos, deformada, My/Mz/N/Vy/Vz, sliders y R instantánea.
- `[CURRENT UI QA] PASS`: modelo actual, histórico apagado y resultados CURRENT disponibles.

Los 629 elementos de resultado son los 633 segmentos FE activos menos cuatro segmentos redundantes cuyos dos extremos pertenecen al mismo cluster rígido. La exclusión evita lazos de deformación nula y está registrada en cada caso OpenSees.
