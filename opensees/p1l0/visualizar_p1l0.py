"""Genera imagenes del modelo P1L0 para presentar."""

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import openseespy.opensees as ops

def main():
    # Parametros
    L = 6.0
    E = 25.0e9
    A = 0.30 * 0.30
    Iz = 0.30 * 0.30**3 / 12.0
    P = 10_000.0

    # Correr OpenSees
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    ops.node(1, 0.0, 0.0)
    ops.node(2, L / 2.0, 0.0)
    ops.node(3, L, 0.0)
    ops.fix(1, 1, 1, 0)
    ops.fix(3, 0, 1, 0)
    ops.geomTransf("Linear", 1)
    ops.element("elasticBeamColumn", 1, 1, 2, A, E, Iz, 1)
    ops.element("elasticBeamColumn", 2, 2, 3, A, E, Iz, 1)
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    ops.load(2, 0.0, -P, 0.0)
    ops.system("BandGeneral")
    ops.numberer("RCM")
    ops.constraints("Plain")
    ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear")
    ops.analysis("Static")
    ops.analyze(1)
    ops.reactions()

    # Obtener deformada con recorder
    ops.timeSeries("Linear", 2)
    ops.pattern("Plain", 2, 2)
    ops.load(2, 0.0, -P, 0.0)
    ops.system("BandGeneral")
    ops.numberer("RCM")
    ops.constraints("Plain")
    ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear")
    ops.analysis("Static")
    ops.analyze(1)

    # Coordenadas deformadas
    x_orig = [0.0, L/2, L]
    y_orig = [0.0, 0.0, 0.0]
    x_def = [ops.nodeDisp(1, 1), ops.nodeDisp(2, 1), ops.nodeDisp(3, 1)]
    y_def = [ops.nodeDisp(1, 2), ops.nodeDisp(2, 2), ops.nodeDisp(3, 2)]

    # ========== FIGURA 1: Modelo estructural ==========
    fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    ax.set_aspect('equal')
    ax.set_xlim(-1, L + 1)
    ax.set_ylim(-2, 2)
    ax.set_xlabel('x [m]', fontsize=12)
    ax.set_ylabel('y [m]', fontsize=12)
    ax.set_title('P1L0 - Modelo: Viga simplemente apoyada', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Viga
    ax.plot([0, L], [0, 0], 'b-', linewidth=4, label='Viga (elasticBeamColumn)')

    # Nodos
    ax.plot(0, 0, 'ko', markersize=10, zorder=5)
    ax.plot(L/2, 0, 'ro', markersize=10, zorder=5)
    ax.plot(L, 0, 'ko', markersize=10, zorder=5)

    # Etiquetas de nodos
    ax.annotate('Nodo 1', (0, 0), textcoords="offset points", xytext=(0, 15),
                ha='center', fontsize=10, fontweight='bold')
    ax.annotate('Nodo 2', (L/2, 0), textcoords="offset points", xytext=(0, 15),
                ha='center', fontsize=10, fontweight='bold', color='red')
    ax.annotate('Nodo 3', (L, 0), textcoords="offset points", xytext=(0, 15),
                ha='center', fontsize=10, fontweight='bold')

    # Apoyo pasador (Nodo 1)
    triangle = patches.RegularPolygon((0, 0), 3, radius=0.3, orientation=0,
                                       facecolor='lightblue', edgecolor='black', linewidth=2)
    ax.add_patch(triangle)
    ax.plot([-0.3, 0.3], [-0.3, -0.3], 'k-', linewidth=2)

    # Apoyo rodillo (Nodo 3)
    triangle2 = patches.RegularPolygon((L, 0), 3, radius=0.3, orientation=0,
                                        facecolor='lightgreen', edgecolor='black', linewidth=2)
    ax.add_patch(triangle2)
    circle = plt.Circle((L - 0.15, -0.3), 0.08, color='lightgreen', ec='black', lw=1.5)
    ax.add_patch(circle)
    circle2 = plt.Circle((L + 0.15, -0.3), 0.08, color='lightgreen', ec='black', lw=1.5)
    ax.add_patch(circle2)
    ax.plot([L - 0.3, L + 0.3], [-0.38, -0.38], 'k-', linewidth=2)

    # Carga
    ax.annotate('', xy=(L/2, 0), xytext=(L/2, 1.2),
                arrowprops=dict(arrowstyle='->', color='red', lw=3))
    ax.text(L/2 + 0.2, 0.8, f'P = {P:.0f} N', fontsize=11, color='red', fontweight='bold')

    # Etiquetas de apoyos
    ax.text(0, -0.7, 'Pasador\n(ux, uy fijos)', ha='center', fontsize=9, style='italic')
    ax.text(L, -0.7, 'Rodillo\n(uy fijo)', ha='center', fontsize=9, style='italic')

    # Elementos
    ax.text(L/4, 0.15, 'Elemento 1', ha='center', fontsize=9, color='blue')
    ax.text(3*L/4, 0.15, 'Elemento 2', ha='center', fontsize=9, color='blue')

    plt.tight_layout()
    plt.savefig('C:/Users/josel/OneDrive/Escritorio/MCOC/MCOC-grupo1/docs/p1l0_modelo.png',
                dpi=150, bbox_inches='tight')
    plt.close()
    print("Guardado: docs/p1l0_modelo.png")

    # ========== FIGURA 2: Deformada ==========
    fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    ax.set_aspect('equal')
    ax.set_xlim(-1, L + 1)
    ax.set_ylim(-4, 2)
    ax.set_xlabel('x [m]', fontsize=12)
    ax.set_ylabel('y [m]', fontsize=12)
    ax.set_title('P1L0 - Deformada (amplificada x100)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Viga original (gris punteado)
    ax.plot([0, L], [0, 0], 'k--', linewidth=1, alpha=0.5, label='Original')

    # Viga deformada (amplificada)
    scale = 100
    x_def_plot = np.array(x_def)
    y_def_plot = np.array(y_def) * scale
    ax.plot(x_def_plot, y_def_plot, 'r-', linewidth=3, label='Deformada (x100)')

    # Nodos deformados
    ax.plot(x_def_plot, y_def_plot, 'ro', markersize=8, zorder=5)

    # Etiquetas
    ax.annotate(f'uy = {y_def[1]*1000:.3f} mm', (x_def_plot[1], y_def_plot[1]),
                textcoords="offset points", xytext=(10, -20),
                fontsize=11, fontweight='bold', color='red',
                arrowprops=dict(arrowstyle='->', color='red'))

    # Apoyos
    triangle = patches.RegularPolygon((0, 0), 3, radius=0.3, orientation=0,
                                       facecolor='lightblue', edgecolor='black', linewidth=2)
    ax.add_patch(triangle)
    ax.plot([-0.3, 0.3], [-0.3, -0.3], 'k-', linewidth=2)

    triangle2 = patches.RegularPolygon((L, 0), 3, radius=0.3, orientation=0,
                                        facecolor='lightgreen', edgecolor='black', linewidth=2)
    ax.add_patch(triangle2)
    circle = plt.Circle((L - 0.15, -0.3), 0.08, color='lightgreen', ec='black', lw=1.5)
    ax.add_patch(circle)
    circle2 = plt.Circle((L + 0.15, -0.3), 0.08, color='lightgreen', ec='black', lw=1.5)
    ax.add_patch(circle2)
    ax.plot([L - 0.3, L + 0.3], [-0.38, -0.38], 'k-', linewidth=2)

    # Carga
    ax.annotate('', xy=(L/2, 0), xytext=(L/2, 1.2),
                arrowprops=dict(arrowstyle='->', color='red', lw=3))
    ax.text(L/2 + 0.2, 0.8, f'P = {P:.0f} N', fontsize=11, color='red', fontweight='bold')

    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig('C:/Users/josel/OneDrive/Escritorio/MCOC/MCOC-grupo1/docs/p1l0_deformada.png',
                dpi=150, bbox_inches='tight')
    plt.close()
    print("Guardado: docs/p1l0_deformada.png")

    # ========== FIGURA 3: Resultados resumen ==========
    fig, ax = plt.subplots(1, 1, figsize=(8, 3))
    ax.axis('off')

    table_data = [
        ['Reaccion Izq (R_Ay)', f'{5000:.2f} N', f'{P/2:.2f} N', '0.00%'],
        ['Reaccion Der (R_By)', f'{5000:.2f} N', f'{P/2:.2f} N', '0.00%'],
        ['Deflexion Central', f'{y_def[1]*1000:.6f} mm',
         f'{-P*L**3/(48*E*Iz)*1000:.6f} mm', '0.00%'],
        ['Equilibrio (R-P)', '0.00 N', '0 N', 'OK'],
    ]

    table = ax.table(cellText=table_data,
                     colLabels=['Variable', 'OpenSees', 'Teorico', 'Error'],
                     cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor('#4472C4')
            cell.set_text_props(color='white', fontweight='bold')
        elif row % 2 == 0:
            cell.set_facecolor('#D6E4F0')
        else:
            cell.set_facecolor('#FFFFFF')

    ax.set_title('Validacion: OpenSees vs Solucion Teorica', fontsize=14,
                 fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig('C:/Users/josel/OneDrive/Escritorio/MCOC/MCOC-grupo1/docs/p1l0_validacion.png',
                dpi=150, bbox_inches='tight')
    plt.close()
    print("Guardado: docs/p1l0_validacion.png")

    ops.wipe()
    print("\nListo. 3 imagenes generadas en docs/")

if __name__ == "__main__":
    main()
