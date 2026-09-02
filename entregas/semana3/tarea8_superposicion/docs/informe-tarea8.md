# Tarea 8 — Superposición de cargas G y Q + combinaciones lineales

## Objetivo

Sobre el modelo del edificio (bloque principal, 5 niveles = 1 sub + 4 pisos) se
resuelven los casos base de carga **gravitacional (G)** y **viva (Q)**, transferidas
por áreas tributarias, y se verifica el **principio de superposición lineal** y las
**combinaciones lineales** de diseño.

## Modelo

- Misma geometría que Semana 2: 90 nodos, 180 elementos (72 columnas + 108 vigas),
  5 niveles de losa, diafragmas rígidos, cargas por áreas tributarias (1/4 por borde).
- Casos base:
  - **G**: solo gravitacional `q_G = 6.35 kN/m²`, 4 pisos cargados (el sub no carga).
  - **Q**: solo viva `SC = 2.50 kN/m²`, 4 pisos cargados.
- Método: se reconstruye el modelo por caso (enfoque inequívoco para superposición).

## Resultados

| Caso | ΣRz [kN] | Verificación |
|------|----------|--------------|
| G | 18459.45 | 4 × (726.75 m² × 6.35) = 18459.45 ✓ |
| Q | 7267.50 | 4 × (726.75 m² × 2.50) = 7267.50 ✓ |
| G + Q | 25726.95 | = G + Q ✓ |

### Superposición

- `R(G) + R(Q) − R(G+Q)` sum abs diff = **1.50e-11 kN** (≈ 0) ✓
- Desplazamientos, máximo diff = **2.4e-18 m** (≈ 0) ✓

### Combinaciones lineales (superpuestas vs. directas)

| Combinación | err Rz máx [kN] | err disp [m] |
|-------------|-----------------|--------------|
| 1.0G | 0 | 0 |
| 1.4G | 2.8e-12 | 4.3e-18 |
| 1.2G + 1.6Q | 2.8e-12 | 3.9e-18 |
| 1.4G + 1.4Q | 2.3e-12 | 2.1e-18 |
| 1.0G + 1.0Q | 3.3e-12 | 2.4e-18 |

Todos los errores son del orden de la precisión numérica: la combinación lineal de
casos base equivale a correrla directamente, como exige un modelo elástico lineal.

## Archivos

- Script: `opensees/superposicion_GQ.py`
- Resultados: `results/superposicion_GQ.json`, `results/superposicion_reacciones.png`

## Comando

```powershell
python entregas/semana3/tarea8_superposicion/opensees/superposicion_GQ.py
```

## Estado

Verificado (asserts automáticos): superposición y combinaciones lineales correctas.
