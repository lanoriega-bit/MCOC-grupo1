"""Genera un PDF con la explicacion del codigo P1L1 benchmark 3D para la defensa."""

from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "MCOC-grupo1 | P1L1 - Explicacion Benchmark 3D", align="R")
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
pdf.titulo("P1L1 - Benchmark 3D\nOpenSeesPy")
pdf.ln(10)
pdf.set_font("Helvetica", "", 12)
pdf.cell(0, 8, "Sector P1L1-S01: pano idealizado entre ejes F-G y 2-3", align="C")
pdf.ln(6)
pdf.cell(0, 8, "Semana 1 - Laboratorio de Analisis Estructural 3D", align="C")
pdf.ln(15)
pdf.set_font("Helvetica", "", 11)
pdf.cell(0, 7, "Grupo: MCOC-grupo1", align="C")
pdf.ln(6)
pdf.cell(0, 7, "Curso: Analisis Estructural", align="C")
pdf.ln(6)
pdf.cell(0, 7, "Fecha de entrega: Jueves 27 de agosto 2026", align="C")
pdf.ln(20)
pdf.linea()
pdf.set_font("Helvetica", "I", 10)
pdf.cell(0, 7, "Documento generado con ayuda de OpenCode (IA)", align="C")

# ===================== PAGINA 2: QUE MODELAMOS =====================
pdf.add_page()
pdf.titulo("1. QUE MODELAMOS")
pdf.subtitulo("Objetivo")
pdf.texto(
    "Construir y verificar un caso estructural 3D propuesto por el grupo. "
    "Se trata de un marco tridimensional de al menos un vano en cada direccion, "
    "con losa cuya carga se descarga sobre las vigas por areas tributarias."
)

pdf.subtitulo("Sector escogido: P1L1-S01")
pdf.texto(
    "Se modela el pano idealizado entre ejes F-G y 2-3 del edificio. "
    "Es una zona repetitiva y facil de verificar antes de pasar al edificio completo."
)

pdf.subtitulo("Geometria")
pdf.codigo(
    "Lx = 6.0 m  (eje F -> G)\n"
    "Ly = 4.0 m  (eje 2 -> 3)\n"
    "H  = 3.0 m  (altura del nivel)\n"
    "A_losa = 6.0 * 4.0 = 24.0 m2"
)

pdf.subtitulo("Nodos")
pdf.codigo(
    "1 = F2 base   = (0, 0, 0)     5 = F2 sup  = (0, 0, 3)\n"
    "2 = G2 base   = (6, 0, 0)     6 = G2 sup  = (6, 0, 3)\n"
    "3 = G3 base   = (6, 4, 0)     7 = G3 sup  = (6, 4, 3)\n"
    "4 = F3 base   = (0, 4, 0)     8 = F3 sup  = (0, 4, 3)"
)

pdf.subtitulo("Secciones")
pdf.codigo(
    "Columnas P. 70x70:  A = 0.49 m2, Iy = Iz = 0.00496 m4\n"
    "Vigas V. 60/80:     A = 0.48 m2, Iy = 0.0256 m4, Iz = 0.0144 m4"
)

pdf.subtitulo("Material")
pdf.codigo(
    "E = 25 GPa (concreto)\n"
    "v = 0.20\n"
    "G = E / (2*(1+v)) = 10.42 GPa"
)

pdf.subtitulo("Apoyos")
pdf.texto(
    "Los 4 nodos de base (1,2,3,4) estan empotrados:\n"
    "fix(node, 1, 1, 1, 1, 1, 1)  -> restringe los 6 GDL\n"
    "Esto significa que no hay desplazamiento ni rotacion en base."
)

pdf.subtitulo("Carga de losa")
pdf.texto(
    "La losa NO se modela con elementos finitos. Se transfiere su carga "
    "a las vigas mediante areas tributarias:"
)
pdf.codigo(
    "qG = 7.35 kN/m2 (250+200+300 kgf/m2 aprox.)\n"
    "P_total = 7.35 * 24.0 = 176.4 kN\n"
    "A_trib_por_viga = 24.0 / 4 = 6.0 m2\n"
    "Vigas de 6m: w = 7.35 * 6 / 6 = 7.35 kN/m\n"
    "Vigas de 4m: w = 7.35 * 6 / 4 = 11.025 kN/m\n"
    "Verificacion: 2*(7.35*6) + 2*(11.025*4) = 176.4 kN"
)

# ===================== PAGINA 3: IMPORTACIONES =====================
pdf.add_page()
pdf.titulo("2. IMPORTACIONES Y CONSTANTES")

pdf.subtitulo("Librerias")
pdf.codigo(
    "from __future__ import annotations  # Tipos modernos\n"
    "import csv                          # Exportar CSV\n"
    "import json                         # Exportar JSON\n"
    "import math                         # hypot, sqrt\n"
    "from pathlib import Path            # Rutas de archivos\n"
    "import matplotlib                   # Graficos\n"
    'matplotlib.use("Agg")              # Sin pantalla\n'
    "import matplotlib.pyplot as plt     # Interfaz de graficos\n"
    "import openseespy.opensees as ops   # Motor de analisis\n"
    "from mpl_toolkits.mplot3d import Axes3D  # Proyeccion 3D"
)

pdf.subtitulo("Constantes de conversion")
pdf.codigo(
    "KN  = 1_000.0      # 1 kN = 1000 N\n"
    "MPA = 1.0e6        # 1 MPa = 1e6 Pa"
)

pdf.subtitulo("Funciones auxiliares")
pdf.codigo(
    "def kN(value_newton):\n"
    "    return value_newton / KN\n"
    "\n"
    "def kN_m(value_newton_meter):\n"
    "    return value_newton_meter / KN"
)

pdf.nota(
    "Razon: OpenSees trabaja en SI (m, N, Pa). Las funciones kN() y kN_m() "
    "convierten los resultados para imprimir valores legibles."
)

# ===================== PAGINA 4: rectangular_section =====================
pdf.add_page()
pdf.titulo("3. FUNCION: rectangular_section()")

pdf.subtitulo("Que hace")
pdf.texto(
    "Calcula propiedades elasticas de una seccion rectangular: "
    "area (A), inercia respecto a eje Y (Iy), inercia respecto a eje Z (Iz), "
    "y constante de torsion (J)."
)

pdf.subtitulo("Codigo")
pdf.codigo(
    "def rectangular_section(width, height):\n"
    "    area = width * height\n"
    "    iy = width * height**3 / 12.0\n"
    "    iz = height * width**3 / 12.0\n"
    "    torsion_j = iy + iz\n"
    "    return {'A': area, 'Iy': iy, 'Iz': iz, 'J': torsion_j}"
)

pdf.subtitulo("Que significan Iy e Iz")
pdf.texto(
    "Iy = inercia para flexion alrededor del eje local Y.\n"
    "Iz = inercia para flexion alrededor del eje local Z.\n\n"
    "Para una viga de 0.60 x 0.80 m:\n"
    "  Iy = 0.60 * 0.80^3 / 12 = 0.0256 m4  (flexion fuerte)\n"
    "  Iz = 0.80 * 0.60^3 / 12 = 0.0144 m4  (flexion debil)\n\n"
    "Para una columna de 0.70 x 0.70 m:\n"
    "  Iy = Iz = 0.70^4 / 12 = 0.0196 m4  (simetrica)"
)

pdf.subtitulo("Resultados")
pdf.codigo(
    "column = rectangular_section(0.70, 0.70)\n"
    "# A=0.49, Iy=0.0196, Iz=0.0196, J=0.0392\n"
    "\n"
    "beam = rectangular_section(0.60, 0.80)\n"
    "# A=0.48, Iy=0.0256, Iz=0.0144, J=0.04"
)

# ===================== PAGINA 5: FUNCIONES VECTORIALES =====================
pdf.add_page()
pdf.titulo("4. FUNCIONES VECTORIALES 3D")

pdf.subtitulo("unit() - Normalizar vector")
pdf.codigo(
    "def unit(vector):\n"
    "    norm = sqrt(sum(v*v for v in vector))\n"
    "    return tuple(v / norm for v in vector)"
)
pdf.nota("Convierte cualquier vector a longitud 1. Necesario para ejes locales.")

pdf.subtitulo("cross() - Producto cruz")
pdf.codigo(
    "def cross(a, b):\n"
    "    return (a[1]*b[2] - a[2]*b[1],\n"
    "            a[2]*b[0] - a[0]*b[2],\n"
    "            a[0]*b[1] - a[1]*b[0])"
)
pdf.nota("Producto cruz: calcula un vector perpendicular a dos vectores dados.")

pdf.subtitulo("local_axes() - Ejes locales del elemento")
pdf.codigo(
    "def local_axes(start, end, vecxz):\n"
    "    local_x = unit(end - start)       # Eje X = elem_i -> elem_j\n"
    "    local_y = unit(cross(vecxz, x))   # Eje Y perpendicular a X y vecxz\n"
    "    local_z = unit(cross(x, y))       # Eje Z completa la terna\n"
    "    return local_x, local_y, local_z"
)

pdf.subtitulo("Que es geomTransf y vecxz")
pdf.texto(
    "geomTransf define la transformacion geometrica del elemento:\n"
    "como se mapean las coordenadas locales a globales.\n\n"
    "vecxz es un vector auxiliar que define la orientacion. "
    "Dice 'hacia donde apunta el eje Z local' (o un vector en el plano XZ local).\n\n"
    "Columnas: vecxz = (1, 0, 0) -> eje Z local apunta en X global\n"
    "Vigas:    vecxz = (0, 0, 1) -> eje Z local apunta en Z global"
)

# ===================== PAGINA 6: add_beam_gravity_load =====================
pdf.add_page()
pdf.titulo("5. FUNCION: add_beam_gravity_load()")

pdf.subtitulo("Que hace")
pdf.texto(
    "Aplica una carga distribuida vertical sobre un elemento viga 3D. "
    "Usa eleLoad con tipo -beamUniform en coordenadas locales."
)

pdf.subtitulo("Codigo")
pdf.codigo(
    "def add_beam_gravity_load(ele_tag, line_load):\n"
    "    ops.eleLoad('-ele', ele_tag, '-type',\n"
    "               '-beamUniform', 0.0, -line_load, 0.0)\n"
    "    return 0.0, 0.0, -line_load"
)

pdf.subtitulo("Argumentos de -beamUniform")
pdf.texto(
    "eleLoad -beamUniform recibe 3 componentes en LOCALES:\n"
    "  wy = carga perpendicular en eje Y local (corte)\n"
    "  wz = carga perpendicular en eje Z local (vertical para vigas)\n"
    "  wx = carga axial\n\n"
    "Para carga gravitacional vertical en vigas horizontales:\n"
    "  wy = 0, wz = -line_load (negativo = hacia abajo), wx = 0"
)

pdf.subtitulo("Carga tributaria")
pdf.codigo(
    "slab_area = lx * ly = 6.0 * 4.0 = 24.0 m2\n"
    "q_g = 7.35 kN/m2\n"
    "tributary_area_per_beam = 24.0 / 4 = 6.0 m2\n"
    "\n"
    "Vigas en X (6m): w = 7.35 * 6 / 6 = 7.35 kN/m\n"
    "Vigas en Y (4m): w = 7.35 * 6 / 4 = 11.025 kN/m"
)

# ===================== PAGINA 7: NODOS Y APOYOS =====================
pdf.add_page()
pdf.titulo("6. NODOS, APOYOS Y MODELO")

pdf.subtitulo("Crear modelo 3D")
pdf.codigo(
    "ops.wipe()\n"
    'ops.model("basic", "-ndm", 3, "-ndf", 6)'
)
pdf.nota(
    "ndm = 3: modelo tridimensional.\n"
    "ndf = 6: cada nodo tiene 6 grados de libertad.\n"
    "Los 6 GDL son: ux, uy, uz, rx, ry, rz"
)

pdf.subtitulo("Los 6 GDL (grados de libertad)")
pdf.codigo(
    "DOF 1 = ux  (traslacion horizontal X)\n"
    "DOF 2 = uy  (traslacion horizontal Y)\n"
    "DOF 3 = uz  (traslacion vertical Z)\n"
    "DOF 4 = rx  (rotacion alrededor de X)\n"
    "DOF 5 = ry  (rotacion alrededor de Y)\n"
    "DOF 6 = rz  (rotacion alrededor de Z)"
)

pdf.subtitulo("Crear nodos")
pdf.codigo(
    "for node, coords in nodes.items():\n"
    "    ops.node(node, *coords)"
)

pdf.subtitulo("Fijar apoyos")
pdf.codigo(
    "for node in (1, 2, 3, 4):\n"
    "    ops.fix(node, 1, 1, 1, 1, 1, 1)"
)
pdf.nota(
    "fix(nodo, 1,1,1,1,1,1) = empotrado: los 6 GDL estan restringidos.\n"
    "No hay ni traslacion ni rotacion en la base.\n"
    "Los nodos superiores (5,6,7,8) estan libres."
)

# ===================== PAGINA 8: TRANSFORMACIONES =====================
pdf.add_page()
pdf.titulo("7. TRANSFORMACIONES GEOMETRICAS")

pdf.subtitulo("Definicion")
pdf.codigo(
    'ops.geomTransf("Linear", 1, 1.0, 0.0, 0.0)  # Columnas\n'
    'ops.geomTransf("Linear", 2, 0.0, 0.0, 1.0)  # Vigas'
)

pdf.subtitulo("Que es geomTransf")
pdf.texto(
    "geomTransf define la transformacion geometrica de un elemento:\n"
    "como se relacionan los ejes locales del elemento con el sistema global.\n\n"
    "Linear = sin actualizar geometria (small strains).\n"
    "Es suficiente para analisis lineal elastico."
)

pdf.subtitulo("Que es el vector vecxz")
pdf.texto(
    "El tercer argumento es un vector auxiliar que define la orientacion.\n"
    "Dice 'hacia donde apunta el eje Z local' o un vector en el plano XZ.\n\n"
    "Columnas (tag 1): vecxz = (1, 0, 0)\n"
    "  -> eje Z local apunta en direccion X global\n"
    "  -> eje Y local queda perpendicular\n\n"
    "Vigas (tag 2): vecxz = (0, 0, 1)\n"
    "  -> eje Z local apunta en direccion Z global (vertical)\n"
    "  -> eje Y local queda perpendicular"
)

pdf.subtitulo("Diferencia local vs global")
pdf.texto(
    "Global: coordenadas del modelo completo (X, Y, Z).\n"
    "Local: coordenadas de cada elemento (x, y, z).\n\n"
    "El eje local x siempre va del nodo i al nodo j.\n"
    "Los ejes local y y local z dependen de geomTransf.\n\n"
    "Las fuerzas localForce se reportan en ejes LOCALES.\n"
    "Para convertir a globales, se usa la transformacion inversa."
)

# ===================== PAGINA 9: ELEMENTOS =====================
pdf.add_page()
pdf.titulo("8. ELEMENTOS elasticBeamColumn")

pdf.subtitulo("Sintaxis 3D")
pdf.codigo(
    "ops.element('elasticBeamColumn', tag, ni, nj,\n"
    "             A, E, G, J, Iy, Iz, transfTag)"
)

pdf.subtitulo("Parametros")
pdf.texto(
    "tag = identificador unico del elemento\n"
    "ni, nj = nodos inicial y final\n"
    "A = area de la seccion\n"
    "E = modulo elastico\n"
    "G = modulo de corte\n"
    "J = constante de torsion\n"
    "Iy = inercia para flexion sobre eje Y local\n"
    "Iz = inercia para flexion sobre eje Z local\n"
    "transfTag = tag de la geomTransf a usar"
)

pdf.subtitulo("Por que Iy e Iz son diferentes en vigas?")
pdf.texto(
    "Una viga rectangular 60x80 es mas alta que ancha.\n"
    "  Iy = b*h^3/12 = 0.60*0.80^3/12 = 0.0256 m4 (flexion fuerte)\n"
    "  Iz = h*b^3/12 = 0.80*0.60^3/12 = 0.0144 m4 (flexion debil)\n\n"
    "Iy > Iz porque es mas dificil doblar la viga por su lado alto."
)

pdf.subtitulo("Elementos del modelo")
pdf.codigo(
    "Columnas (1-4): elasticBeamColumn ... 1  # transf 1\n"
    "Vigas (5-8):    elasticBeamColumn ... 2  # transf 2"
)

# ===================== PAGINA 10: CARGAS Y ANALISIS =====================
pdf.add_page()
pdf.titulo("9. CARGAS Y ANALISIS")

pdf.subtitulo("Patron de carga")
pdf.codigo(
    'ops.timeSeries("Linear", 1)  # Carga se aplica en 1 paso\n'
    'ops.pattern("Plain", 1, 1)   # Patron usando la serie 1'
)

pdf.subtitulo("Aplicar cargas en vigas")
pdf.codigo(
    "uniform_loads[5] = add_beam_gravity_load(5, line_load_x)  # viga eje 2\n"
    "uniform_loads[7] = add_beam_gravity_load(7, line_load_x)  # viga eje 3\n"
    "uniform_loads[6] = add_beam_gravity_load(6, line_load_y)  # viga eje G\n"
    "uniform_loads[8] = add_beam_gravity_load(8, line_load_y)  # viga eje F"
)

pdf.subtitulo("Configurar analisis")
pdf.codigo(
    'ops.system("BandGeneral")         # Matriz de rigidez banda\n'
    'ops.numberer("RCM")               # Numeracion RCM\n'
    'ops.constraints("Transformation") # Manejo de restricciones\n'
    'ops.integrator("LoadControl", 1.0) # 1 paso\n'
    'ops.algorithm("Linear")            # Sin iteracion\n'
    'ops.analysis("Static")             # Estatico'
)

pdf.subtitulo("Ejecutar")
pdf.codigo(
    "result = ops.analyze(1)\n"
    "if result != 0:\n"
    "    raise RuntimeError('OpenSees no convergio')"
)
pdf.nota(
    "analyze(1) resuelve K*u = F para 1 paso de carga.\n"
    "Si converge, result = 0. Si falla, result != 0."
)

pdf.subtitulo("Que esta resolviendo OpenSees?")
pdf.texto(
    "OpenSees ensambla la matriz de rigidez global K a partir de "
    "las rigideces de cada elemento (basado en A, E, G, J, Iy, Iz).\n"
    "Luego resuelve: K * u = F\n"
    "  K = matriz de rigidez global\n"
    "  u = vector de desplazamientos nodales (incognita)\n"
    "  F = vector de cargas\n\n"
    "Una vez que tiene u, calcula las fuerzas internas de cada elemento."
)

# ===================== PAGINA 11: RESULTADOS =====================
pdf.add_page()
pdf.titulo("10. LEER RESULTADOS")

pdf.subtitulo("Reacciones")
pdf.codigo(
    "ops.reactions()\n"
    "\n"
    "reactions = {\n"
    "    node: tuple(ops.nodeReaction(node, dof) for dof in (1,2,3))\n"
    "    for node in (1, 2, 3, 4)\n"
    "}"
)

pdf.subtitulo("Desplazamientos")
pdf.codigo(
    "displacements = {\n"
    "    node: tuple(ops.nodeDisp(node, dof) for dof in (1,2,3))\n"
    "    for node in nodes\n"
    "}"
)

pdf.subtitulo("Fuerzas locales (3D)")
pdf.codigo(
    "local_forces = {ele: ops.eleResponse(ele, 'localForce')\n"
    "                for ele in elements}"
)
pdf.nota(
    "En 3D, localForce retorna 12 valores por elemento:\n"
    "[Ni, Vyi, Vzi, Ti, Myi, Mzi, Nj, Vyj, Vzj, Tj, Myj, Mzj]\n"
    "N = axial, V = corte, M = momento, T = torsion\n"
    "Subscript i = nodo inicial, j = nodo final"
)

pdf.subtitulo("Desplazamiento maximo superior")
pdf.codigo(
    "max_top_uz = max(abs(displacements[node][2])\n"
    "                 for node in (5,6,7,8))\n"
    "# Resultado: -1.080e-05 m (compresion de columna)"
)

# ===================== PAGINA 12: DIAGRAMAS NVM =====================
pdf.add_page()
pdf.titulo("11. DIAGRAMAS DE ESFUERZOS INTERNOS")

pdf.subtitulo("element_diagram_values()")
pdf.texto(
    "Para cada elemento, calcula N, V y M en 81 estaciones "
    "a lo largo de su longitud usando equilibrio local."
)

pdf.subtitulo("Ecuaciones de equilibrio")
pdf.codigo(
    "# Axial:\n"
    "N(x) = Ni + wx * x\n"
    "\n"
    "# Cortante:\n"
    "Vy(x) = Vyi + wy * x\n"
    "Vz(x) = Vzi + wz * x\n"
    "Vres = sqrt(Vy^2 + Vz^2)\n"
    "\n"
    "# Momento (integrando cortes):\n"
    "My(x) = Myi + Vzi*x + 0.5*wz*x^2\n"
    "Mz(x) = Mzi - Vyi*x - 0.5*wy*x^2\n"
    "Mres = sqrt(My^2 + Mz^2)"
)

pdf.subtitulo("Por que no interpolar linealmente?")
pdf.texto(
    "En vigas con carga distribuida, el momento es parabolico, "
    "no lineal. Si solo interpolamos entre extremos, perderiamos "
    "el valor maximo interior. Por eso se calcula por estaciones "
    "usando las ecuaciones de equilibrio."
)

pdf.subtitulo("Cierre de diagramas")
pdf.texto(
    "El script verifica que los diagramas cierren correctamente: "
    "el valor en el nodo j debe coincidir con la fuerza de "
    "extremo j reportada por OpenSees. Si hay error grande, "
    "el modelo tiene un problema."
)

# ===================== PAGINA 13: VERIFICACION =====================
pdf.add_page()
pdf.titulo("12. VERIFICACION")

pdf.subtitulo("Equilibrio vertical")
pdf.codigo(
    "total_reaction_z = sum(reactions[n][2] for n in (1,2,3,4))\n"
    "vertical_residual = total_reaction_z - total_slab_load\n"
    "\n"
    "# Debe ser ~0:\n"
    "assert isclose(vertical_residual, 0, abs_tol=1e-6)"
)

pdf.subtitulo("Reacciones por columna")
pdf.codigo(
    "expected = total_slab_load / 4 = 176.4 / 4 = 44.1 kN\n"
    "# Cada columna debe tomar ~44.1 kN:\n"
    "assert isclose(reactions[n][2], 44.1, abs_tol=1e-5)"
)

pdf.subtitulo("Tabla de verificacion")
pdf.codigo(
    "Magnitud                        Referencia    OpenSees\n"
    "----------------------------------------------------\n"
    "Suma cargas verticales          -176.400 kN    -176.400 kN\n"
    "Suma reacciones verticales       176.400 kN     176.400 kN\n"
    "Reaccion por columna              44.100 kN      44.100 kN\n"
    "Axial columna elem 1              44.100 kN      44.100 kN\n"
    "Max N global diagrama             44.100 kN      44.100 kN\n"
    "Max Vres global diagrama          22.050 kN      22.050 kN\n"
    "Max Mres global diagrama          19.250 kN*m    19.250 kN*m\n"
    "Despl. vertical superior        -1.080e-05 m  -1.080e-05 m\n"
    "Cierre diagramas fuerza                0 kN      0.000e+00 kN\n"
    "Cierre diagramas momento           0 kN*m     1.091e-14 kN*m"
)

pdf.subtitulo("Por que converger no significa estar correcto?")
pdf.texto(
    "OpenSees puede converger (result=0) incluso con errores en:\n"
    "- Signo de cargas (carga hacia arriba en vez de abajo)\n"
    "- Unidades incorrectas (mm en vez de m)\n"
    "- Apoyos mal definidos (liberados sin querer)\n"
    "- Secciones incorrectas\n\n"
    "Por eso SIEMPRE hay que comparar contra valores de referencia "
    "manuales o de otro programa. El equilibrio es necesario pero no suficiente."
)

# ===================== PAGINA 14: PREGUNTAS CLAVE =====================
pdf.add_page()
pdf.titulo("13. PREGUNTAS PARA LA DEFENSA")

pdf.sub2("1. Que son los 6 GDL de un nodo 3D?")
pdf.texto(
    "Los 6 grados de libertad representan los movimientos posibles:\n"
    "- 3 traslaciones: ux (X), uy (Y), uz (Z)\n"
    "- 3 rotaciones: rx (alrededor de X), ry (alrededor de Y), rz (alrededor de Z)\n"
    "En 2D solo hay 3 (ux, uy, rz). En 3D hay 6."
)

pdf.sub2("2. Que representa geomTransf?")
pdf.texto(
    "Define como se calculan las deformaciones del elemento.\n"
    "Linear = pequenas deformaciones, sin actualizar geometria.\n"
    "Incluye un vector auxiliar (vecxz) que fija la orientacion "
    "de los ejes locales Y y Z del elemento."
)

pdf.sub2("3. Diferencia local vs global?")
pdf.texto(
    "Global: sistema de coordenadas del modelo completo (X, Y, Z).\n"
    "Local: sistema de coordenadas de cada elemento (x, y, z).\n"
    "El eje local x siempre va del nodo i al nodo j.\n"
    "Las fuerzas localForce se reportan en ejes locales."
)

pdf.sub2("4. Que representa Iy e Iz?")
pdf.texto(
    "Iy = inercia para flexion alrededor del eje local Y.\n"
    "Iz = inercia para flexion alrededor del eje local Z.\n"
    "Para una viga 60x80: Iy > Iz porque es mas dificil "
    "doblar por su lado alto."
)

pdf.sub2("5. Que esta resolviendo OpenSees?")
pdf.texto(
    "Resuelve K*u = F:\n"
    "- K: matriz de rigidez global (ensamblada de cada elemento)\n"
    "- u: vector de desplazamientos nodales (incognita)\n"
    "- F: vector de cargas\n"
    "Con u conocido, calcula fuerzas internas de cada elemento."
)

pdf.sub2("6. Por que converger no es suficiente?")
pdf.texto(
    "OpenSees puede converger con errores de:\n"
    "- Signos de carga invertidos\n"
    "- Unidades inconsistentes\n"
    "- Apoyos mal definidos\n"
    "- Secciones incorrectas\n"
    "Siempre hay que verificar equilibrio, unidades y comparar "
    "contra valores de referencia."
)

# ===================== PAGINA 15: COMANDOS =====================
pdf.add_page()
pdf.titulo("14. COMANDOS UTILES")

pdf.subtitulo("Ejecutar el script")
pdf.codigo(
    "cd entregas/p1l1_benchmark_3d\n"
    "python opensees/benchmark_3d.py"
)

pdf.subtitulo("Ejecutar desde VS Code")
pdf.codigo("Abrir terminal con Ctrl+` y pegar el comando anterior")

pdf.subtitulo("Instalar dependencias")
pdf.codigo(
    "python -m pip install openseespy\n"
    "python -m pip install matplotlib\n"
    "python -m pip install fpdf2"
)

pdf.subtitulo("Git")
pdf.codigo(
    "git pull              # Bajar cambios del grupo\n"
    "git add .             # Seleccionar todos los cambios\n"
    'git commit -m "msg"   # Guardar cambios localmente\n'
    "git push              # Subir a GitHub"
)

pdf.subtitulo("Ubicacion de archivos")
pdf.codigo(
    "entregas/p1l1_benchmark_3d/\n"
    "  opensees/benchmark_3d.py              # El script\n"
    "  results/geometria_deformada_ejes.png   # Geometria 3D\n"
    "  results/diagramas_nvm_3d.png           # Diagramas NVM\n"
    "  results/fuerzas_elementos.csv          # Fuerzas locales\n"
    "  results/diagramas_nvm_3d_valores.csv   # Valores por estacion\n"
    "  results/verificacion.json              # Chequeos\n"
    "  docs/semana01.md                       # Informe\n"
    "  docs/P1L1_explicacion_codigo.pdf       # Este PDF"
)

# Guardar
output = "C:/Users/josel/OneDrive/Escritorio/MCOC/MCOC-grupo1/entregas/p1l1_benchmark_3d/docs/P1L1_explicacion_codigo.pdf"
pdf.output(output)
print(f"PDF guardado en: {output}")
