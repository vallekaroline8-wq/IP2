import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from procedures.bitacora import obtener_bitacora

def test_obtener_bitacora_retorna_items():
    resultado = obtener_bitacora(page=1, limit=10)
    assert "items" in resultado
    assert "total" in resultado
    assert resultado["total"] >= 1
    assert len(resultado["items"]) >= 1
    primero = resultado["items"][0]
    assert "id" in primero
    assert "fecha" in primero
    assert "usuario" in primero
    assert "accion" in primero
