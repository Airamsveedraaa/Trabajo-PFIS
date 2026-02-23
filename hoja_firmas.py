import csv
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak
)
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


def generar_pdf(alumnos: list[dict], ruta_salida: str = 'hoja_firmas.pdf'):
    """Genera el PDF de hoja de firmas."""
    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'titulo',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=0.3*cm
    )
    subtitulo_style = ParagraphStyle(
        'subtitulo',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=0.5*cm,
        textColor=colors.grey
    )

    alumnos_ordenados = ordenar_alumnos(alumnos)
    grupos = agrupar_en_grupos(alumnos_ordenados, 8)

    story = []

    for i, grupo in enumerate(grupos):
        # Encabezado
        story.append(Paragraph("Hoja de Firmas — Curso PFIS", titulo_style))
        story.append(Paragraph(f"Grupo {i + 1} de {len(grupos)}", subtitulo_style))
        story.append(Spacer(1, 0.3*cm))

        # Cabecera de la tabla
        cabecera = ['#', 'Nombre', 'Apellidos', 'Lunes', 'Jueves']
        datos = [cabecera]

        for j, alumno in enumerate(grupo, start=1):
            datos.append([
                str((i * 8) + j),
                alumno['nombre'],
                alumno['apellidos'],
                '',  # firma lunes
                '',  # firma jueves
            ])

        # Anchos de columna
        anchos = [1*cm, 4.5*cm, 5*cm, 4.5*cm, 4.5*cm]

        tabla = Table(datos, colWidths=anchos, rowHeights=[1*cm] + [1.5*cm] * len(grupo))
        tabla.setStyle(TableStyle([
            # Cabecera
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Filas de datos
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (1, 1), (2, -1), 'LEFT'),
            ('ALIGN', (3, 1), (-1, -1), 'CENTER'),
            # Alternar color de filas
            *[('BACKGROUND', (0, r), (-1, r), colors.HexColor('#ecf0f1'))
              for r in range(2, len(grupo) + 1, 2)],
            # Bordes
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2c3e50')),
            # Padding
            ('LEFTPADDING', (1, 1), (2, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        story.append(tabla)

        if i < len(grupos) - 1:
            story.append(PageBreak())

    doc.build(story)
    print(f"PDF generado: {ruta_salida}")


if __name__ == '__main__':
    ruta_csv = 'pokemons_participantes_curso.csv'
    alumnos = leer_csv(ruta_csv)
    generar_pdf(alumnos, 'hoja_firmas.pdf')
