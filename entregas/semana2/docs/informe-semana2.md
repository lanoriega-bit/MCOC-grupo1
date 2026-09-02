# Semana 2 — Informe del modelo OpenSeesPy del edificio completo

## 1. Alcance

Modelo **lineal elástico 3D** de los **DOS bloques** del Edificio de Ingeniería con:
geometría completa, carga gravitacional transferida por **áreas tributarias**,
**diafragmas rígidos**, apoyos de fundación y salidas para el **viewer Unity**.
Los datos de entrada son trazables desde los planos originales (DWG→DXF vía ODA).

El edificio está formado por **dos bloques en planta** (plano 101) separados por una
**junta de dilatación de 10 cm** (confirmado por el cliente): el **bloque A** (torre
principal de columnas 70×70 cm, pisos subterráneo a 4°) y el **bloque B** (zona del
1° Subterráneo de **muros de contención**, sin columnas 70×70 propias), ubicado **al
lado** del bloque A (desplazado en +Y).

## 2. Datos de entrada (trazables)

- **Unidades del dibujo**: 1 unidad = 1 cm (cota 500.0 = 5.00 m; ancho total 45.00 m).
- **5 niveles de losa** (cota superior de losa):

| Piso | Cota (m) |
|------|----------|
| 1° Subterráneo | −4.01 |
| 1° | −0.05 |
| 2° | +3.91 |
| 3° | +7.87 |
| 4° / techumbre | +11.83 |

- **Altura de entrepiso**: H = 3.96 m (constante, diferencia de cotas consecutivas).
- **Retícula X**: ejes E, F, G, H, I, I' → `0, 10, 20, 30, 40, 45` m (vanos 10+10+10+10+5; eje secundario I' a media luz del último vano).
- **Retícula Y**: `0, 7.25, 16.15` m (3 filas; la techumbre usa solo las filas extremas).
- **Sección de columnas**: 70×70 cm (bloque principal). Vigas rectangulares de sección (60/80 dominante).
- **Carga gravitacional (plano 700)**: `q_G = PP losa + PM adic` con losa e=15 cm:
  `375 + 260 = 635 Kg/m² ≈ 6.35 kN/m²`. SC aplicada al piso típico: 250–500 Kg/m².

### Slot de carga adoptado para el modelo global

Dado que el modelo global es lineal elástico (membrana de diafragma, sin FE de losa),
se adopta una carga unitaria total representativa de piso:

```
q_G = 6.35 kN/m²  (PP losa 15cm + PM adic 260 Kg/m²)
SC  = 2.50 kN/m²  (carga viva representativa baja)
total = 8.85 kN/m²
```

El valor de carga y su distribución por zonas quedan concentrados en `CONFIG`
del script y son **independientes de la geometría** (la geometría no cambia si se
ajusta la carga; solo cambia el factor de escala de resultados).

## 3. Modelo

- Script: `entregas/semana2/opensees/edificio_completo_2bloques.py`
- **98 nodos, 192 elementos** (72 columnas + 108 vigas + **12 muros equivalentes**).
- Elementos `forceBeamColumn` / `elasticBeamColumn` 3D con secciones y materiales
  definidos en `CONFIG`.
- **Dos bloques en planta**:
  - **Bloque A (torre principal)**: retícula X `0,10,20,30,40,45` m, Y `0,7.25,16.15` m,
    niveles `−4.01` a `+11.83` m. Columnas 70×70, vigas, diafragmas y carga tributaria.
  - **Bloque B (1°S, muros de contención)**: caja rectangular de muros perimetrales al
    lado del bloque A (desplazada en +Y), separada por junta de dilatación de 10 cm.
    Dimensiones extraídas de `data/piso1S_raw.json` (plano 101): Lx = 21.90 m,
    Ly = 27.32 m. Solo existe en el nivel subterráneo (z −4.01 a −0.05). No aporta
    carga de losa típica ni tiene columnas 70×70 propias.
- **Muros equivalentes del 1° Subterráneo**: según la convención del curso, los muros
  de contención del perímetro (−4.01 a −0.05) se representan como elementos lineales
  verticales con sección de muro (e = 0.25 m): 8 muros sobre las líneas de columna del
  perímetro del bloque A + 4 muros perimetrales de la caja del bloque B. Aportan rigidez
  (no carga tributaria).
- **Diafragmas rígidos** (`rigidDiaphragm`) en los 5 niveles de losa del bloque A: los
  nodos de cada piso comparten los grados en el plano (movimiento como sólido rígido en x-y).
- **Apoyos**: base empotrada en el nivel inferior (fundación) de ambos bloques.
- Las **losas no se modelan como elementos finitos**; su carga se transfiere a las
  vigas mediante **áreas tributarias**.
- Ambos bloques **no comparten nodos** en la junta de dilatación (separación de 10 cm).

## 4. Área tributaria y transferencia de carga

Cada piso típico (1°–4°) aporta su carga a las vigas por área tributaria de su vigueta:

- Área de piso típico: `(45.0 × 16.15)` = **726.75 m²**.
- Carga por piso: `726.75 × 8.85` = **6431.74 kN**, repartida entre sus vigas
  (carga distribuida por tributary area por tramo).
- Carga total acumulada en vigas: **4 pisos × 6431.74 = 25726.95 kN**.

El 1° Subterráneo **no transfiere carga de losa típica**: es nivel de estacionamiento /
muros de contención, sin columnas 70×70 propias ni vigas tributarias; se incluye en la
geometría (nodos, diafragma y columnas que bajan desde el 1° a la base) pero no recibe
carga de losa como piso típico.

## 5. Verificaciones (asserts automáticos)

| Verificación | Método | Resultado |
|--------------|--------|-----------|
| Conservación de carga | Σ carga en vigas vs. 4×carga de piso | error **3.7e-12 kN** ✓ |
| Carga total de losa por piso | 4 pisos × 726.75 m² × 8.85 kN/m² | **25726.95 kN** ✓ |
| Suma de áreas tributarias | Σ trib_area de vigas vs. área de losa total (bloque A) | **2907.0 = 2907.0 m²** ✓ |
| Equilibrio vertical | Σ reacciones Z vs. Σ cargas | 25726.95 = 25726.95 kN, error **1.5e-11 kN** ✓ |
| Compatibilidad de diafragma | ux,uy iguales en todos los nodos de un piso (sólido rígido) | dif. en plano **2.2e-5 m** (< 0.1 mm) ✓ |
| Cálculo manual independiente (axial en columnas) | Σ axial manual por área tributaria (Voronoi) vs. reacciones en base de cada columna | Σ manual = **25726.95 kN** = Σ OpenSees; máx. error por columna **85.3 kN** ✓ |
| Convergencia del análisis | análisis elástico completo | convergente ✓ |

El script lanza **assert** y aborta si falla alguna, garantizando que los resultados
entregados están verificados.

## 6. Salidas

| Archivo | Contenido |
|---------|-----------|
| `opensees/edificio_completo_2bloques.py` | Modelo completo de los 2 bloques (configuración y verificación) |
| `results/verificacion_2bloques.json` | Resumen de conteos, cargas y checks |
| `results/geometria_edificio_2bloques.png` | Vista 3D de la geometría |
| `results/geometria_unity_2bloques.json` | **Contrato JSON OpenSees → Unity** (nodos, columnas, vigas, muros, apoyos, diafragmas, cargas, desplazamientos) |

El `geometria_unity_2bloques.json` es el contrato consumible por el **viewer Unity** para
orbitar la geometría y alternar nodos/vigas/columnas/muros/apoyos/diafragmas/IDs.

## 7. Comando de ejecución

```powershell
python entregas/semana2/opensees/edificio_completo_2bloques.py
python tools/build_viewer.py   # regenera viewer/index.html con los 2 bloques
```

## 8. Supuestos y pendientes (revisión humana)

- **Retícula Y** se adoptó como `0, 7.25, 16.15` m (3 filas). Debe cruzarse contra las
  cotas reales (vanos Y ~7.25 y ~8.90 m detectados).
- La **techumbre** usa solo 2 filas de columnas (x 6); las filas de cubierta/penthouse
  se modelan en la etapa de interface/penthouse.
- El **1°S** está modelado geométricamente, con sus **muros de contención como 12 muros
  equivalentes** (8 del bloque A + 4 del bloque B) y sin carga de losa típica.
- El **bloque B (muros 1°S)** se posicionó al lado del bloque A con su propia retícula
  (Lx = 21.90 m, Ly = 27.32 m) extraída de `piso1S_raw.json`; su posición exacta en Y
  relativa al bloque principal debe validarse visualmente contra el plano 101.
- `q_G` y `SC` son valores representativos por zona; los textos finos del plano 700
  (SC y PM por zona) y la asignación por área tributaria por vigueta deben validarse.
- Falta validación visual humana del PNG (este agente no interpreta imágenes).

## 9. Estado

Modelo de **dos bloques** completo, validado numéricamente (conservación, equilibrio y
diafragma rígido) y commiteado. Pendiente: validación humana de geometría/cargas y
siguientes etapas (interface Unity completa, análisis modal y sísmico).
