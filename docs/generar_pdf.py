"""Genera un PDF con la explicacion del codigo P1L0 para imprimir y repasar."""

from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "MCOC-grupo1 | P1L0 - Explicacion del codigo", align="R")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def titulo(self, txt):
        self.set_font("Helvetica", "B", 16)
        self.set_fill_color(44, 114, 196)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, txt, fill=True, align="C")
        self.set_text_color(0, 0, 0)
        self.ln(6)

    def subtitulo(self, txt):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(214, 228, 240)
        self.cell(0, 9, txt, fill=True)
        self.ln(6)

    def sub2(self, txt):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(44, 114, 196)
        self.cell(0, 7, txt)
        self.set_text_color(0, 0, 0)
        self.ln(5)

    def texto(self, txt):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5, txt)
        self.ln(2)

    def codigo(self, txt):
        self.set_font("Courier", "", 8)
        self.set_fill_color(245, 245, 245)
        self.multi_cell(0, 4.5, txt, fill=True)
        self.set_font("Helvetica", "", 10)
        self.ln(2)

    def nota(self, txt):
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 5, txt)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def linea(self):
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)


pdf = PDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)

# ===================== PAGINA 1: PORTADA =====================
pdf.add_page()
pdf.ln(30)
pdf.titulo("P1L0 - Ejemplo Minimo 2D\nOpenSeesPy")
pdf.ln(10)
pdf.set_font("Helvetica", "", 12)
pdf.cell(0, 8, "Marco isostatico de tres articulaciones", align="C")
pdf.ln(6)
pdf.cell(0, 8, "Pregunta 2 - Control 1 Estructuras Isostaticas", align="C")
pdf.ln(15)
pdf.set_font("Helvetica", "", 11)
pdf.cell(0, 7, "Grupo: MCOC-grupo1", align="C")
pdf.ln(6)
pdf.cell(0, 7, "Curso: Analisis Estructural", align="C")
pdf.ln(6)
pdf.cell(0, 7, "Fecha de entrega: Jueves 20 de agosto 2026", align="C")
pdf.ln(20)
pdf.linea()
pdf.set_font("Helvetica", "I", 10)
pdf.cell(0, 7, "Documento generado con ayuda de OpenCode (IA)", align="C")

# ===================== PAGINA 2: QUE MODELAMOS =====================
pdf.add_page()
pdf.titulo("1. QUE MODELAMOS")
pdf.subtitulo("Ejercicio")
pdf.texto(
    "Se modela el marco isostatico de la Pregunta 2 del Control 1 "
    "de Estructuras Isostaticas. El marco tiene 4 barras inclinadas "
    "(AB, BC, CD, DE), apoyos articulados en A y E, y una rotula "
    "interna en C. Se le aplica una carga distribuida vertical de "
    "3 tonf/m sobre la proyeccion horizontal."
)

pdf.subtitulo("Geometria")
pdf.codigo(
    "A = (0.0, 0.0)  m     E = (13.0, 0.0) m\n"
    "B = (4.0, 3.0)  m\n"
    "C = (6.5, 3.0)  m  (punto de rotula interna)\n"
    "D = (9.0, 3.0)  m"
)

pdf.subtitulo("Seccion: HE 340 AA (acero)")
pdf.codigo(
    "E  = 200 GPa = 200e9 Pa\n"
    "A  = 9424.5 mm2\n"
    "Iz = 182805143.4 mm4\n"
    "Wz = 1142532.1 mm3\n"
    "tw = 8.5 mm"
)

pdf.subtitulo("Carga")
pdf.codigo("q = 3 tonf/m (vertical, hacia abajo, sobre proyeccion horizontal)")

pdf.subtitulo("Apoyos")
pdf.texto(
    "- Nodo A: apoyo articulado (restringe ux y uy, libre rz)\n"
    "- Nodo E: apoyo articulado (restringe ux y uy, libre rz)\n"
    "- Nodo C: rotula interna (equalDOF comparte ux, uy pero no rz)"
)

pdf.subtitulo("Tipo de modelo OpenSees")
pdf.codigo(
    'ops.model("basic", "-ndm", 2, "-ndf", 3)\n'
    "# 2 dimensiones, 3 GDL por nodo: ux, uy, rz"
)

# ===================== PAGINA 3: BLOQUE IMPORTACIONES =====================
pdf.add_page()
pdf.titulo("2. IMPORTACIONES Y CONSTANTES")

pdf.subtitulo("Librerias")
pdf.codigo(
    "from __future__ import annotations  # Tipos modernos\n"
    "import math                         # hypot, isclose\n"
    "from pathlib import Path            # Rutas de archivos\n"
    "import matplotlib                   # Graficos\n"
    'matplotlib.use("Agg")              # Sin pantalla\n'
    "import matplotlib.pyplot as plt     # Interfaz de graficos\n"
    "import openseespy.opensees as ops   # Motor de analisis"
)

pdf.subtitulo("Constantes de conversion")
pdf.codigo(
    "TONF    = 1_000.0 * 9.8    # 1 tonf = 9800 N\n"
    "MM2_TO_M2 = 1.0e-6         # mm2 a m2\n"
    "MM4_TO_M4 = 1.0e-12        # mm4 a m4\n"
    "MM3_TO_M3 = 1.0e-9         # mm3 a m3\n"
    "MPA       = 1.0e6          # 1 MPa = 1e6 Pa"
)

pdf.nota(
    "Razon: el enunciado entrega propiedades en mm y tonf, "
    "pero OpenSees trabaja en SI (m, N, Pa). Hay que convertir todo."
)

pdf.subtitulo("Funciones auxiliares de conversion")
pdf.codigo(
    "def tonf(value_newton):\n"
    "    return value_newton / TONF\n"
    "\n"
    "def tonf_m(value_newton_meter):\n"
    "    return value_newton_meter / TONF"
)

# ===================== PAGINA 4: FUNCION DE CARGA =====================
pdf.add_page()
pdf.titulo("3. FUNCION: CARGA DISTRIBUIDA")

pdf.sub2("add_vertical_load_on_horizontal_projection()")
pdf.texto(
    "Esta es la funcion mas importante del codigo. "
    "Resuelve un problema real: el enunciado dice '3 tonf/m sobre "
    "la proyeccion horizontal', pero OpenSees aplica cargas en "
    "ejes LOCALES del elemento. Los elementos AB, BC, CD, DE estan "
    "inclinados, entonces hay que convertir."
)

pdf.subtitulo("Paso 1: Obtener geometria del elemento")
pdf.codigo(
    "xi, yi = ops.nodeCoord(node_i)   # Coordenadas nodo inicial\n"
    "xj, yj = ops.nodeCoord(node_j)   # Coordenadas nodo final\n"
    "dx = xj - xi                      # Distancia horizontal\n"
    "dy = yj - yi                      # Distancia vertical\n"
    "length = math.hypot(dx, dy)       # Longitud real del elemento\n"
    "cos_theta = dx / length           # Coseno del angulo\n"
    "sin_theta = dy / length           # Seno del angulo"
)

pdf.subtitulo("Paso 2: Calcular carga en longitud real")
pdf.codigo(
    "q_on_member = q_horizontal * abs(dx) / length\n"
    "# La carga por metro horizontal se distribuye sobre la\n"
    "# longitud real inclinada del elemento"
)

pdf.subtitulo("Paso 3: Carga global (vertical hacia abajo)")
pdf.codigo(
    "load_global_x = 0.0        # No hay carga horizontal\n"
    "load_global_y = -q_on_member  # Negativo = hacia abajo"
)

pdf.subtitulo("Paso 4: Rotacion global -> local")
pdf.codigo(
    "load_local_x =  load_global_x * cos_theta + load_global_y * sin_theta\n"
    "load_local_y = -load_global_x * sin_theta + load_global_y * cos_theta"
)
pdf.nota(
    "Matriz de rotacion 2D:\n"
    "  [Fx']   [ cos  sin] [Fx]\n"
    "  [Fy'] = [-sin  cos] [Fy]\n"
    "Esto convierte fuerzas de coordenadas globales a locales del elemento."
)

pdf.subtitulo("Paso 5: Aplicar en OpenSees")
pdf.codigo(
    'ops.eleLoad("-ele", ele_tag, "-type", "-beamUniform",\n'
    "             load_local_y, load_local_x)"
)
pdf.nota("Nota: eleLoad recibe primero la componente perpendicular (corte), luego la axial.")

pdf.subtitulo("Paso 6: Retornar carga total")
pdf.codigo("return q_horizontal * abs(dx)  # Carga total en N para verificar equilibrio")

# ===================== PAGINA 5: NODOS Y APOYOS =====================
pdf.add_page()
pdf.titulo("4. NODOS, APOYOS Y ROTULA")

pdf.subtitulo("Crear modelo")
pdf.codigo(
    "ops.wipe()\n"
    'ops.model("basic", "-ndm", 2, "-ndf", 3)'
)
pdf.nota("wipe() limpia todo. model() crea un modelo nuevo 2D con 3 GDL/nodo.")

pdf.subtitulo("Nodos")
pdf.codigo(
    "ops.node(1, 0.0, 0.0)    # A  - apoyo izquierdo\n"
    "ops.node(2, 4.0, 3.0)    # B  - nodo intermedio\n"
    "ops.node(3, 6.5, 3.0)    # C  - izquierda de rotula\n"
    "ops.node(4, 6.5, 3.0)    # C  - derecha de rotula (MISMA posicion)\n"
    "ops.node(5, 9.0, 3.0)    # D  - nodo intermedio\n"
    "ops.node(6, 13.0, 0.0)   # E  - apoyo derecho"
)
pdf.nota(
    "PREGUNTA CLAVE: Por que 2 nodos en C?\n"
    "Respuesta: Para modelar la rotula interna. Los 2 nodos estan en la misma "
    "posicion pero tienen rotaciones independientes. Esto permite que no se "
    "transmita momento flector a traves de C."
)

pdf.subtitulo("Apoyos (condiciones de frontera)")
pdf.codigo(
    "ops.fix(1, 1, 1, 0)   # A: restringe ux=1, uy=1, rz=0 (articula)\n"
    "ops.fix(6, 1, 1, 0)   # E: restringe ux=1, uy=1, rz=0 (articula)"
)
pdf.nota(
    "1 = restringido (fijo), 0 = libre.\n"
    "Articula: no permite traslacion, pero si rotacion.\n"
    "El marco tiene 2 articulas + 1 rotula interna = isostatico."
)

pdf.subtitulo("Rotula interna")
pdf.codigo("ops.equalDOF(3, 4, 1, 2)")
pdf.nota(
    "equalDOF(nodo_master, nodo_slave, DOF1, DOF2)\n"
    "Iguala los DOF 1 (ux) y 2 (uy) entre los nodos 3 y 4.\n"
    "El DOF 3 (rz) NO se iguala -> cada lado rota independiente.\n"
    "Resultado: se transmite fuerza axial y corte, pero NO momento."
)

# ===================== PAGINA 6: ELEMENTOS =====================
pdf.add_page()
pdf.titulo("5. ELEMENTOS Y TRANSFORMACION")

pdf.subtitulo("Transformacion geometrica")
pdf.codigo('ops.geomTransf("Linear", 1)')
pdf.nota(
    "Linear = sin considerar grandes deformaciones.\n"
    "El tag 1 se reutiliza para todos los elementos (todos usan la misma transformacion)."
)

pdf.subtitulo("Elementos viga-columna elasticos")
pdf.codigo(
    "ops.element('elasticBeamColumn', tag, nodo_i, nodo_j,\n"
    "             area, E, I, geomTransf)\n"
    "\n"
    "# Elemento 1: A-B\n"
    "ops.element('elasticBeamColumn', 1, 1, 2, area, E, Iz, 1)\n"
    "# Elemento 2: B-C (termina en nodo 3 = C izquierda)\n"
    "ops.element('elasticBeamColumn', 2, 2, 3, area, E, Iz, 1)\n"
    "# Elemento 3: C-D (empieza en nodo 4 = C derecha)\n"
    "ops.element('elasticBeamColumn', 3, 4, 5, area, E, Iz, 1)\n"
    "# Elemento 4: D-E\n"
    "ops.element('elasticBeamColumn', 4, 5, 6, area, E, Iz, 1)"
)
pdf.nota(
    "PREGUNTA CLAVE: Por que el elemento 3 empieza en nodo 4 y no en 3?\n"
    "Respuesta: Porque en C hay rotula. El elemento BC termina en nodo 3 "
    "y el CD empieza en nodo 4. Al tener equalDOF, comparten "
    "desplazamientos pero no rotacion."
)

# ===================== PAGINA 7: CARGAS Y ANALISIS =====================
pdf.add_page()
pdf.titulo("6. CARGAS Y ANALISIS")

pdf.subtitulo("Definir patron de carga")
pdf.codigo(
    'ops.timeSeries("Linear", 1)  # La carga se aplica en 1 paso\n'
    'ops.pattern("Plain", 1, 1)   # Patron de carga usando la serie 1'
)

pdf.subtitulo("Aplicar carga distribuida en cada elemento")
pdf.codigo(
    "total_load = 0.0\n"
    "total_load += add_vertical_load_on_horizontal_projection(1, 1, 2, q)\n"
    "total_load += add_vertical_load_on_horizontal_projection(2, 2, 3, q)\n"
    "total_load += add_vertical_load_on_horizontal_projection(3, 4, 5, q)\n"
    "total_load += add_vertical_load_on_horizontal_projection(4, 5, 6, q)"
)
pdf.nota("Se acumula el total de carga para verificar equilibrio: sum(Fy) = 0")

pdf.subtitulo("Configurar el analisis")
pdf.codigo(
    'ops.system("BandGeneral")        # Matriz de rigidez banda\n'
    'ops.numberer("RCM")              # Numeracion Reverse Cuthill-McKee\n'
    'ops.constraints("Transformation") # Manejo de equalDOF\n'
    'ops.integrator("LoadControl", 1.0) # 1 paso, factor 1.0\n'
    'ops.algorithm("Linear")           # Sin iteracion\n'
    'ops.analysis("Static")            # Estatico, no dinamico'
)

pdf.subtitulo("Ejecutar")
pdf.codigo(
    "result = ops.analyze(1)     # 1 paso de analisis\n"
    "if result != 0:             # Si falla...\n"
    "    raise RuntimeError(...) # ...lanza error"
)
pdf.nota("analyze(1) resuelve K*u = F. Si la matriz es singular o no converge, retorna != 0.")

# ===================== PAGINA 8: RESULTADOS =====================
pdf.add_page()
pdf.titulo("7. LEER RESULTADOS")

pdf.subtitulo("Reacciones en apoyos")
pdf.codigo(
    "ops.reactions()  # Calcula reacciones\n"
    "\n"
    "R_Ax = ops.nodeReaction(1, 1)  # Reaccion horizontal en A\n"
    "R_Ay = ops.nodeReaction(1, 2)  # Reaccion vertical en A\n"
    "R_Ex = ops.nodeReaction(6, 1)  # Reaccion horizontal en E\n"
    "R_Ey = ops.nodeReaction(6, 2)  # Reaccion vertical en E"
)
pdf.nota(
    "nodeReaction(nodo, DOF)\n"
    "DOF 1 = horizontal (ux), DOF 2 = vertical (uy), DOF 3 = momento (rz)"
)

pdf.subtitulo("Fuerzas internas de cada elemento")
pdf.codigo(
    "local_forces = {ele: ops.eleResponse(ele, 'localForce')\n"
    "                for ele in range(1, 5)}\n"
    "\n"
    "# localForce retorna: [Ni, Vi, Mi, Nj, Vj, Mj]\n"
    "# N = axial, V = corte, M = momento\n"
    "# Subscript i = nodo inicial, j = nodo final"
)

pdf.subtitulo("Encontrar maximos")
pdf.codigo(
    "# Mayor fuerza axial\n"
    "max_axial = max(abs(f[0]) for f in local_forces.values())\n"
    "\n"
    "# Mayor corte (compara ambos extremos de cada elemento)\n"
    "max_shear = max(max(abs(f[1]), abs(f[4])) for f in local_forces.values())\n"
    "\n"
    "# Mayor momento\n"
    "max_moment = max(max(abs(f[2]), abs(f[5])) for f in local_forces.values())"
)

pdf.subtitulo("Calcular tensiones")
pdf.codigo(
    "sigma_flexion = max_moment / Wz     # sigma = M/W (flexion)\n"
    "sigma_axial   = max_axial / A       # sigma = N/A (axial)\n"
    "\n"
    "# Corte maximo (Jouravsky)\n"
    "tau = max_shear * S/(I*t)  # S/(I*t) = 0.0004028 1/mm2 de la pauta"
)

# ===================== PAGINA 9: VALIDACION =====================
pdf.add_page()
pdf.titulo("8. VALIDACION CONTRA LA PAUTA")

pdf.subtitulo("Valores de referencia (pauta)")
pdf.codigo(
    "R_Ay = R_Ey = 19.5 tonf\n"
    "|R_Ax| = |R_Ex| = 21.13 tonf\n"
    "|N|max = 28.6 tonf\n"
    "|Q|max = 7.5 tonf\n"
    "|M|max = 9.38 tonf*m\n"
    "sigma flexion = 80.511 MPa\n"
    "tau max = 29.6 MPa"
)

pdf.subtitulo("Verificacion de equilibrio")
pdf.codigo(
    "vertical   = R_Ay + R_Ey - total_load   # Debe ser 0\n"
    "horizontal = R_Ax + R_Ex                  # Debe ser 0"
)

pdf.subtitulo("Assertions (validacion automatica)")
pdf.codigo(
    "# Equilibrio\n"
    "assert isclose(horizontal_residual, 0, abs_tol=1e-7)\n"
    "assert isclose(vertical_residual, 0, abs_tol=1e-7)\n"
    "\n"
    "# Reacciones contra pauta\n"
    "assert isclose(R_Ay_tonf, 19.5, abs_tol=1e-9)\n"
    "assert isclose(R_Ey_tonf, 19.5, abs_tol=1e-9)\n"
    "assert isclose(|R_Ax|, 21.13, abs_tol=0.01)\n"
    "assert isclose(|R_Ex|, 21.13, abs_tol=0.01)\n"
    "\n"
    "# Fuerzas internas contra pauta\n"
    "assert isclose(|N|max, 28.6, abs_tol=0.1)\n"
    "assert isclose(|Q|max, 7.5, abs_tol=0.1)\n"
    "assert isclose(|M|max, 9.38, abs_tol=0.02)"
)
pdf.nota(
    "Si algun assert falla, el script aborta con AssertionError.\n"
    "Esto garantiza que los resultados son correctos."
)

pdf.subtitulo("Resultados esperados")
pdf.codigo(
    "R_Ax = 21.125 tonf\n"
    "R_Ay = 19.500 tonf\n"
    "R_Ex = -21.125 tonf\n"
    "R_Ey = 19.500 tonf\n"
    "|N|max = 28.600 tonf\n"
    "|Q|max = 7.500 tonf\n"
    "|M|max = 9.375 tonf*m\n"
    "Estado: OK"
)

# ===================== PAGINA 10: PREGUNTAS CLAVE =====================
pdf.add_page()
pdf.titulo("9. PREGUNTAS QUE TE PUEDEN HACER")

pdf.sub2("1. Que es OpenSeesPy?")
pdf.texto(
    "Es un wrapper de Python para OpenSees, un programa de analisis "
    "estructural desarrollado en UC Berkeley. Resuelve K*u = F "
    "para estructuras lineales y no lineales."
)

pdf.sub2("2. Que significan ndm=2 y ndf=3?")
pdf.texto(
    "ndm=2: modelo en 2 dimensiones (plano).\n"
    "ndf=3: cada nodo tiene 3 grados de libertad: ux (horizontal), "
    "uy (vertical), rz (rotacion fuera del plano)."
)

pdf.sub2("3. Para que sirve equalDOF?")
pdf.texto(
    "Iguala grados de libertad entre dos nodos. Se usa para modelar "
    "la rotula interna: los nodos comparten ux y uy, pero no rz. "
    "Asi no se transmite momento a traves de C."
)

pdf.sub2("4. Que es elasticBeamColumn?")
pdf.texto(
    "Un elemento viga-columna con comportamiento lineal elastico. "
    "Responde a fuerza axial, corte y momento flector. "
    "Requiere: area, modulo elastico E, inercia I, y transformacion."
)

pdf.sub2("5. Que es geomTransf Linear?")
pdf.texto(
    "Define como se calculan las deformaciones del elemento. "
    "Linear =small strains, sin actualizar geometria. "
    "Es suficiente para analisis lineal elastico."
)

pdf.sub2("6. Que hace eleLoad?")
pdf.texto(
    "Aplica una carga distribuida sobre un elemento. "
    "-beamUniform significa carga uniforme. "
    "Se ingresa en coordenadas LOCALES del elemento."
)

pdf.sub2("7. Por que la carga se convierte a locales?")
pdf.texto(
    "El enunciado dice '3 tonf/m sobre proyeccion horizontal'. "
    "Pero los elementos estan inclinados. OpenSees recibe la carga "
    "en ejes locales, asi que hay que rotar la carga global "
    "a componentes local_x (axial) y local_y (perpendicular)."
)

pdf.sub2("8. Que es localForce?")
pdf.texto(
    "Retorna las fuerzas internas de un elemento en sus ejes locales:\n"
    "[Ni, Vi, Mi, Nj, Vj, Mj]\n"
    "N = axial, V = corte, M = momento en cada extremo (i y j)."
)

pdf.sub2("9. Que es un marco isostatico?")
pdf.texto(
    "Una estructura determinada estaticamente: se puede resolver "
    "con ecuaciones de equilibrio sin necesitar compatibilidad. "
    "Tiene 3 ecuaciones de equilibrio y 3 incognitas de reaccion "
    "(o equivalentes). La rotula interna reduce la indeterminacion."
)

pdf.sub2("10. Que es la verificacion?")
pdf.texto(
    "Comparamos los resultados de OpenSees contra la pauta del profesor. "
    "Si coinciden dentro de tolerancia, el modelo es correcto. "
    "Las assertions automatizan esta verificacion."
)

# ===================== PAGINA 11: COMANDOS =====================
pdf.add_page()
pdf.titulo("10. COMANDOS UTILES")

pdf.subtitulo("Ejecutar el script")
pdf.codigo("python opensees/p1l0/ejemplo_minimo_2d.py")

pdf.subtitulo("Ejecutar desde VS Code")
pdf.codigo("Abrir terminal con Ctrl+` y pegar el comando anterior")

pdf.subtitulo("Instalar dependencias")
pdf.codigo(
    "python -m pip install openseespy\n"
    "python -m pip install matplotlib\n"
    "python -m pip install fpdf2"
)

pdf.subtitulo("Git:Actualizar repositorio")
pdf.codigo(
    "git pull              # Bajar cambios del grupo\n"
    "git add .             # Seleccionar todos los cambios\n"
    'git commit -m "msg"   # Guardar cambios localmente\n'
    "git push              # Subir a GitHub"
)

pdf.subtitulo("Ubicacion de archivos")
pdf.codigo(
    "opensees/p1l0/ejemplo_minimo_2d.py  # El script\n"
    "results/p1l0/diagrama_pregunta_2.png # El diagrama\n"
    "docs/p1l0-explicacion.md            # La explicacion\n"
    "docs/p1l0-pregunta-2-control-1.md   # Ejercicio base\n"
    "AGENTS.md                           # Reglas para IA"
)

pdf.subtitulo("Estructura del marco (recordar)")
pdf.codigo(
    "A(0,0) -> B(4,3) -> C(6.5,3) -> D(9,3) -> E(13,0)\n"
    "\n"
    "  B _________ C ___________ D\n"
    "  /           |              \\\n"
    " /            | (rotula)      \\\n"
    "A                           E\n"
    "\n"
    "Apoyos: A = articula, E = articula\n"
    "Carga: q = 3 tonf/m vertical"
)

# Guardar
output = "C:/Users/josel/OneDrive/Escritorio/MCOC/MCOC-grupo1/docs/P1L0_explicacion_codigo.pdf"
pdf.output(output)
print(f"PDF guardado en: {output}")
