from io import BytesIO
from datetime import datetime

from database.conexion import get_connection
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from mysql.connector import Error
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from procedures.bitacoramodulo import registrar_bitacora


# ==========================================
# LISTAR ASIGNACIONES
# ==========================================

def obtener_asignaciones(page: int = 1):
    """
    Obtiene únicamente las direcciones IP que se encuentran asignadas.
    """

    if page < 1:
        page = 1

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        page_size = 10
        offset = (page - 1) * page_size

        consulta_sql = """
            SELECT
                ai.id_asignacion AS id,
                ip.direccion_ip AS ip_direccion,
                e.nombre_equipo AS equipo_nombre,
                ai.fecha_asignacion,
                ai.fecha_liberacion,
                ai.id_estado,
                est.nombre AS estado,

                CASE
                    WHEN ai.id_estado = 4 THEN TRUE
                    ELSE FALSE
                END AS activo

            FROM tbl_asignacion_ip ai

            INNER JOIN tbl_ip ip
                ON ai.id_ip = ip.id_ip

            INNER JOIN tbl_equipo e
                ON ai.id_equipo = e.id_equipo

            INNER JOIN tbl_estado est
                ON ai.id_estado = est.id_estado

            WHERE ai.id_estado = 4

            ORDER BY ai.id_asignacion DESC

            LIMIT %s, %s
        """

        cursor.execute(
            consulta_sql,
            (
                offset,
                page_size
            )
        )

        items = cursor.fetchall()

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM tbl_asignacion_ip
            WHERE id_estado = 4
        """)

        total = cursor.fetchone()["total"]

        pages = (total + page_size - 1) // page_size

        return {
            "items": items,
            "pages": pages,
            "total": total
        }

    except Error as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener asignaciones: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()

# ==========================================
# LIBERAR ASIGNACIÓN DE IP
# ==========================================

def liberar_asignacion(id_asignacion: int, id_usuario_actual: int):
    """
    Libera una dirección IP asignada.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # Buscar asignación
        cursor.execute("""
            SELECT
                ai.id_ip,
                ai.id_estado,
                ip.direccion_ip,
                eq.nombre_equipo
            FROM tbl_asignacion_ip ai
            INNER JOIN tbl_ip ip
            ON ip.id_ip = ai.id_ip
            INNER JOIN tbl_equipo eq
            ON eq.id_equipo = ai.id_equipo
            WHERE ai.id_asignacion = %s
        """, (id_asignacion,))

        asignacion = cursor.fetchone()

        if not asignacion:
            raise HTTPException(
                status_code=404,
                detail="La asignación no existe."
            )

        # Verificar si ya está liberada
        if asignacion["id_estado"] == 3:
            raise HTTPException(
                status_code=400,
                detail="La asignación ya fue liberada."
            )

        # Actualizar asignación
        cursor.execute("""
            UPDATE tbl_asignacion_ip
            SET
                id_estado = 3,
                fecha_liberacion = NOW()
            WHERE id_asignacion = %s
        """, (id_asignacion,))

        # Actualizar IP
        cursor.execute("""
            UPDATE tbl_ip
            SET id_estado = 3
            WHERE id_ip = %s
        """, (asignacion["id_ip"],))

        conexion.commit()

        registrar_bitacora(
            id_usuario=id_usuario_actual,
            accion="LIBERAR",
            tabla_afectada="tbl_asignacion_ip",
            registro_id=id_asignacion,
            detalle=(
            f"Se liberó la dirección IP "
            f"'{asignacion['direccion_ip']}' "
            f"del equipo "
            f"'{asignacion['nombre_equipo']}'."
            )
        )

        return {
            "mensaje": "Dirección IP liberada correctamente."
        }

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al liberar la dirección IP: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()

# ==========================================
# COMBO EQUIPOS
# ==========================================

def obtener_equipos():

    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_equipo AS id,
                nombre_equipo AS nombre
            FROM tbl_equipo
            WHERE id_estado = 1
            ORDER BY nombre_equipo
        """)

        return cursor.fetchall()

    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        cursor.close()
        conexion.close()


# ==========================================
# COMBO SEGMENTOS
# ==========================================

def obtener_segmentos():

    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_segmento AS id,
                nombre
            FROM tbl_segmento
            WHERE id_estado = 1
            ORDER BY nombre
        """)

        return cursor.fetchall()

    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        cursor.close()
        conexion.close()

# ==========================================
# IPS DISPONIBLES
# ==========================================

def obtener_ips_disponibles(id_segmento):
    """
    Obtiene las IP disponibles de un segmento.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        print("ID SEGMENTO RECIBIDO:", id_segmento)

        cursor.execute("""
            SELECT
                id_ip AS id,
                direccion_ip AS direccion
            FROM tbl_ip
            WHERE id_segmento = %s
              AND id_estado = 3
            ORDER BY direccion_ip
        """, (id_segmento,))

        return cursor.fetchall()

    except Error as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener las IP disponibles: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()

# ==========================================
# EXPORTAR ASIGNACIONES A EXCEL
# ==========================================

def exportar_asignaciones_excel():
    conexion = get_connection()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                ai.id_asignacion AS id,
                ip.direccion_ip AS direccion_ip,
                e.nombre_equipo AS equipo_nombre,
                ai.fecha_asignacion,
                est.nombre AS estado
            FROM tbl_asignacion_ip ai
            INNER JOIN tbl_ip ip
                ON ai.id_ip = ip.id_ip
            INNER JOIN tbl_equipo e
                ON ai.id_equipo = e.id_equipo
            INNER JOIN tbl_estado est
                ON ai.id_estado = est.id_estado
            WHERE ai.id_estado = 4
            ORDER BY ai.fecha_asignacion DESC
        """)

        datos = cursor.fetchall()

        wb = Workbook()
        ws = wb.active
        ws.title = "Asignaciones"
        ws.sheet_view.showGridLines = False

        title_cell = ws.cell(row=1, column=1, value="Reporte de Asignaciones de IP")
        ws.merge_cells("A1:E1")
        title_cell.font = Font(bold=True, size=14, color="FFFFFF")
        title_cell.alignment = Alignment(horizontal="center", vertical="center")
        title_cell.fill = PatternFill("solid", fgColor="0A4B8F")
        ws.row_dimensions[1].height = 28

        subtitle_cell = ws.cell(row=2, column=1, value=f"Generado el {datetime.now():%d/%m/%Y %H:%M:%S}")
        ws.merge_cells("A2:E2")
        subtitle_cell.font = Font(size=10, italic=True, color="1F2937")
        subtitle_cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[2].height = 20

        encabezados = [
            "ID Asignación",
            "Dirección IP",
            "Equipo",
            "Fecha Asignación",
            "Estado"
        ]

        header_fill = PatternFill("solid", fgColor="D9E4F3")
        border = Border(
            left=Side(style="thin", color="BFC9D9"),
            right=Side(style="thin", color="BFC9D9"),
            top=Side(style="thin", color="BFC9D9"),
            bottom=Side(style="thin", color="BFC9D9")
        )

        for columna, texto in enumerate(encabezados, start=1):
            celda = ws.cell(row=4, column=columna, value=texto)
            celda.font = Font(bold=True, color="0A4B8F")
            celda.fill = header_fill
            celda.alignment = Alignment(horizontal="center", vertical="center")
            celda.border = border

        fila = 5
        for index, item in enumerate(datos, start=1):
            fila_fill = PatternFill("solid", fgColor="F3F6FB") if index % 2 == 0 else None

            ws.cell(row=fila, column=1, value=item["id"]).alignment = Alignment(vertical="center")
            ws.cell(row=fila, column=2, value=item["direccion_ip"]).alignment = Alignment(vertical="center")
            ws.cell(row=fila, column=3, value=item["equipo_nombre"]).alignment = Alignment(vertical="center")
            ws.cell(
                row=fila,
                column=4,
                value=item["fecha_asignacion"].strftime("%Y-%m-%d %H:%M:%S") if item["fecha_asignacion"] else ""
            ).alignment = Alignment(vertical="center")
            ws.cell(row=fila, column=5, value=item["estado"]).alignment = Alignment(vertical="center")

            for columna in range(1, 6):
                cell = ws.cell(row=fila, column=columna)
                cell.border = border
                if fila_fill is not None:
                    cell.fill = fila_fill

            fila += 1

        widths = [18, 22, 32, 24, 18]
        for columna, ancho_col in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(columna)].width = ancho_col

        ws.freeze_panes = "A5"

        archivo = BytesIO()
        wb.save(archivo)
        archivo.seek(0)

        return StreamingResponse(
            archivo,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=Reporte_Asignaciones_SIGIP.xlsx"
            }
        )

    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al exportar asignaciones: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            if cursor:
                cursor.close()
            conexion.close()

# ==========================================
# EXPORTAR ASIGNACIONES A PDF
# ==========================================

def exportar_asignaciones_pdf():
    conexion = get_connection()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                ai.id_asignacion AS id,
                ip.direccion_ip AS direccion_ip,
                e.nombre_equipo AS equipo_nombre,
                ai.fecha_asignacion,
                est.nombre AS estado
            FROM tbl_asignacion_ip ai
            INNER JOIN tbl_ip ip
                ON ai.id_ip = ip.id_ip
            INNER JOIN tbl_equipo e
                ON ai.id_equipo = e.id_equipo
            INNER JOIN tbl_estado est
                ON ai.id_estado = est.id_estado
            WHERE ai.id_estado = 4
            ORDER BY ai.fecha_asignacion DESC
        """)

        datos = cursor.fetchall()

        archivo = BytesIO()
        ancho, alto = letter
        pdf = canvas.Canvas(archivo, pagesize=letter)
        pdf.setTitle("Reporte de Asignaciones SIGIP")

        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        encabezados = ["ID", "Dirección IP", "Equipo", "Fecha Asignación", "Estado"]
        anchos = [50, 110, 170, 150, 80]
        x_inicio = 40
        y = alto - 90

        def dibujar_encabezado():
            pdf.setFillColor(colors.HexColor("#0A4B8F"))
            pdf.rect(0, alto - 70, ancho, 70, fill=1, stroke=0)
            pdf.setFillColor(colors.white)
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(40, alto - 44, "Reporte de Asignaciones de IP")
            pdf.setFont("Helvetica", 10)
            pdf.drawString(40, alto - 60, f"Fecha de generación: {fecha}")
            pdf.setFillColor(colors.white)
            pdf.setFont("Helvetica-Bold", 9)
            x = x_inicio
            for i, texto in enumerate(encabezados):
                pdf.rect(x, y - 16, anchos[i], 18, fill=1, stroke=0)
                pdf.setFillColor(colors.white)
                pdf.drawString(x + 4, y - 12, texto)
                x += anchos[i]
            pdf.setFillColor(colors.black)

        def dibujar_pie(pagina):
            pdf.setFont("Helvetica", 8)
            pdf.setFillColor(colors.grey)
            pdf.drawString(40, 40, f"SIGIP - Hospital Militar")
            pdf.drawRightString(ancho - 40, 40, f"Página {pagina}")

        pagina = 1
        dibujar_encabezado()
        pdf.setFont("Helvetica", 8)

        for item in datos:
            if y < 90:
                dibujar_pie(pagina)
                pdf.showPage()
                pagina += 1
                y = alto - 90
                dibujar_encabezado()
                pdf.setFont("Helvetica", 8)

            x = x_inicio
            fecha_asignacion = item["fecha_asignacion"].strftime("%Y-%m-%d %H:%M:%S") if item["fecha_asignacion"] else ""
            fila = [
                str(item["id"]),
                item["direccion_ip"],
                item["equipo_nombre"],
                fecha_asignacion,
                item["estado"]
            ]

            if pagina % 2 == 0:
                pdf.setFillColor(colors.HexColor("#F3F6FB"))
                pdf.rect(x_inicio, y - 18, sum(anchos), 18, fill=1, stroke=0)
                pdf.setFillColor(colors.black)

            for i, valor in enumerate(fila):
                pdf.drawString(x + 4, y - 12, str(valor))
                x += anchos[i]

            y -= 20
            pdf.setFillColor(colors.black)

        dibujar_pie(pagina)
        pdf.save()
        archivo.seek(0)

        return StreamingResponse(
            archivo,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=Reporte_Asignaciones_SIGIP.pdf"
            }
        )

    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al exportar asignaciones a PDF: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            if cursor:
                cursor.close()
            conexion.close()

# ==========================================
# ASIGNAR DIRECCIÓN IP
# ==========================================

def asignar_ip(id_ip: int, id_equipo: int, id_usuario: int, id_usuario_actual: int):
    """
    Asigna una dirección IP a un equipo.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # ======================================
        # Verificar que la IP exista
        # ======================================

        cursor.execute("""
            SELECT
                id_ip,
                direccion_ip,
                id_estado
            FROM tbl_ip
            WHERE id_ip = %s
        """, (id_ip,))

        ip = cursor.fetchone()

        if not ip:
            raise HTTPException(
                status_code=404,
                detail="La dirección IP no existe."
            )

        # Debe estar DISPONIBLE
        if ip["id_estado"] != 3:
            raise HTTPException(
                status_code=400,
                detail="La dirección IP no está disponible."
            )

        # ======================================
        # Verificar equipo
        # ======================================

        cursor.execute("""
            SELECT id_equipo, nombre_equipo
            FROM tbl_equipo
            WHERE id_equipo = %s
        """, (id_equipo,))

        equipo = cursor.fetchone()

        if not equipo:
            raise HTTPException(
                status_code=404,
                detail="El equipo no existe."
            )

        # ======================================
        # Verificar usuario
        # ======================================

        cursor.execute("""
            SELECT id_usuario
            FROM tbl_usuario
            WHERE id_usuario = %s
        """, (id_usuario,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="El usuario no existe."
            )

        # ======================================
        # Registrar asignación
        # ======================================

        cursor.execute("""
            INSERT INTO tbl_asignacion_ip
            (
                id_ip,
                id_equipo,
                id_usuario,
                fecha_asignacion,
                id_estado
            )
            VALUES
            (
                %s,
                %s,
                %s,
                NOW(),
                %s
            )
        """, (
            id_ip,
            id_equipo,
            id_usuario,
            4
        ))

        # ======================================
        # Cambiar estado de la IP
        # ======================================

        cursor.execute("""
            UPDATE tbl_ip
            SET id_estado = 4
            WHERE id_ip = %s
        """, (id_ip,))

        conexion.commit()

        registrar_bitacora(
            id_usuario=id_usuario_actual,
            accion="ASIGNAR",
            tabla_afectada="tbl_asignacion_ip",
            registro_id=cursor.lastrowid,
            detalle=(
            f"Se asignó la dirección IP "
            f"'{ip['direccion_ip']}' "
            f"al equipo "
            f"'{equipo['nombre_equipo']}'."
            )
        )

        return {
            "mensaje": "Dirección IP asignada correctamente."
        }

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al asignar la dirección IP: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()
    """
    Asigna una dirección IP a un equipo.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # ======================================
        # Verificar que la IP exista
        # ======================================

        cursor.execute("""
            SELECT
                id_ip,
                id_estado
            FROM tbl_ip
            WHERE id_ip = %s
        """, (id_ip,))

        ip = cursor.fetchone()

        if not ip:
            raise HTTPException(
                status_code=404,
                detail="La dirección IP no existe."
            )

        # id_estado = 3 -> DISPONIBLE
        if ip["id_estado"] != 3:
            raise HTTPException(
                status_code=400,
                detail="La dirección IP no está disponible."
            )

        # ======================================
        # Verificar que exista el equipo
        # ======================================

        cursor.execute("""
            SELECT id_equipo
            FROM tbl_equipo
            WHERE id_equipo = %s
        """, (id_equipo,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="El equipo no existe."
            )

        # ======================================
        # Verificar que exista el usuario
        # ======================================

        cursor.execute("""
            SELECT id_usuario
            FROM tbl_usuario
            WHERE id_usuario = %s
        """, (id_usuario,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="El usuario no existe."
            )

        # ======================================
        # Registrar asignación
        # ======================================

        cursor.execute("""
            INSERT INTO tbl_asignacion_ip
            (
                id_ip,
                id_equipo,
                id_usuario,
                fecha_asignacion,
                estado_asignacion
            )
            VALUES
            (
                %s,
                %s,
                %s,
                NOW(),
                'ACTIVA'
            )
        """, (
            id_ip,
            id_equipo,
            id_usuario
        ))

        # ======================================
        # Cambiar estado de la IP
        # id_estado = 4 -> ASIGNADA
        # ======================================

        cursor.execute("""
            UPDATE tbl_ip
            SET id_estado = 4
            WHERE id_ip = %s
        """, (id_ip,))

        conexion.commit()

        return {
            "mensaje": "Dirección IP asignada correctamente."
        }

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al asignar la dirección IP: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()


# ======================================
# IMPRIMIR EXEL
# ======================================

from io import BytesIO
from pathlib import Path
from datetime import datetime

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from mysql.connector import Error

from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.drawing.spreadsheet_drawing import (
    AnchorMarker,
    OneCellAnchor,
    XDRPositiveSize2D
)
from openpyxl.utils.units import pixels_to_EMU
from openpyxl.styles import (
    Font,
    PatternFill,
    Alignment,
    Border,
    Side
)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.page import PageMargins

from database.conexion import get_connection


def exportar_equipos_excel():
    conexion = get_connection()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                e.nombre_equipo,
                td.nombre AS tipo,
                e.marca,
                e.modelo,
                d.nombre AS departamento,
                est.nombre AS estado
            FROM tbl_equipo e
            INNER JOIN tbl_tipo_dispositivo td
                ON td.id_tipo = e.id_tipo
            INNER JOIN tbl_departamento d
                ON d.id_departamento = e.id_departamento
            INNER JOIN tbl_estado est
                ON est.id_estado = e.id_estado
            WHERE e.id_estado <> 6
            ORDER BY e.nombre_equipo ASC
        """)

        datos = cursor.fetchall()

        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte Equipos"
        ws.sheet_view.showGridLines = True

        azul = "0A4B8F"
        blanco = "FFFFFF"

        # --- ALINEACIÓN Y ESTRUCTURA DEL ENCABEZADO Y LOGO ---
        ws.column_dimensions["A"].width = 20

        # Ajuste de alturas para que el banner azul se vea simétrico con el logo
        ws.row_dimensions[1].height = 12
        ws.row_dimensions[2].height = 28
        ws.row_dimensions[3].height = 24
        ws.row_dimensions[4].height = 24
        ws.row_dimensions[5].height = 12

        # Combinar el espacio del logo A1:A4 y forzar fondo blanco
        ws.merge_cells("A1:A4")
        fill_blanco = PatternFill("solid", fgColor=blanco)
        for row in ws["A1:A4"]:
            for cell in row:
                cell.fill = fill_blanco

        logo = Path(__file__).parent.parent / "assets" / "hospital_logo.png"

        if logo.exists():
            imagen = Image(str(logo))

            # Dimensiones del logo
            imagen.width = 180
            imagen.height = 180

            # Posicionamiento preciso dentro de la celda combinada
            marker = AnchorMarker(
                col=0,                     # Columna A
                row=0,                     # Fila 1
                colOff=pixels_to_EMU(35),  # Desplazamiento horizontal
                rowOff=pixels_to_EMU(8)    # Desplazamiento vertical
            )

            imagen.anchor = OneCellAnchor(
                _from=marker,
                ext=XDRPositiveSize2D(
                    pixels_to_EMU(imagen.width),
                    pixels_to_EMU(imagen.height)
                )
            )

            ws.add_image(imagen)

        # Encabezados del reporte (Bloque Azul B2:F4)
        ws.merge_cells("B2:F2")
        ws["B2"] = "HOSPITAL MILITAR"
        ws["B2"].font = Font(bold=True, size=16, color=blanco)
        ws["B2"].alignment = Alignment(horizontal="center", vertical="center")
        ws["B2"].fill = PatternFill("solid", fgColor=azul)

        ws.merge_cells("B3:F3")
        ws["B3"] = "SISTEMA SIGIP"
        ws["B3"].font = Font(bold=True, size=12, color=blanco)
        ws["B3"].alignment = Alignment(horizontal="center", vertical="center")
        ws["B3"].fill = PatternFill("solid", fgColor=azul)

        ws.merge_cells("B4:F4")
        ws["B4"] = "REPORTE GENERAL DE EQUIPOS"
        ws["B4"].font = Font(bold=True, size=11, color=blanco)
        ws["B4"].alignment = Alignment(horizontal="center", vertical="center")
        ws["B4"].fill = PatternFill("solid", fgColor=azul)

        # --- METADATOS DEL REPORTE ---
        fecha = datetime.now()
        ws["B6"] = "Fecha"
        ws["C6"] = fecha.strftime("%d/%m/%Y")

        ws["B7"] = "Hora"
        ws["C7"] = fecha.strftime("%H:%M")

        ws["E6"] = "Total Equipos"
        ws["F6"] = len(datos)

        ws["E7"] = "Registros"
        ws["F7"] = len(datos)

        for celda in ["B6", "B7", "E6", "E7"]:
            ws[celda].font = Font(bold=True)

        # Configuración de alineación de Metadatos
        ws["B6"].alignment = Alignment(horizontal="left")
        ws["B7"].alignment = Alignment(horizontal="left")
        ws["C6"].alignment = Alignment(horizontal="left")
        ws["C7"].alignment = Alignment(horizontal="left")
        ws["E6"].alignment = Alignment(horizontal="left")
        ws["E7"].alignment = Alignment(horizontal="left")
        ws["F6"].alignment = Alignment(horizontal="right")
        ws["F7"].alignment = Alignment(horizontal="right")

        # --- TABLA DE DATOS ---
        encabezados = [
            "Nombre",
            "Tipo",
            "Marca",
            "Modelo",
            "Departamento",
            "Estado"
        ]

        fila_inicio = 10

        borde = Border(
            left=Side(style="thin", color="D9D9D9"),
            right=Side(style="thin", color="D9D9D9"),
            top=Side(style="thin", color="D9D9D9"),
            bottom=Side(style="thin", color="D9D9D9")
        )

        # Insertar encabezados
        for columna, texto in enumerate(encabezados, start=1):
            celda = ws.cell(row=fila_inicio, column=columna)
            celda.value = texto
            celda.font = Font(bold=True, color=blanco)
            celda.fill = PatternFill(fill_type="solid", fgColor=azul)
            celda.alignment = Alignment(horizontal="center", vertical="center")
            celda.border = borde

        # Insertar filas
        fila = fila_inicio + 1
        for equipo in datos:
            ws.cell(fila, 1).value = equipo["nombre_equipo"]
            ws.cell(fila, 2).value = equipo["tipo"]
            ws.cell(fila, 3).value = equipo["marca"]
            ws.cell(fila, 4).value = equipo["modelo"]
            ws.cell(fila, 5).value = equipo["departamento"]
            ws.cell(fila, 6).value = equipo["estado"]

            for columna in range(1, 7):
                celda = ws.cell(fila, columna)
                celda.border = borde
                celda.alignment = Alignment(vertical="center")

            fila += 1

        ultima_fila = max(fila - 1, fila_inicio)

        # Formato de semáforo por Estado
        verde = PatternFill(fill_type="solid", fgColor="C6EFCE")
        amarillo = PatternFill(fill_type="solid", fgColor="FFF2CC")
        rojo = PatternFill(fill_type="solid", fgColor="F4CCCC")

        for fila_actual in range(fila_inicio + 1, ultima_fila + 1):
            celda_estado = ws.cell(fila_actual, 6)
            estado = celda_estado.value

            if estado is None:
                continue

            estado_str = str(estado).upper()

            if "ACT" in estado_str:
                celda_estado.fill = verde
            elif "MANT" in estado_str:
                celda_estado.fill = amarillo
            elif "BAJA" in estado_str:
                celda_estado.fill = rojo

        # Crear tabla oficial de Excel sin sobrescribir el semáforo
        if datos:
            tabla = Table(
                displayName="TablaEquipos",
                ref=f"A{fila_inicio}:F{ultima_fila}"
            )
            estilo = TableStyleInfo(
                name="TableStyleLight1",
                showFirstColumn=False,
                showLastColumn=False,
                showRowStripes=False,
                showColumnStripes=False
            )
            tabla.tableStyleInfo = estilo
            ws.add_table(tabla)

        ws.freeze_panes = f"A{fila_inicio + 1}"

        # Ajuste de ancho de columnas
        for columna in range(1, 7):
            letra = get_column_letter(columna)
            longitud = 0
            for fila_excel in range(1, ultima_fila + 1):
                valor = ws.cell(fila_excel, columna).value
                if valor is not None:
                    longitud = max(longitud, len(str(valor)))
            # Mantener un ancho mínimo cómodo
            ws.column_dimensions[letra].width = max(longitud + 4, 15)

        # Pie de página / Resumen
        fila_resumen = ultima_fila + 3
        ws.merge_cells(
            start_row=fila_resumen,
            start_column=1,
            end_row=fila_resumen,
            end_column=6
        )

        celda_resumen = ws.cell(row=fila_resumen, column=1)
        celda_resumen.value = "Reporte generado automáticamente por SIGIP"
        celda_resumen.font = Font(italic=True, size=10, color="666666")
        celda_resumen.alignment = Alignment(horizontal="center")

        # Configuración de impresión
        ws.page_setup.orientation = "landscape"
        ws.page_setup.paperSize = ws.PAPERSIZE_A4
        ws.page_setup.fitToWidth = 1
        ws.page_margins = PageMargins(
            left=0.3,
            right=0.3,
            top=0.5,
            bottom=0.5
        )

        wb.properties.creator = "SIGIP"
        wb.properties.title = "Reporte General de Equipos"
        wb.properties.subject = "Hospital Militar"
        wb.properties.company = "Hospital Militar"
        wb.properties.category = "Reportes"

        archivo = BytesIO()
        wb.save(archivo)
        archivo.seek(0)

        return StreamingResponse(
            archivo,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=Reporte_Equipos_SIGIP.xlsx"
            }
        )

    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al exportar equipos: {str(e)}"
        )

    finally:
        if conexion and conexion.is_connected():
            if cursor:
                cursor.close()
            conexion.close()

            