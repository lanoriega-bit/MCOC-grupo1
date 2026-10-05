# Unity CURRENT — QA de núcleos

Estado: **PASS_WITH_NOTE**. Editor Unity 6000.6.0f1, Assets/Main.unity,
Play real sobre el proyecto canónico. No se probó AR ni Android en este hito.

## Compilación

Se corrigió el error de la función nueva de captura, que dependía de un módulo
ScreenCapture no incluido en el proyecto. Ahora captura el framebuffer Game
con Texture2D, sin agregar dependencias. Recompilación: cero errores en consola;
Play abre y ejecuta la escena. Persisten advertencias antiguas de APIs
FindObjectsOfType y tipos JSON anidados; no se declaran resueltas en este hito.

## Prueba reproducible

`UNITY_RUNTIME_QA.json`: 76 controles PASS / CURRENT_VERIFIED.
Ejecutada desde MCOC → Validar núcleos CURRENT y capturar vistas.

- Defaults: vigas, columnas, muros y nodos ON; losas y mapa/falla OFF.
- Filtros: ED1/ED2, S1/P1/P2/P3/P4 y BASE; categorías estructurales y nodos.
- Selección: E1-P2-V-041, E2-P4-C-004/C-007, E1-P4-M-007 y E2-P4-M-009.
- Resultados G/Q/EX/EY/R disponibles para las cinco selecciones.
- Explicaciones de los cinco casos; R usa coeficientes adimensionales.
- D/C: activar/apagar restaura exactamente los colores normales.
- Capturas ISO/TOP/FRONT/RIGHT desde Game; archivos unity_*.png.

## Contraste visual e interacción

En TOP se observan tres C completas. ISO/elevación muestran sus paños
hasta P4. Las plantas before_cores/after_cores tienen la misma escala y
encuadre; BEFORE incluye ambos snapshots externos normalizados. La corrección
ED1 utiliza controles de ejes propios: no copia su offset externo.

También se seleccionó manualmente la viga de demostración y se pulsaron
G/Q/EX/EY/R para leer la ayuda y verificar el cambio de caso en su ficha.
La escala Game 1,3x recortaba los paneles aunque el framebuffer era completo;
se ajustó a 1x. Esto es una preferencia del editor, no un problema del dataset.

La prueba automatizada recorre más controles que la inspección manual; se
conserva esa distinción. No se afirma haber verificado un APK o hardware AR.

## Modelación

Las C son tres paños físicos. El FE sigue usando barras equivalentes y
vínculos del adaptador vigente; no se afirma que reproduzca el comportamiento
de una sección C compuesta monolítica o de shells. La validación de continuidad
y apoyo confirma el modelo de laboratorio implementado, no su diseño normativo.
