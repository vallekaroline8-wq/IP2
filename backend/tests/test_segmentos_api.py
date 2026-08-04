import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from procedures.segmentos import obtener_segmentos, generar_ips_segmento


def test_obtener_segmentos_contiene_contadores_ip():
    resultado = obtener_segmentos(page=1, limit=5)
    assert "items" in resultado
    assert "total" in resultado
    if resultado["items"]:
        primero = resultado["items"][0]
        assert "total_ips" in primero
        assert "ocupadas" in primero
        assert "disponibles" in primero
        assert isinstance(primero["total_ips"], int)
        assert isinstance(primero["ocupadas"], int)
        assert isinstance(primero["disponibles"], int)
