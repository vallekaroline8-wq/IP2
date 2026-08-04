import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from procedures.export_bitacora import exportar_bitacora_excel, exportar_bitacora_pdf


class DummyCursor:
    def __init__(self):
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchall(self):
        return [
            {
                "id": 1,
                "fecha": "2026-07-28 10:00:00",
                "usuario": "admin",
                "accion": "Alta",
                "modulo": "Usuarios",
                "detalle": "Creó usuario",
            }
        ]

    def close(self):
        return None


class DummyConn:
    def __init__(self):
        self.cursor_obj = DummyCursor()

    def cursor(self, dictionary=True):
        return self.cursor_obj

    def is_connected(self):
        return True

    def close(self):
        return None


def fake_get_connection():
    return DummyConn()


def test_exportar_bitacora_excel_generates_bytes(monkeypatch):
    monkeypatch.setattr("procedures.export_bitacora.get_connection", fake_get_connection)

    data = exportar_bitacora_excel()

    assert isinstance(data, bytes)
    assert len(data) > 0
    assert data.startswith(b"PK")


def test_exportar_bitacora_pdf_generates_bytes(monkeypatch):
    monkeypatch.setattr("procedures.export_bitacora.get_connection", fake_get_connection)

    data = exportar_bitacora_pdf()

    assert isinstance(data, bytes)
    assert len(data) > 0
    assert data.startswith(b"%PDF")
