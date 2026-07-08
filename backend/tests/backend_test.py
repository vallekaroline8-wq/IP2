"""Backend tests for SIGIP - Hospital Militar IPAM.

Covers: auth (3 roles), RBAC, dashboard, CRUD (departamentos/secciones/segmentos/equipos/usuarios),
generar-ips (RN-03/RN-04), asignaciones (RN-01/RN-02/RN-05), reasignar, liberar, ip estado,
historial, bitacora, export excel/pdf.
"""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://sigip-hospital.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


def _login(username, password):
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json={"username": username, "password": password}, timeout=30)
    return s, r


@pytest.fixture(scope="session")
def admin():
    s, r = _login("admin", "admin123")
    assert r.status_code == 200, r.text
    token = r.json()["token"]
    s.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def tecnico():
    s, r = _login("tecnico", "tecnico123")
    assert r.status_code == 200, r.text
    s.headers.update({"Authorization": f"Bearer {r.json()['token']}", "Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def consulta():
    s, r = _login("consulta", "consulta123")
    assert r.status_code == 200, r.text
    s.headers.update({"Authorization": f"Bearer {r.json()['token']}", "Content-Type": "application/json"})
    return s


# ---------------- AUTH ----------------
class TestAuth:
    def test_login_admin(self):
        _, r = _login("admin", "admin123")
        assert r.status_code == 200
        d = r.json()
        assert "token" in d and d["user"]["username"] == "admin"
        assert d["user"]["role"] == "administrador"
        # httpOnly cookie
        assert "access_token" in r.cookies

    def test_login_wrong_password(self):
        _, r = _login("admin", "wrong")
        assert r.status_code == 401

    def test_login_tecnico(self):
        _, r = _login("tecnico", "tecnico123")
        assert r.status_code == 200
        assert r.json()["user"]["role"] == "tecnico"

    def test_login_consulta(self):
        _, r = _login("consulta", "consulta123")
        assert r.status_code == 200
        assert r.json()["user"]["role"] == "consulta"

    def test_bcrypt_hash_format(self, admin):
        # Not directly exposed, but /auth/me should not expose password_hash
        r = admin.get(f"{API}/auth/me")
        assert r.status_code == 200
        assert "password_hash" not in r.json()

    def test_me_requires_token(self):
        r = requests.get(f"{API}/auth/me")
        assert r.status_code == 401


# ---------------- RBAC ----------------
class TestRBAC:
    def test_consulta_cannot_write_departamentos(self, consulta):
        r = consulta.post(f"{API}/departamentos", json={"nombre": "TEST_DEP_C", "descripcion": "x"})
        assert r.status_code == 403

    def test_consulta_cannot_access_usuarios(self, consulta):
        r = consulta.get(f"{API}/usuarios")
        assert r.status_code == 403

    def test_tecnico_cannot_access_usuarios(self, tecnico):
        r = tecnico.get(f"{API}/usuarios")
        assert r.status_code == 403

    def test_consulta_can_read_dashboard(self, consulta):
        r = consulta.get(f"{API}/dashboard")
        assert r.status_code == 200


# ---------------- DASHBOARD ----------------
class TestDashboard:
    def test_dashboard_structure(self, admin):
        r = admin.get(f"{API}/dashboard")
        assert r.status_code == 200
        d = r.json()
        for k in ["cards", "pie", "por_segmento", "ultimas_asignaciones", "actividad"]:
            assert k in d
        for c in ["segmentos", "departamentos", "equipos", "ips", "disponibles",
                  "ocupadas", "reservadas", "telefonos"]:
            assert c in d["cards"]
            assert isinstance(d["cards"][c], int)
        assert len(d["pie"]) == 3
        assert d["cards"]["segmentos"] >= 1
        assert d["cards"]["ips"] >= 254


# ---------------- CRUD Departamentos ----------------
class TestDepartamentos:
    _created_id = None

    def test_list(self, admin):
        r = admin.get(f"{API}/departamentos")
        assert r.status_code == 200
        assert r.json()["total"] >= 7

    def test_create(self, admin):
        r = admin.post(f"{API}/departamentos", json={"nombre": f"TEST_DEP_{uuid.uuid4().hex[:6]}", "descripcion": "desc"})
        assert r.status_code == 200
        d = r.json()
        assert "id" in d and d["nombre"].startswith("TEST_DEP_")
        TestDepartamentos._created_id = d["id"]

    def test_update(self, admin):
        assert TestDepartamentos._created_id
        r = admin.put(f"{API}/departamentos/{TestDepartamentos._created_id}",
                      json={"nombre": "TEST_DEP_UPDATED", "descripcion": "upd"})
        assert r.status_code == 200
        # verify persistence via list search
        r2 = admin.get(f"{API}/departamentos?search=TEST_DEP_UPDATED")
        assert r2.status_code == 200
        assert any(x["nombre"] == "TEST_DEP_UPDATED" for x in r2.json()["items"])

    def test_search_pagination(self, admin):
        r = admin.get(f"{API}/departamentos?page=1&limit=3")
        assert r.status_code == 200
        d = r.json()
        assert len(d["items"]) <= 3
        assert "pages" in d

    def test_delete(self, admin):
        assert TestDepartamentos._created_id
        r = admin.delete(f"{API}/departamentos/{TestDepartamentos._created_id}")
        assert r.status_code == 200


# ---------------- Secciones ----------------
class TestSecciones:
    def test_create_with_dep(self, admin):
        deps = admin.get(f"{API}/departamentos?all=true").json()["items"]
        assert deps
        r = admin.post(f"{API}/secciones", json={"nombre": "TEST_SEC", "departamento_id": deps[0]["id"]})
        assert r.status_code == 200
        sec_id = r.json()["id"]
        # delete
        d = admin.delete(f"{API}/secciones/{sec_id}")
        assert d.status_code == 200


# ---------------- Segmentos + Generar IPs ----------------
class TestSegmentos:
    _seg_id = None

    def test_list_segments_have_counts(self, admin):
        r = admin.get(f"{API}/segmentos")
        assert r.status_code == 200
        for s in r.json()["items"]:
            assert "total_ips" in s and "ocupadas" in s and "disponibles" in s

    def test_create_segment(self, admin):
        # unique red
        red = f"10.{__import__('random').randint(0,254)}.{__import__('random').randint(0,254)}.0"
        r = admin.post(f"{API}/segmentos", json={"nombre": f"TEST_SEG_{uuid.uuid4().hex[:6]}",
                                                  "direccion_red": red, "mascara": "255.255.255.0",
                                                  "gateway": red.rsplit('.',1)[0] + ".254"})
        assert r.status_code == 200, r.text
        TestSegmentos._seg_id = r.json()["id"]

    def test_generar_ips_rn04(self, admin):
        assert TestSegmentos._seg_id
        r = admin.post(f"{API}/segmentos/{TestSegmentos._seg_id}/generar-ips")
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["total"] == 254

    def test_generar_ips_rn03_duplicate(self, admin):
        assert TestSegmentos._seg_id
        r = admin.post(f"{API}/segmentos/{TestSegmentos._seg_id}/generar-ips")
        assert r.status_code == 400

    def test_ips_count_persisted(self, admin):
        r = admin.get(f"{API}/ips?segmento_id={TestSegmentos._seg_id}&limit=1")
        assert r.status_code == 200
        assert r.json()["total"] == 254

    def test_authorize_departments_rn01(self, admin):
        deps = admin.get(f"{API}/departamentos?all=true").json()["items"]
        dep_id = deps[0]["id"]
        r = admin.post(f"{API}/departamento-segmento",
                       json={"departamento_id": dep_id, "segmento_ids": [TestSegmentos._seg_id]})
        assert r.status_code == 200
        chk = admin.get(f"{API}/departamento-segmento/{dep_id}").json()
        assert TestSegmentos._seg_id in chk["segmento_ids"]


# ---------------- IPs ----------------
class TestIPs:
    def test_list_filter_estado(self, admin):
        r = admin.get(f"{API}/ips?estado=disponible&limit=5")
        assert r.status_code == 200
        for i in r.json()["items"]:
            assert i["estado"] == "disponible"

    def test_search_by_ip(self, admin):
        r = admin.get(f"{API}/ips?search=192.168.10.")
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_change_state_reservada_and_back(self, admin):
        r = admin.get(f"{API}/ips?estado=disponible&limit=1").json()
        ip = r["items"][0]
        assert admin.put(f"{API}/ips/{ip['id']}/estado", json={"estado": "reservada"}).status_code == 200
        # verify
        r2 = admin.get(f"{API}/ips?search={ip['direccion']}").json()
        assert any(x["id"] == ip["id"] and x["estado"] == "reservada" for x in r2["items"])
        # revert
        assert admin.put(f"{API}/ips/{ip['id']}/estado", json={"estado": "disponible"}).status_code == 200

    def test_history_of_ip(self, admin):
        # find an occupied ip
        r = admin.get(f"{API}/ips?estado=ocupada&limit=1").json()
        if not r["items"]:
            pytest.skip("No occupied IPs")
        ip = r["items"][0]
        h = admin.get(f"{API}/ips/{ip['id']}/historial")
        assert h.status_code == 200
        assert "items" in h.json()


# ---------------- Equipos ----------------
class TestEquipos:
    _eq_id = None

    def test_create_telefono_ip(self, admin):
        deps = admin.get(f"{API}/departamentos?all=true").json()["items"]
        tipos = admin.get(f"{API}/tipo_dispositivo?all=true").json()["items"]
        tel = next(t for t in tipos if "Tel" in t["nombre"])
        r = admin.post(f"{API}/equipos", json={
            "nombre": f"TEST_TEL_{uuid.uuid4().hex[:6]}", "marca": "Cisco", "modelo": "IP",
            "tipo_id": tel["id"], "departamento_id": deps[0]["id"], "seccion_id": "",
            "es_telefono_ip": True,
        })
        assert r.status_code == 200
        TestEquipos._eq_id = r.json()["id"]
        assert r.json()["es_telefono_ip"] is True

    def test_list_filter_telefono(self, admin):
        r = admin.get(f"{API}/equipos?tipo=telefono")
        assert r.status_code == 200
        for e in r.json()["items"]:
            assert e["es_telefono_ip"] is True

    def test_update_and_delete(self, admin):
        assert TestEquipos._eq_id
        deps = admin.get(f"{API}/departamentos?all=true").json()["items"]
        tipos = admin.get(f"{API}/tipo_dispositivo?all=true").json()["items"]
        r = admin.put(f"{API}/equipos/{TestEquipos._eq_id}", json={
            "nombre": "TEST_TEL_UPD", "marca": "Cisco", "modelo": "IP2",
            "tipo_id": tipos[0]["id"], "departamento_id": deps[0]["id"], "seccion_id": "",
            "es_telefono_ip": False,
        })
        assert r.status_code == 200
        d = admin.delete(f"{API}/equipos/{TestEquipos._eq_id}")
        assert d.status_code == 200


# ---------------- Asignaciones (RN-01/02/05) ----------------
class TestAsignaciones:
    def test_assign_full_flow(self, admin):
        # Create dept, segment, generate IPs, authorize, create equipo, assign, liberate
        dep = admin.post(f"{API}/departamentos", json={"nombre": f"TEST_ADEP_{uuid.uuid4().hex[:5]}", "descripcion": ""}).json()
        red = f"172.{__import__('random').randint(16,31)}.{__import__('random').randint(0,254)}.0"
        seg = admin.post(f"{API}/segmentos", json={"nombre": f"TEST_ASEG_{uuid.uuid4().hex[:5]}",
                                                    "direccion_red": red, "mascara": "255.255.255.0",
                                                    "gateway": red.rsplit('.',1)[0]+".254"}).json()
        gen = admin.post(f"{API}/segmentos/{seg['id']}/generar-ips")
        assert gen.status_code == 200
        # Authorize
        admin.post(f"{API}/departamento-segmento", json={"departamento_id": dep["id"], "segmento_ids": [seg["id"]]})
        # Create equipo
        tipos = admin.get(f"{API}/tipo_dispositivo?all=true").json()["items"]
        eq = admin.post(f"{API}/equipos", json={"nombre": f"TEST_EQ_{uuid.uuid4().hex[:5]}",
                                                 "marca": "x", "modelo": "x",
                                                 "tipo_id": tipos[0]["id"], "departamento_id": dep["id"],
                                                 "seccion_id": "", "es_telefono_ip": False}).json()
        ip = admin.get(f"{API}/ips?segmento_id={seg['id']}&estado=disponible&limit=1").json()["items"][0]

        # Assign OK
        r = admin.post(f"{API}/asignaciones", json={"ip_id": ip["id"], "equipo_id": eq["id"]})
        assert r.status_code == 200, r.text

        # RN-02: second attempt on same IP -> 400
        ip2 = admin.get(f"{API}/ips?segmento_id={seg['id']}&estado=disponible&limit=1").json()["items"][0]
        r2 = admin.post(f"{API}/asignaciones", json={"ip_id": ip["id"], "equipo_id": eq["id"]})
        assert r2.status_code == 400

        # RN-05: same equipo cannot get second IP
        r3 = admin.post(f"{API}/asignaciones", json={"ip_id": ip2["id"], "equipo_id": eq["id"]})
        assert r3.status_code == 400
        assert "RN-05" in r3.json().get("detail", "") or "activa" in r3.json().get("detail", "").lower()

        # Find active asignacion for this equipo
        asigs = admin.get(f"{API}/asignaciones?activas=true&limit=100").json()["items"]
        active = next(a for a in asigs if a["equipo_id"] == eq["id"])
        # Liberar
        rl = admin.post(f"{API}/asignaciones/{active['id']}/liberar")
        assert rl.status_code == 200

        # Reasignar (should work now)
        rr = admin.post(f"{API}/asignaciones/reasignar", json={"ip_id": ip["id"], "equipo_id": eq["id"]})
        assert rr.status_code == 200

        # RN-01: unauthorized segment
        red2 = f"192.{__import__('random').randint(100,200)}.{__import__('random').randint(0,254)}.0"
        seg2 = admin.post(f"{API}/segmentos", json={"nombre": f"TEST_ASEG2_{uuid.uuid4().hex[:5]}",
                                                     "direccion_red": red2, "mascara": "255.255.255.0",
                                                     "gateway": red2.rsplit('.',1)[0]+".254"}).json()
        admin.post(f"{API}/segmentos/{seg2['id']}/generar-ips")
        ip3 = admin.get(f"{API}/ips?segmento_id={seg2['id']}&estado=disponible&limit=1").json()["items"][0]
        # Create a new equipo (fresh, no IP) in dep
        eq2 = admin.post(f"{API}/equipos", json={"nombre": f"TEST_EQ2_{uuid.uuid4().hex[:5]}",
                                                  "marca": "x", "modelo": "x",
                                                  "tipo_id": tipos[0]["id"], "departamento_id": dep["id"],
                                                  "seccion_id": "", "es_telefono_ip": False}).json()
        r4 = admin.post(f"{API}/asignaciones", json={"ip_id": ip3["id"], "equipo_id": eq2["id"]})
        assert r4.status_code == 400
        assert "RN-01" in r4.json().get("detail", "")


# ---------------- Usuarios ----------------
class TestUsuarios:
    _uid = None

    def test_create_user(self, admin):
        r = admin.post(f"{API}/usuarios", json={
            "nombre": "TEST User", "username": f"test_{uuid.uuid4().hex[:6]}",
            "password": "pw12345", "role": "tecnico", "activo": True,
        })
        assert r.status_code == 200, r.text
        TestUsuarios._uid = r.json()["id"]

    def test_change_password(self, admin):
        assert TestUsuarios._uid
        r = admin.put(f"{API}/usuarios/{TestUsuarios._uid}/password", json={"password": "newpw123"})
        assert r.status_code == 200

    def test_deactivate(self, admin):
        assert TestUsuarios._uid
        r = admin.delete(f"{API}/usuarios/{TestUsuarios._uid}")
        assert r.status_code == 200

    def test_cannot_delete_admin(self, admin):
        users = admin.get(f"{API}/usuarios?search=admin&limit=50").json()["items"]
        adm = next(u for u in users if u["username"] == "admin")
        r = admin.delete(f"{API}/usuarios/{adm['id']}")
        assert r.status_code == 400


# ---------------- Bitacora ----------------
class TestBitacora:
    def test_bitacora_has_login(self, admin):
        r = admin.get(f"{API}/bitacora?search=sesi&limit=20")
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_bitacora_has_alta(self, admin):
        r = admin.get(f"{API}/bitacora?search=Alta&limit=20")
        assert r.status_code == 200


# ---------------- Export ----------------
class TestExport:
    @pytest.mark.parametrize("path,ctype", [
        ("ips/excel", "spreadsheetml"),
        ("ips/pdf", "application/pdf"),
        ("asignaciones/pdf", "application/pdf"),
        ("bitacora/excel", "spreadsheetml"),
    ])
    def test_export(self, admin, path, ctype):
        r = admin.get(f"{API}/export/{path}")
        assert r.status_code == 200
        assert ctype in r.headers.get("content-type", "").lower()
        assert len(r.content) > 100
