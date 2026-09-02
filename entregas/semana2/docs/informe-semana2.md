# Semana 2 — Informe del modelo OpenSeesPy del edificio completo

## 1. Alcance

Modelo **lineal elástico 3D** del bloque principal del Edificio de Ingeniería con:
geometría completa, carga gravitacional transferida por **áreas tributarias**,
**diafragmas rígidos**, apoyos de fundación y salidas para el **viewer Unity**.
Los datos de entrada son trazables desde los planos originales (DWG→DXF vía ODA).

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

- Script: `entregas/semana2/opensees/edificio_completo.py`
- **90 nodos, 188 elementos** (72 columnas + 108 vigas + **8 muros equivalentes**).
- Elementos `forceBeamColumn` / `elasticBeamColumn` 3D con secciones y materiales
  definidos en `CONFIG`.
- **Muros equivalentes del 1° Subterráneo**: según la convención del curso, los muros
  de contención del perímetro (−4.01 a −0.05) se representan como 8 elementos lineales
  verticales con sección de muro (e = 0.25 m) sobre las líneas de columna del perímetro,
  reproduciendo la caja de contención. Aportan rigidez (no carga tributaria).
- **Diafragmas rígidos** (`rigidDiaphragm`) en los 5 niveles de losa: los nodos de
  cada piso comparten los grados en el plano (movimiento como sólido rígido en x-y).
- **Apoyos**: base empotrada en el nivel inferior (fundación).
- Las **losas no se modelan como elementos finitos**; su carga se transfiere a las
  vigas mediante **áreas tributarias**.

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
| Suma de áreas tributarias | Σ trib_area de vigas vs. área de losa total | **2907.0 = 2907.0 m²** ✓ |
| Equilibrio vertical | Σ reacciones Z vs. Σ cargas | 25726.95 = 25726.95 kN, error **2.2e-11 kN** ✓ |
| Compatibilidad de diafragma | ux,uy iguales en todos los nodos de un piso (sólido rígido) | dif. en plano **7.3e-6 m** (< 0.1 mm) ✓ |
| Cálculo manual independiente (axial en columnas) | Σ axial manual por área tributaria (Voronoi) vs. reacciones en base de cada columna | Σ manual = **25726.95 kN** = Σ OpenSees; máx. error por columna **50.0 kN** (~1.2% en columnas mayores) ✓ |
| Convergencia del análisis | análisis elástico completo | convergente ✓ |

El script lanza **assert** y aborta si falla alguna, garantizando que los resultados
entregados están verificados.

## 6. Salidas

| Archivo | Contenido |
|---------|-----------|
| `opensees/edificio_completo.py` | Modelo completo (configuración y verificación) |
| `results/verificacion.json` | Resumen de conteos, cargas y checks |
| `results/geometria_edificio.png` | Vista 3D de la geometría |
| `results/geometria_unity.json` | **Contrato JSON OpenSees → Unity** (nodos, columnas, vigas, apoyos, diafragmas, cargas, desplazamientos) |

El `geometria_unity.json` es el contrato consumible por el **viewer Unity** para
orbitar la geometría y alternar nodos/vigas/columnas/muros/apoyos/diafragmas/IDs.

## 7. Comando de ejecución

```powershell
python entregas/semana2/opensees/edificio_completo.py
```

## 8. Supuestos y pendientes (revisión humana)

- **Retícula Y** se adoptó como `0, 7.25, 16.15` m (3 filas). Debe cruzarse contra las
  cotas reales (vanos Y ~7.25 y ~8.90 m detectados).
- La **techumbre** usa solo 2 filas de columnas (x 6); las filas de cubierta/penthouse
  se modelan en la etapa de interface/penthouse.
- El **1°S** está modelado geométricamente, con sus **muros de contención como 8 muros
  equivalentes** y sin carga de losa típica (nivel de estacionamiento).
- `q_G` y `SC` son valores representativos por zona; los textos finos del plano 700
  (SC y PM por zona) y la asignación por área tributaria por vigueta deben validarse.
- Falta validación visual humana del PNG (este agente no interpreta imágenes).

## 9. Estado

Modelo completo, validado numéricamente (conservación, equilibrio y diafragma rígido) y
commiteado. Pendiente: validación humana de geometría/cargas y siguientes etapas
(diafragmas por bloque, interface Unity completa, análisis modal y sísmico).
