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
    el pie de página (con numeración dinámica) en dos pasadas.
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


def exportar_ips_pdf():
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                ip.direccion_ip AS direccion,
                seg.nombre AS segmento,
                est.nombre AS estado,
                (
                    SELECT eq.nombre_equipo
                    FROM tbl_asignacion_ip asig
                    LEFT JOIN tbl_equipo eq
                        ON eq.id_equipo = asig.id_equipo
                    WHERE asig.id_ip = ip.id_ip
                      AND asig.fecha_liberacion IS NULL
                    ORDER BY asig.fecha_asignacion DESC
                    LIMIT 1
                ) AS equipo
            FROM tbl_ip ip
            LEFT JOIN tbl_segmento seg
                ON seg.id_segmento = ip.id_segmento
            LEFT JOIN tbl_estado est
                ON est.id_estado = ip.id_estado
            WHERE ip.id_estado IN (3, 4, 5)
            ORDER BY ip.direccion_ip ASC
        """)

        ips = cursor.fetchall()

        # Configuración de carpeta y archivo de salida local
        carpeta = "exports"
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)

        archivo_pdf = os.path.join(carpeta, "Reporte_Direcciones_IP.pdf")

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

        estilo_celda_centro = ParagraphStyle(
            'CeldaTablaCentro',
            parent=estilos['Normal'],
            fontSize=8,
            leading=10,
            alignment=TA_CENTER
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
        # Ruta estándar compatible con el módulo de Equipos
        logo_path = os.path.join("assets", "hospital_logo.png")

        titulo_texto = """
        <b>HOSPITAL MILITAR</b><br/>
        <font size=10 color="#555555">SIGIP - Sistema de Gestión de Direcciones IP</font><br/>
        <font size=12 color="#003366"><b>REPORTE GENERAL DE DIRECCIONES IP</b></font>
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
            Paragraph("Dirección IP", estilo_encabezado),
            Paragraph("Segmento", estilo_encabezado),
            Paragraph("Estado", estilo_encabezado),
            Paragraph("Equipo", estilo_encabezado)
        ]]

        estilos_tabla = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
        ]

        # Cargar datos e incorporar intercalado de colores en filas
        for idx, ip in enumerate(ips, start=1):
            bg_color = colors.HexColor("#FFFFFF") if idx % 2 != 0 else colors.HexColor("#F9F9F9")
            estilos_tabla.append(("BACKGROUND", (0, idx), (-1, idx), bg_color))

            datos.append([
                Paragraph(str(ip["direccion"] or ""), estilo_celda_centro),
                Paragraph(str(ip["segmento"] or ""), estilo_celda),
                Paragraph(str(ip["estado"] or ""), estilo_celda_centro),
                Paragraph(str(ip["equipo"] or "-"), estilo_celda),
            ])

        # Ancho total utilizable para la hoja Horizontal (24.9 cm)
        tabla = Table(
            datos,
            repeatRows=1,  # Repite el encabezado si se extiende a más páginas
            colWidths=[
                5.0 * cm,   # Dirección IP
                5.0 * cm,   # Segmento
                3.5 * cm,   # Estado
                11.4 * cm,  # Equipo
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
            try:
                cursor.close()
            except Exception:
                pass
        if conexion and conexion.is_connected():
            try:
                conexion.close()
            except Exception:
                pass