# P1L5 — Defensa y demo de 5 minutos

## Explicación corta

OpenSees es dueño del análisis, Unity de la interacción y JSON del intercambio. Calculamos cuatro casos base lineales compatibles (`G`, `Q`, `EX`, `EY`). Unity combina desplazamientos y fuerzas con coeficientes elegidos por el usuario, por eso mover sliders no requiere reanálisis. Cambiar una carga base, sección, material, apoyo o conectividad sí cambia el modelo y deja los resultados `STALE` hasta ejecutar nuevamente OpenSees.

La demanda P-M del elemento seleccionado se actualiza con la combinación activa y se compara con una curva compatible. `D/C` se clasifica como `OK`, `WARNING`, `EXCEEDS` o `NO CAPACITY DATA`.

## Guion

**0:00–1:00 · Modelo e interacción**  
Mostrar el edificio, navegar, apagar/encender una capa y seleccionar una viga. Enseñar ID, piso, sección, material y ejes locales.

**1:00–2:00 · Resultados CURRENT**  
Mostrar el panel de estado (`CURRENT`, OpenSees `PASS`), deformada y diagramas `My` y `N`/`V`. Aclarar unidades.

**2:00–3:00 · Superposición**  
Mover `G`, `Q`, `EX`, `EY`. Enseñar que deformada, fuerzas y R cambian al instante. Explicar que no se reanaliza porque los casos comparten K, nodos, apoyos y ejes.

**3:00–4:00 · Capacidad**  
Seleccionar columna/muro con capacidad. Abrir P-M, mover un slider y mostrar el punto CURRENT, D/C y estado.

**4:00–5:00 · Modificación real**  
Cambiar factor Q o sección. Mostrar `MODIFIED / STALE / REANALYSIS REQUIRED`. Reanalizar y confirmar que vuelve a `CURRENT`.

## Respuestas de defensa

- **¿Por qué funciona la superposición?** Es un análisis lineal elástico con la misma rigidez, topología, apoyos y convenciones.
- **¿Cuándo deja de funcionar?** Con no linealidad, cambio de sección/material/apoyo/conectividad, grandes deformaciones o casos incompatibles.
- **¿Qué obliga a reanalizar?** Carga base, sección, E, apoyo, elemento activo o tributaria.
- **¿Qué no obliga?** Visualización, escala, capas y combinación lineal de resultados vigentes.
- **¿Demanda versus capacidad?** Demanda es la respuesta requerida; capacidad es el límite resistente. D/C las compara.
- **¿Qué aproximamos?** G35 con 28 GPa; 79 materiales desconocidos con G35 predominante; espesor de losa 0,15 m; cargas sin posición inequívoca permanecen unresolved.
- **¿Limitación principal?** Es académico; `E2-P4-V-009` está STOP y algunas cargas no tienen receptor actual inequívoco.
