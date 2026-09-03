# Viewer gravedad Edificio 1

Viewer web autocontenido para `entregas/semana2_gravedad/results/edificio1_unity.json`.

## Que muestra

- Losas por piso con `gravity_verified` y cargas `qG`, `PP`, `PM`, `SC`.
- Vigas con nodos, longitud, area tributaria, `P_kN` y `w_lineal_kN_m`.
- Poligonos tributarios por viga, ocultos por defecto para no saturar la vista.
- Blocker geometrico `E1_F01_L101` sin inventar geometria de gravedad.
- Toggles por piso/capa, busqueda por ID y panel de seleccion.

## Ejecutar

Desde la raiz del repo:

```bash
python3 -m http.server 8000
```

Abrir:

```text
http://localhost:8000/entregas/semana2_gravedad/viewer/
```

No abrir `index.html` directo con `file://`, porque el navegador bloquea `fetch()` del JSON local.

## Validar contrato

```bash
python3 entregas/semana2_gravedad/viewer/validate_viewer_json.py
```

La validacion comprueba que el viewer puede consumir el JSON E1 existente y que `E1_F01_L101` permanece como `GEOMETRIC_BLOCKER_EXCLUDED_FROM_VERIFIED_GRAVITY`.
