# Contrato CURRENT — preparado, sin resultados fabricados

Estado: `BLOCKED_NOT_RUN`. No existe payload numérico CURRENT. El inspector
normal no consulta el diccionario de resultados archivados. El acceso histórico
requiere opt-in explícito en Entregas/Avanzado y conserva su advertencia.

`build_current_contract.py` identifica geometría (incluidas propiedades), candidato
FE, catálogo de cargas y archivo geométrico distribuido mediante SHA-256. Incluye
`geometry_version`, `fe_version`, `loads_version`, `analysis_version`, `git_commit`,
`timestamp`, `units`, `cases`. El commit identifica la base de generación; los
hashes identifican los bytes, también antes de guardar el checkpoint en Git.

Un catálogo auditado NO es un vector de cargas aprobado. En una corrida futura,
`loads_version` debe identificar el paquete efectivamente aplicado, con áreas,
receptores, pesos propios y parámetros sísmicos; no reutilizar este hash provisional.

## Puerta de entrada

`CurrentVersionGate.Check` rechaza contratos ausentes, entradas no aprobadas,
resultados no verificados/históricos, versiones distintas, archivo geométrico
distinto, unidades incorrectas, casos incompletos y payload ausente. El resultado
positivo es deliberadamente `IDENTITY_MATCH_REQUIRES_PAYLOAD_QA`, NO autorización
para mostrar cifras ni certificación de equilibrio.

El futuro importador numérico aún debe verificar SHA del payload, esquema,
IDs/crosswalk 1:N, orden de nodos/miembros, extremos, ejes, ausencia de NaN/Inf,
equilibrio global/local y comparación de R con una corrida explícita. Debe mostrar
CURRENT solamente tras ambos controles. Hoy no existe ese importador ni un dataset
aprobado: se mantiene el mensaje «Resultados actuales no disponibles».

## Datos previstos

- SI en almacenamiento: m, N, N.m, Pa, kg, rad; kN/kN.m/mm sólo presentación.
- Bases ordenadas G, Q, EX, EY; R incluye sus cuatro coeficientes y procedencia.
- Por caso: desplazamientos y reacciones por nodo; N/Vy/Vz/T/My/Mz firmados en
  ambos extremos por miembro; ejes locales; cargas nodales y de elemento aplicadas.
- No interpolar cargas distribuidas inexistentes. Si existen cargas de elemento,
  exportar distribución y estaciones suficientes para reconstruir equilibrio.
- Resumen futuro: axial con convención comprobada, corte/momento dominante con
  componente y extremo explícitos, desplazamiento con definición precisa. No se
  convirtió el histórico en ese resumen ni se introdujeron números de ejemplo.

La identidad del contexto de conexiones del inspector se compara con la versión
geométrica. Las conexiones listadas son incidencias candidatas, no apoyos aprobados.

## Ensayos

`ViewerReviewQA` ejecuta pruebas de rechazo de geometría, FE, cargas, unidades,
estado histórico y bytes geométricos; combinación firmada y rechazo de NaN.
`validate_current_readiness.py` verifica archivos reales, 909 registros de contexto,
alcance de materiales y bloqueo numérico. Las pruebas de contrato no ejecutan OpenSees.
