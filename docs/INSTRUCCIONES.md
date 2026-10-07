# Instrucciones reproducibles — Semana 7 (entrega final)

Estas instrucciones permiten reproducir desde cero el estado CURRENT del
laboratorio: análisis, QA, viewer de escritorio y compilación de la aplicación
AR para Android. El punto de partida es un clon limpio del repositorio.

El entregable se congela en el tag `SEMANA7_ENTREGA`
(commit `c243a7b` de `origin/main`).

---

## 1. Prerrequisitos

| Herramienta | Versión verificada | Notas |
| --- | --- | --- |
| Windows | 10/11 x64 | Shell PowerShell |
| Python | 3.12.x x64 | Python canónico del proyecto |
| OpenSeesPy | 3.8.0.0 | Fijado en `requirements.txt` |
| Unity | 6000.6.0f1 | Licencia personal activa en Unity Hub |
| Git | cualquiera reciente | Solo para clonar/validar |

No actualizar paquetes: las versiones están congeladas en `requirements.txt`
y en `Packages/manifest.json` del Viewer para que el resultado sea reproducible.

---

## 2. Clonar y preparar el entorno

```powershell
git clone https://github.com/lanoriega-bit/MCOC-grupo1.git
cd MCOC-grupo1
git checkout SEMANA7_ENTREGA   # punto exacto de la entrega

python --version                # confirmar 3.12.x
python -m venv .venv-p1l5
.\.venv-p1l5\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 3. Validar el modelo CURRENT sin recalcular física

```powershell
.\Proyecto.bat validar          # o: python main.py validar
```

Este comando verifica fuentes, topología FE, equilibrio, contratos, hashes y
crosswalk Unity **sin** ejecutar OpenSees. No modifica geometría ni cargas.
Si el clon no contiene la historia Git del commit fuente de secciones/materiales,
el resultado es `REVIEW REQUIRED` y no se debe certificar el modelo.

---

## 4. Estado rápido y rutas

```powershell
.\Proyecto.bat estado   # conteos + identidad rápida del dataset
.\Proyecto.bat rutas    # rutas completas de los archivos canónicos
```

---

## 5. Recalcular G/Q/EX/EY/R y capacidades (opcional, solo si cambia la física)

El pipeline CURRENT usa geometría y tributarias **versionadas**: no necesita los
planos CAD originales.

```powershell
.\.venv-p1l5\Scripts\python.exe -B tools/rebuild_all.py          # muestra el plan
.\.venv-p1l5\Scripts\python.exe -B tools/rebuild_all.py --execute # recalcula
```

Cambiar la carga uniforme `qQ` (valor inicial **0,667 kN/m²** en
`config/analysis_settings.json`) invalida Q/EX/EY/R y D/C y obliga a reanalizar;
la carga sísmica mantiene explícitamente la hipótesis educativa
**0,20 × (G + 0,50 Q)**.

Para regenerar las curvas Fiber P-M/M-φ (estudio separado de la capacidad CURRENT):

```powershell
.\.venv-p1l5\Scripts\python.exe -B analysis/fiber/reproduce_studies.py
# resultados en results/fiber
```

---

## 6. Abrir el viewer de escritorio (Unity)

```powershell
.\Abrir_Unity.bat
```

En Unity Hub el proyecto canónico es `viewer/unity`:

1. Abrir `Assets/Main.unity`.
2. Pulsar **Play** y usar la pestaña **Game** (escala 1x si queda recortado).
3. En **Análisis**: cambiar `qQ [kN/m²]` → **Guardar** → **Reanalizar** para
   probar sensibilidad; `λQ` solo combina respuestas (no cambia el caso físico Q).

El ejecutable de escritorio compilado (Windows x64) se genera con el builder
`viewer/unity/Assets/Editor/CurrentReviewBuild.cs` hacia
`viewer/unity/Builds/CurrentReview/StructuralReview.exe`.

---

## 7. Compilar la aplicación AR para Android (APK)

La escena `P1L6_AR_Final` muestra resultados CURRENT superpuestos sobre una
imagen objetivo detectada con ARCore (tracking por imagen, mín. API 29, ARM64).

### 7.1 Instalar una sola vez las herramientas Android en Unity Hub

Unity Hub → **Installs** → `6000.6.0f1` → **···/Añadir módulos** → marcar:

- **Android Build Support**
- **OpenJDK** (incluido con el módulo)
- **Android SDK & NDK Tools**

Son ~2,5 GB. Sin este módulo, el compilador falla con
`ANDROID_BUILD_SUPPORT_MISSING`.

### 7.2 Habilitar el builder

El script está deshabilitado en el repositorio (`.disabled`) para que el proyecto
de escritorio compile sin instalar el módulo Android. Para compilar la APK:

1. Renombrar `Assets/Editor/P1L6AndroidBuilder.cs.disabled` → `.cs`
   (conservar el `.meta` con su GUID).
2. Abrir una consola en la raíz del repo y ejecutar:

```powershell
$unity = "C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe"
& $unity -batchmode -nographics -quit `
  -projectPath (Join-Path (Get-Location) "viewer\unity") `
  -executeMethod Mcoc.UnityViewer.EditorTools.P1L6AndroidBuilder.BuildApk
```

La APK se genera en `viewer/unity/Builds/P1L6/P1L6_AR_Final.apk`.

### 7.3 Verificación de la escena AR

El builder valida antes de compilar: una sola cámara, `ARSession`, `XROrigin`,
`ARTrackedImageManager` (biblioteca con 1 imagen), `ARAnchorManager` y el
dataset `p1l6_current_ar_elements.json` presente en `StreamingAssets`.
Cualquier incumplimiento aborta el build con un mensaje explícito.

### 7.4 Instalación en el teléfono

```powershell
adb install -r viewer/unity/Builds/P1L6/P1L6_AR_Final.apk
```

(o copiar la APK al dispositivo y aceptar la instalación). La demostración usa
la imagen `Assets/AR/Image_AR.png` como marcador.

> Nota: el AutoCAD/DXF original no es necesario en ningún paso; todo deriva de
> las fuentes canónicas `model/model_master.json`, `model/sections.json`,
> `model/materials.json`, `model/loads.json` y `config/`. Flujo de datos:
> `model → analysis → results → Unity / AR`.

---

## 8. Comandos de referencia rápida

| Acción | Comando |
| --- | --- |
| Validar modelo (sin recalcular) | `.\Proyecto.bat validar` |
| Estado del dataset | `.\Proyecto.bat estado` |
| Abrir Unity | `.\Abrir_Unity.bat` |
| Plan de recálculo | `python -B tools/rebuild_all.py` |
| Recálculo completo | `python -B tools/rebuild_all.py --execute` |
| Estudios Fiber | `python -B analysis/fiber/reproduce_studies.py` |
| Build APK AR | `Unity.exe -batchmode ... -executeMethod Mcoc.UnityViewer.EditorTools.P1L6AndroidBuilder.BuildApk` |