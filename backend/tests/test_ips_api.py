import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from procedures.ips import resolver_id_estado, map_estado_db, map_estado_frontend, obtener_ips


def test_resolver_id_estado_para_valores_basicos():
    assert resolver_id_estado("disponible") == 3
    assert resolver_id_estado("ocupada") == 4
    assert resolver_id_estado("asignada") == 4
    assert resolver_id_estado("reservada") == 5


def test_map_estado_frontend_y_db():
    assert map_estado_frontend("DISPONIBLE") == "disponible"
    assert map_estado_frontend("ASIGNADA") == "ocupada"
    assert map_estado_db("ocupada") == "ASIGNADA"


def test_filtrar_ips_por_segmento_numero():
    resultado = obtener_ips(page=1, limit=20, segmento_id=6)
    assert resultado["total"] >= 1
    assert all(ip["direccion"].split(".")[2] == "1" for ip in resultado["items"])


def test_resolver_id_estado_invalido_lanza_error():
    with pytest.raises(Exception):
        resolver_id_estado("mantenimiento")
