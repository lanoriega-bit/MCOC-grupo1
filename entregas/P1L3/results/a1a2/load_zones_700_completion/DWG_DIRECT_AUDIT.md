# Comprobación directa del respaldo DWG 2018

Se abrió `2017_67-700.bak` como copia temporal mediante AutoCAD Core Console
2026 y se cerró descartando cambios. Esta comprobación es independiente del DXF
derivado usado por el script espacial.

En la capa `HATCH CARGAS` se encontraron 168 TEXT, 140 LINE, 51 HATCH,
25 LWPOLYLINE y 1 INSERT. No aparecen LEADER, MLEADER ni POINT.

Se confirmaron literalmente las anotaciones `SC=7000 Kg`, `SC=6000 Kg` y
`SC=6700 Kg`, junto con `CARGA PUNTUAL`. No existe una entidad de llamada
inequívoca que permita transformar la coordenada del texto en punto de
aplicación o receptor; las tres quedan `UNRESOLVED`.

También se confirmó `PM. ADIC. = 2800 Kg/m` y una entidad TEXT separada `2` en
`(7550.145, 3037.468)`, elevada respecto de la línea base. La unidad completa
es, por tanto, `kgf/m²` y su estado final es `CONFIRMED_UNIT`.
