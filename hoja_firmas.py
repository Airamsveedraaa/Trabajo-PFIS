import csv
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm


def leer_csv(ruta: str) -> list[dict]:
    """Lee el CSV y devuelve lista de dicts con Nombre y Apellidos."""
    alumnos = []
    with open(ruta, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            nombre = row['Nombre'].strip()
            apellidos = row[' Apellido(s)'].strip()
            alumnos.append({'nombre': nombre, 'apellidos': apellidos})
    return alumnos


def ordenar_alumnos(alumnos: list[dict]) -> list[dict]:
    """Ordena los alumnos alfabéticamente por nombre."""
    return sorted(alumnos, key=lambda a: a['nombre'].lower())


def agrupar_en_grupos(alumnos: list[dict], tamanyo: int = 8) -> list[list[dict]]:
    """Agrupa los alumnos en grupos de tamanyo."""
    return [alumnos[i:i + tamanyo] for i in range(0, len(alumnos), tamanyo)]


def _build_group_table(grupo, grupo_num, num_grupos, col_widths, row_h_data):
    """Construye una tabla para un grupo individual."""
    c_head  = colors.HexColor('#2c3e50')
    c_col   = colors.HexColor('#34495e')
    c_par   = colors.HexColor('#ecf0f1')
    c_grid  = colors.HexColor('#bdc3c7')
    c_box   = colors.HexColor('#2c3e50')

    datos = [[f'Grupo {grupo_num} de {num_grupos}', '', '', '', ''],
             ['#', 'Nombre', 'Apellidos', 'Lunes', 'Jueves']]
    st = [
        ('SPAN', (0,0), (-1,0)),
        ('BACKGROUND', (0,0), (-1,0), c_head), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 6.5),
        ('ALIGN', (0,0), (-1,0), 'LEFT'), ('LEFTPADDING', (0,0), (-1,0), 3),
        ('TOPPADDING', (0,0), (-1,0), 1), ('BOTTOMPADDING', (0,0), (-1,0), 1),
        ('BACKGROUND', (0,1), (-1,1), c_col), ('TEXTCOLOR', (0,1), (-1,1), colors.white),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'), ('FONTSIZE', (0,1), (-1,1), 6),
        ('ALIGN', (0,1), (-1,1), 'CENTER'),
        ('TOPPADDING', (0,1), (-1,1), 1), ('BOTTOMPADDING', (0,1), (-1,1), 1),
    ]

    base = (grupo_num-1)*8
    for j, a in enumerate(grupo):
        r = j+2
        datos.append([str(base+j+1), a['nombre'], a['apellidos'], '', ''])
        if j%2==1: st.append(('BACKGROUND', (0,r), (-1,r), c_par))
        st += [
            ('FONTNAME', (0,r), (-1,r), 'Helvetica'), ('FONTSIZE', (0,r), (-1,r), 6),
            ('ALIGN', (0,r), (0,r), 'CENTER'), ('ALIGN', (1,r), (2,r), 'LEFT'),
            ('ALIGN', (3,r), (-1,r), 'CENTER'),
            ('TOPPADDING', (0,r), (-1,r), 0), ('BOTTOMPADDING', (0,r), (-1,r), 0),
            ('LEFTPADDING', (1,r), (2,r), 2),
        ]

    rh = [0.38*cm, 0.33*cm] + [row_h_data]*len(grupo)
    t = Table(datos, colWidths=col_widths, rowHeights=rh)
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.3, c_grid),
        ('BOX', (0,0), (-1,-1), 0.6, c_box),
    ] + st))
    return t


def generar_pdf(alumnos: list[dict], ruta_salida: str = 'hoja_firmas.pdf'):
    """Genera el PDF de hoja de firmas con todos los grupos en una sola página."""
    page_size = landscape(A4)
    margin = 0.5*cm

    doc = SimpleDocTemplate(
        ruta_salida, pagesize=page_size,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin, bottomMargin=margin
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('titulo', parent=styles['Title'], fontSize=10, spaceAfter=0.1*cm)

    alumnos_ordenados = ordenar_alumnos(alumnos)
    grupos = agrupar_en_grupos(alumnos_ordenados, 8)
    num_grupos = len(grupos)

    # 3 grupos por fila: 9 grupos -> 3 filas de 3
    # Landscape A4 usable: ~28.7cm
    # Cada sub-tabla: #(0.4), Nombre(2.3), Apellidos(2.8), Lunes(2.1), Jueves(2.1) = 9.7cm
    # 3 * 9.7 = 29.1cm -> un poco justo, ajustar a 9.5 cada una
    col_widths = [0.38*cm, 2.2*cm, 2.7*cm, 2.0*cm, 2.0*cm]  # total 9.28cm
    row_h_data = 0.55*cm
    subtable_w = sum(col_widths)  # 9.28cm
    sep = 0.2*cm

    story = [Paragraph("Hoja de Firmas — Curso PFIS", titulo_style)]

    # Agrupar de 3 en 3
    filas = [grupos[i:i+3] for i in range(0, num_grupos, 3)]
    nums  = [list(range(i+1, min(i+4, num_grupos+1))) for i in range(0, num_grupos, 3)]

    for fila, ns in zip(filas, nums):
        tablas = [_build_group_table(fila[k], ns[k], num_grupos, col_widths, row_h_data)
                  for k in range(len(fila))]
        # Pad to 3 columns
        while len(tablas) < 3:
            tablas.append('')

        outer = Table([tablas], colWidths=[subtable_w + sep]*3, hAlign='LEFT')
        outer.setStyle(TableStyle([
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), sep),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(outer)
        story.append(Spacer(1, 0.08*cm))

    doc.build(story)
    print(f"PDF generado: {ruta_salida}")


if __name__ == '__main__':
    ruta_csv = 'pokemons_participantes_curso.csv'
    alumnos = leer_csv(ruta_csv)
    generar_pdf(alumnos, 'hoja_firmas.pdf')
