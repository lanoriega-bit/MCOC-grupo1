# Viewer de escritorio P1L6

Abrir el proyecto Unity `entregas/P1L3/José/viewer_unity`, escena `Assets/Main.unity`, y pulsar **Play**. En la pestaña **MODELO**, pulsar **Seleccionar E1-P2-V-041**. La ficha aparece a la derecha; **Aislar elemento** aproxima la cámara y oculta temporalmente el resto del edificio, y **Mostrar edificio** lo restaura.

En **RESULTADOS** se elige G, Q, EX, EY o R. Los coeficientes de R actualizan fuerzas y D/C por superposición lineal sin lanzar OpenSees. Los botones My, Mz, N, Vy, Vz y T abren las representaciones 3D; **Gráfico 2D CURRENT** abre la lectura de extremos con su clasificación física. La ficha contiene las secciones **PROPIEDADES**, **CARGAS**, **EJES**, **CAPACIDAD** y **DETALLE TÉCNICO**. El caso activo y la condición CURRENT aparecen siempre en la interfaz.

Los archivos `p1l6_current_materials.json` y `p1l6_current_member_identity.json` de StreamingAssets se generan desde el modelo central con los scripts de este directorio. Si el modelo canónico cambia, regenerar ambos catálogos antes de revisar una nueva versión del Viewer.

Datos y verificación de la viga: [E1_P2_V_041_DESKTOP_QA.md](E1_P2_V_041_DESKTOP_QA.md).
