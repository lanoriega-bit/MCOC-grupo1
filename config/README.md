# Configuración

- `project_config.json`: rutas relativas a la raíz y ubicación de validadores.
- `analysis_settings.json`: única fuente editable de qQ y política sísmica actual.

La copia de configuración en StreamingAssets es una salida generada para Unity,
no una fuente editable. No agregar parámetros equivalentes en otro script.
La intensidad actual de qQ y sus supuestos permanecen intactos.

`historical_property_paths` sirve exclusivamente para consultar la procedencia
Git del resultado guardado; no lee archivos semanales del disco ni es fallback.
Se conserva mientras ese resultado apunta a un commit anterior a la migración.

Estado: fuentes trasladadas; consolidación de módulos y configuración global
final todavía pendiente. No declarar `FINAL` por tener estas carpetas.
