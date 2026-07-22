import os
from datetime import datetime

from mysql.connector import Error

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image
)

from database.conexion import get_connection


class NumberedCanvas(canvas.Canvas):
    """
    Canvas personalizado para calcular el total de páginas y dibujar
    el pie de página (con numeración dinámicamente) en dos pasadas.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#555555"))

        # Pie de página (Izquierda: Nombre del Hospital, Derecha: Páginas)
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        texto_izq = f"Hospital Militar — Generado: {fecha_actual}"
        texto_der = f"Página {self._pageNumber} de {page_count}"

        self.drawString(1.5 * cm, 0.8 * cm, texto_izq)
        self.drawRightString(26.4 * cm, 0.8 * cm, texto_der)

        # Línea divisoria inferior
        self.setStrokeColor(colors.HexColor("#CCCCCC"))
        self.setLineWidth(0.5)
        self.line(1.5 * cm, 1.2 * cm, 26.4 * cm, 1.2 * cm)

        self.restoreState()


def exportar_equipos_pdf():
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                e.id_equipo,
                e.nombre_equipo,
                td.nombre AS tipo,
                d.nombre AS departamento,
                e.marca,
                e.modelo,
                est.nombre AS estado
            FROM tbl_equipo e
            INNER JOIN tbl_tipo_dispositivo td
                ON td.id_tipo = e.id_tipo
            INNER JOIN tbl_departamento d
                ON d.id_departamento = e.id_departamento
            INNER JOIN tbl_estado est
                ON est.id_estado = e.id_estado
            WHERE e.id_estado <> 6
            ORDER BY e.nombre_equipo
        """)

        equipos = cursor.fetchall()

        # Configuración de carpeta y archivo de salida
        carpeta = "exports"
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)

        archivo_pdf = os.path.join(carpeta, "Reporte_Equipos.pdf")

        # Configuración del documento PDF (Horizontal / Landscape)
        documento = SimpleDocTemplate(
            archivo_pdf,
            pagesize=landscape(letter),
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.8 * cm
        )

        estilos = getSampleStyleSheet()

        # --- ESTILOS PERSONALIZADOS ---
        titulo_estilo = ParagraphStyle(
            "TituloSIGIP",
            parent=estilos["Title"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#003366")
        )

        estilo_celda = ParagraphStyle(
            'CeldaTabla',
            parent=estilos['Normal'],
            fontSize=8,
            leading=10,
            alignment=TA_LEFT
        )

        estilo_encabezado = ParagraphStyle(
            'EncabezadoTabla',
            parent=estilos['Normal'],
            fontSize=9,
            leading=11,
            textColor=colors.white,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER
        )

        contenido = []

        # --- ENCABEZADO / CABECERA ---
        logo_path = os.path.join("assets", "hospital_logo.png")

        titulo_texto = """
        <b>HOSPITAL MILITAR</b><br/>
        <font size=10 color="#555555">SIGIP - Sistema de Gestión de Direcciones IP</font><br/>
        <font size=12 color="#003366"><b>REPORTE GENERAL DE EQUIPOS</b></font>
        """
        paragraph_titulo = Paragraph(titulo_texto, titulo_estilo)

        if os.path.exists(logo_path):
            imagen_logo = Image(logo_path, width=2.3 * cm, height=2.3 * cm)
            header_table = Table(
                [[imagen_logo, paragraph_titulo]],
                colWidths=[2.8 * cm, 22.1 * cm]
            )
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ]))
            contenido.append(header_table)
        else:
            contenido.append(paragraph_titulo)

        contenido.append(Spacer(1, 0.6 * cm))

        # --- CONSTRUCCIÓN DE LA TABLA ---
        datos = [[
            Paragraph("ID", estilo_encabezado),
            Paragraph("Equipo", estilo_encabezado),
            Paragraph("Tipo", estilo_encabezado),
            Paragraph("Departamento", estilo_encabezado),
            Paragraph("Marca", estilo_encabezado),
            Paragraph("Modelo", estilo_encabezado),
            Paragraph("Estado", estilo_encabezado)
        ]]

        estilos_tabla = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F9F9F9")),
        ]

        # Cargar datos y aplicar color dinámico al estado
        for idx, equipo in enumerate(equipos, start=1):
            estado_texto = str(equipo["estado"] or "").strip().upper()

            if estado_texto == "ACTIVO":
                color_estado = colors.HexColor("#D4EDDA")  # Verde claro
            elif estado_texto == "INACTIVO":
                color_estado = colors.HexColor("#F8D7DA")  # Rojo claro
            elif estado_texto == "MANTENIMIENTO":
                color_estado = colors.HexColor("#FFF3CD")  # Amarillo claro
            else:
                color_estado = colors.white

            estilos_tabla.append(
                ("BACKGROUND", (6, idx), (6, idx), color_estado)
            )

            datos.append([
                Paragraph(str(equipo["id_equipo"]), estilo_celda),
                Paragraph(str(equipo["nombre_equipo"] or ""), estilo_celda),
                Paragraph(str(equipo["tipo"] or ""), estilo_celda),
                Paragraph(str(equipo["departamento"] or ""), estilo_celda),
                Paragraph(str(equipo["marca"] or "-"), estilo_celda),
                Paragraph(str(equipo["modelo"] or "-"), estilo_celda),
                Paragraph(estado_texto, estilo_celda)
            ])

        tabla = Table(
            datos,
            repeatRows=1,  # Repite el encabezado si se extiende a más páginas
            colWidths=[
                1.3 * cm,  # ID
                5.1 * cm,  # Equipo
                3.8 * cm,  # Tipo
                4.7 * cm,  # Departamento
                3.3 * cm,  # Marca
                3.3 * cm,  # Modelo
                3.4 * cm   # Estado
            ]
        )
        tabla.setStyle(TableStyle(estilos_tabla))

        contenido.append(tabla)

        # Construir el documento PDF con numeración de páginas
        documento.build(contenido, canvasmaker=NumberedCanvas)
        return archivo_pdf

    except Error as e:
        raise Exception(f"Error al consultar la base de datos: {str(e)}")
    except Exception as e:
        raise Exception(f"Error al generar el PDF: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()