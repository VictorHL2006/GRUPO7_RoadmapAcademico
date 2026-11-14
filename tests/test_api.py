import hashlib
from datetime import datetime, timezone
from uuid import UUID, uuid4

import jwt
import pytest
from fastapi import HTTPException

from backend.auth import hash_clave, usuario_actual
from backend.main import app, health
from backend.routers import auth as auth_router
from backend.routers import perfil as perfil_router
from backend.routers import roadmaps as roadmaps_router
from backend.routers import verificacion
from backend.routes import intereses, roadmap
from backend import services


class FakeCursor:
    def __init__(self, row=None, error=None):
        self.row = row
        self.error = error
        self.statements = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, sql, params=None):
        self.statements.append((sql, params))
        if self.error:
            raise self.error

    def executemany(self, sql, params):
        self.statements.append((sql, list(params)))

    def fetchone(self):
        return self.row

    def fetchall(self):
        return []


class FakeConnection:
    def __init__(self, cursor):
        self.fake_cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def cursor(self):
        return self.fake_cursor


def mock_db(monkeypatch, module, cursor):
    monkeypatch.setattr(module, "get_conn", lambda: FakeConnection(cursor))


class FakeUpload:
    def __init__(self, data, content_type):
        self.data = data
        self.content_type = content_type

    async def read(self, size=-1):
        return self.data[:size] if size >= 0 else self.data


def uploaded(filename, data, content_type):
    return FakeUpload(data, content_type)


def run_immediate(coroutine):
    """Run a coroutine composed only of the immediate fake uploads in these tests."""
    try:
        coroutine.send(None)
    except StopIteration as result:
        return result.value
    raise AssertionError("La operación de prueba intentó esperar una tarea externa")


@pytest.fixture
def signed_pdf():
    pdf = b"%PDF-1.7\nRoadmap de prueba\n%%EOF"
    return pdf, b"firma-de-prueba"


def test_health_returns_ok():
    assert health() == {"estado": "ok"}


def test_openapi_documents_roman_api_routes():
    paths = app.openapi()["paths"]
    required = {
        "/auth/yo", "/perfil/intereses", "/historial", "/roadmaps/recomendar",
        "/roadmaps/emitir", "/verificar/{codigo}", "/v/{codigo}",
        "/verificar/{codigo}/documento", "/tutor/estudiantes",
    }
    assert required <= paths.keys()
    assert "put" in paths["/historial"]


def test_cors_allows_static_frontend_origins():
    from fastapi.middleware.cors import CORSMiddleware
    config = next(item.kwargs for item in app.user_middleware if item.cls is CORSMiddleware)
    assert "http://localhost:3000" in config["allow_origins"]
    assert "http://127.0.0.1:3000" in config["allow_origins"]


def test_auth_dependency_requires_bearer():
    with pytest.raises(HTTPException) as exc:
        usuario_actual(None)
    assert exc.value.status_code == 401


def test_auth_dependency_rejects_invalid_token(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret-that-is-at-least-32-characters")
    with pytest.raises(HTTPException) as exc:
        usuario_actual("Bearer invalid.token")
    assert exc.value.status_code == 401


def test_auth_dependency_decodes_user_and_role(monkeypatch):
    secret = "test-secret-that-is-at-least-32-characters"
    monkeypatch.setenv("JWT_SECRET", secret)
    token = jwt.encode({"sub": "12", "rol": "tutor"}, secret, algorithm="HS256")
    assert usuario_actual(f"Bearer {token}") == {"id": 12, "rol": "tutor"}


def test_register_always_assigns_student_role(monkeypatch):
    from backend.routers.auth import RegistroIn
    cursor = FakeCursor(row=(31,))
    mock_db(monkeypatch, auth_router, cursor)
    result = auth_router.registrar(RegistroIn(
        codigo=" e001 ", nombres="Ana Demo", correo="ana@example.org", clave="password-demo"
    ))
    assert result == {"mensaje": "Cuenta creada", "id": 31}
    sql, params = cursor.statements[0]
    assert "'estudiante'" in sql
    assert params[0] == "E001"


def test_registration_model_accepts_guide_password_field():
    from backend.routers.auth import RegistroIn
    user = RegistroIn(codigo="E001", nombres="Ana", correo="ana@example.org", password="password-demo")
    assert user.clave == "password-demo"


def test_register_returns_conflict_for_duplicate(monkeypatch):
    from psycopg2.errors import UniqueViolation
    from backend.routers.auth import RegistroIn
    mock_db(monkeypatch, auth_router, FakeCursor(error=UniqueViolation("duplicate")))
    with pytest.raises(HTTPException) as exc:
        auth_router.registrar(RegistroIn(
            codigo="E001", nombres="Ana Demo", correo="ana@example.org", clave="password-demo"
        ))
    assert exc.value.status_code == 409


def test_password_hash_checks_plaintext_without_storing_it():
    hashed = hash_clave("correct-horse")
    assert "correct-horse" not in hashed
    assert auth_router.clave_valida("correct-horse", hashed)
    assert not auth_router.clave_valida("wrong-password", hashed)


def test_login_returns_signed_jwt_and_name(monkeypatch):
    from backend.routers.auth import LoginIn
    secret = "test-secret-that-is-at-least-32-characters"
    monkeypatch.setenv("JWT_SECRET", secret)
    mock_db(monkeypatch, auth_router,
            FakeCursor(row=(31, hash_clave("password-demo"), "estudiante", "Ana Demo")))
    result = auth_router.login(LoginIn(correo="ana@example.org", clave="password-demo"))
    claims = jwt.decode(result["token"], secret, algorithms=["HS256"])
    assert claims["sub"] == "31"
    assert result["rol"] == "estudiante"
    assert result["nombre"] == "Ana Demo"


def test_login_rejects_wrong_password(monkeypatch):
    from backend.routers.auth import LoginIn
    mock_db(monkeypatch, auth_router,
            FakeCursor(row=(31, hash_clave("right-password"), "estudiante", "Ana")))
    with pytest.raises(HTTPException) as exc:
        auth_router.login(LoginIn(correo="ana@example.org", clave="wrong-password"))
    assert exc.value.status_code == 401


def test_current_user_endpoint_returns_profile(monkeypatch):
    mock_db(monkeypatch, auth_router,
            FakeCursor(row=("E001", "Ana Demo", "ana@example.org", "estudiante")))
    result = auth_router.quien_soy({"id": 31, "rol": "estudiante"})
    assert result["codigo"] == "E001"
    assert result["rol"] == "estudiante"


def test_replace_history_deletes_then_inserts(monkeypatch):
    from backend.routers.perfil import CursoIn
    cursor = FakeCursor()
    mock_db(monkeypatch, perfil_router, cursor)
    result = perfil_router.reemplazar_historial(
        [CursoIn(codigo_curso="mat101", nota=15, periodo="2026-I")], {"id": 9}
    )
    assert result["cursos"] == 1
    assert cursor.statements[0][0].startswith("DELETE FROM historial_academico")
    assert cursor.statements[1][1] == [(9, "MAT101", 15.0, "2026-I")]


def test_replace_history_accepts_documented_object_shape(monkeypatch):
    from backend.routers.perfil import CursoIn, HistorialIn
    cursor = FakeCursor()
    mock_db(monkeypatch, perfil_router, cursor)
    data = HistorialIn(cursos=[CursoIn(codigo_curso="PRG101", nota=18, periodo="2026-I")])
    result = perfil_router.reemplazar_historial(data, {"id": 9})
    assert result["cursos"] == 1


def test_course_model_rejects_grade_outside_scale():
    from pydantic import ValidationError
    from backend.routers.perfil import CursoIn
    with pytest.raises(ValidationError):
        CursoIn(codigo_curso="MAT101", nota=21, periodo="2026-I")


def test_interests_are_available_under_profile_alias(monkeypatch):
    paths = app.openapi()["paths"]["/perfil/intereses"]
    assert set(paths) == {"get", "put"}
    cursor = FakeCursor()
    mock_db(monkeypatch, intereses, cursor)
    result = intereses.guardar_intereses(
        intereses.InteresesIn(intereses=[" redes ", "redes", "seguridad"]),
        {"id": 9, "rol": "estudiante"},
    )
    assert result["intereses"] == ["redes", "seguridad"]


def test_tutor_cannot_change_student_interests():
    with pytest.raises(HTTPException) as exc:
        intereses._estudiante({"rol": "tutor"})
    assert exc.value.status_code == 403


def test_recommendation_returns_plan_without_emitting(monkeypatch):
    result = {"estudiante": "E001", "especialidad": "Redes y Seguridad", "cursos": ["RED201"], "creditos": 4}
    monkeypatch.setattr(roadmap, "recomendar_para_usuario", lambda uid, credits: result)
    assert roadmap.recomendar(max_creditos=12, usuario={"id": 9, "rol": "estudiante"}) == result


def test_tutor_cannot_request_student_recommendation(monkeypatch):
    monkeypatch.setattr(roadmap, "recomendar_para_usuario", lambda *_: pytest.fail("should not query"))
    with pytest.raises(HTTPException) as exc:
        roadmap.recomendar(max_creditos=22, usuario={"id": 3, "rol": "tutor"})
    assert exc.value.status_code == 403


def test_recommendation_reports_missing_student(monkeypatch):
    monkeypatch.setattr(roadmap, "recomendar_para_usuario", lambda *_: None)
    with pytest.raises(HTTPException) as exc:
        roadmap.recomendar(max_creditos=22, usuario={"id": 999, "rol": "estudiante"})
    assert exc.value.status_code == 404


def test_recommendation_service_uses_database_history_and_interests(monkeypatch):
    cursor = FakeCursor(row=("E001", "Ana Demo"))
    mock_db(monkeypatch, services, cursor)
    monkeypatch.setattr(services, "cargar_json", lambda _: {"malla": True})
    captured = {}
    def build(malla, student, credits):
        captured.update(malla=malla, student=student, credits=credits)
        return {"especialidad": "Redes"}
    monkeypatch.setattr(services, "generar_recomendacion", build)
    result = services.recomendar_para_usuario(9, 16)
    assert result == {"especialidad": "Redes"}
    assert captured["student"] == {
        "codigo": "E001", "nombre": "Ana Demo", "aprobados": [], "intereses": [],
    }
    assert len(cursor.statements) == 3


def test_emit_service_creates_pdf_qr_and_stores_uuid(monkeypatch):
    cursor = FakeCursor(row=(44,))
    mock_db(monkeypatch, services, cursor)
    recommendation = {
        "estudiante": "E001", "especialidad": "Redes", "puntajes": {"Redes": 1},
        "cursos": ["RED201"], "creditos": 4,
    }
    monkeypatch.setenv("API_BASE_URL", "http://localhost:8000")
    monkeypatch.setattr(services, "recomendar_para_usuario", lambda *_: recommendation)
    generated = {}
    def make_pdf(rec, url):
        generated["url"] = url
        return b"%PDF-test"
    monkeypatch.setattr(services, "generar_pdf", make_pdf)
    monkeypatch.setattr(services, "firmar_pdf", lambda _: ("a" * 64, b"signature"))
    result = services.emitir_para_usuario(9, 12)
    assert result["id"] == 44
    code = result["codigo_verificacion"]
    assert str(UUID(code)) == code
    assert generated["url"] == f"http://localhost:8000/v/{code}"
    sql, params = cursor.statements[0]
    assert "codigo_verificacion" in sql
    assert params[1] == code


def test_emit_returns_public_verification_code(monkeypatch):
    result = {"id": 12, "codigo": str(uuid4()), "codigo_verificacion": str(uuid4())}
    monkeypatch.setattr(roadmap, "emitir_para_usuario", lambda *_: result)
    assert roadmap.emitir(max_creditos=22, usuario={"id": 9, "rol": "estudiante"}) == result


def test_tutor_cannot_emit_roadmap(monkeypatch):
    monkeypatch.setattr(roadmap, "emitir_para_usuario", lambda *_: pytest.fail("should not emit"))
    with pytest.raises(HTTPException) as exc:
        roadmap.emitir(max_creditos=22, usuario={"id": 3, "rol": "tutor"})
    assert exc.value.status_code == 403


def test_legacy_generate_path_calls_same_emitter(monkeypatch):
    result = {"id": 12, "codigo": "public-code"}
    monkeypatch.setattr(roadmap, "emitir_para_usuario", lambda *_: result)
    assert roadmap.generar(max_creditos=10, usuario={"id": 9, "rol": "estudiante"}) == result


def test_student_download_query_is_limited_to_owner(monkeypatch):
    cursor = FakeCursor(row=(b"file",))
    mock_db(monkeypatch, roadmaps_router, cursor)
    assert roadmaps_router._buscar_archivo("42", {"id": 9, "rol": "estudiante"}, "firma") == (b"file",)
    sql, params = cursor.statements[0]
    assert "usuario_id=%s" in sql
    assert params == (9, "42", "42")


def test_tutor_download_query_accepts_any_student_roadmap(monkeypatch):
    cursor = FakeCursor(row=(b"file",))
    mock_db(monkeypatch, roadmaps_router, cursor)
    roadmaps_router._buscar_archivo("42", {"id": 3, "rol": "tutor"}, "archivo_pdf")
    sql, params = cursor.statements[0]
    assert "usuario_id" not in sql
    assert params == ("42", "42")


def test_manual_signature_verification_accepts_authentic_pdf(monkeypatch, signed_pdf):
    monkeypatch.setattr(verificacion, "_verificar", lambda *_: True)
    pdf, signature = signed_pdf
    result = run_immediate(verificacion.verificar_archivos(
        uploaded("roadmap.pdf", pdf, "application/pdf"),
        uploaded("roadmap.sig", signature, "application/octet-stream"),
    ))
    assert result["resultado"] == "auténtico"


def test_manual_signature_verification_detects_modified_pdf(monkeypatch, signed_pdf):
    monkeypatch.setattr(verificacion, "_verificar", lambda *_: False)
    pdf, signature = signed_pdf
    result = verificacion._resultado(pdf + b"changed", signature)
    assert result["resultado"] == "alterado"


def test_manual_verification_rejects_non_pdf():
    with pytest.raises(HTTPException) as exc:
        run_immediate(verificacion.verificar_archivos(
            uploaded("bad.pdf", b"not pdf", "application/pdf"),
            uploaded("bad.sig", b"sig", "application/octet-stream"),
        ))
    assert exc.value.status_code == 400


def test_manual_verification_rejects_wrong_media_type():
    with pytest.raises(HTTPException) as exc:
        run_immediate(verificacion.verificar_archivos(
            uploaded("roadmap.pdf", b"%PDF-test", "text/plain"),
            uploaded("roadmap.sig", b"sig", "application/octet-stream"),
        ))
    assert exc.value.status_code == 415


def test_public_uuid_verification_returns_authentic_document(monkeypatch, signed_pdf):
    pdf, signature = signed_pdf
    code = uuid4()
    row = (pdf, signature, hashlib.sha256(pdf).hexdigest(),
           datetime.now(timezone.utc), "E001", code)
    monkeypatch.setattr(verificacion, "_leer_codigo", lambda _: row)
    monkeypatch.setattr(verificacion, "_verificar", lambda *_: True)
    result = verificacion.verificar_por_codigo(str(code))
    assert result["resultado"] == "auténtico"
    assert result["codigo"] == str(code)


def test_public_verification_detects_mismatched_stored_hash(monkeypatch, signed_pdf):
    pdf, signature = signed_pdf
    row = (pdf, signature, "0" * 64, datetime.now(timezone.utc), "E001", uuid4())
    monkeypatch.setattr(verificacion, "_leer_codigo", lambda _: row)
    monkeypatch.setattr(verificacion, "_verificar", lambda *_: True)
    assert verificacion.verificar_por_codigo("sample")["resultado"] == "alterado"


def test_missing_public_verification_code_returns_404(monkeypatch):
    monkeypatch.setattr(verificacion, "_leer_codigo", lambda _: None)
    with pytest.raises(HTTPException) as exc:
        verificacion.verificar_por_codigo(str(uuid4()))
    assert exc.value.status_code == 404


def test_qr_short_link_redirects_to_static_frontend(monkeypatch):
    monkeypatch.setenv("FRONTEND_URL", "http://localhost:3000")
    code = str(uuid4())
    response = verificacion.abrir_verificacion(code)
    assert response.status_code == 307
    assert response.headers["location"].endswith(f"/verificar.html?codigo={code}")


def test_uploaded_pdf_matches_the_issued_document(monkeypatch, signed_pdf):
    pdf, signature = signed_pdf
    code = str(uuid4())
    row = (pdf, signature, hashlib.sha256(pdf).hexdigest(),
           datetime.now(timezone.utc), "E001", code)
    monkeypatch.setattr(verificacion, "_leer_codigo", lambda _: row)
    monkeypatch.setattr(verificacion, "_verificar", lambda *_: True)
    result = run_immediate(verificacion.verificar_documento_emitido(
        code, uploaded("roadmap.pdf", pdf, "application/pdf")
    ))
    assert result["resultado"] == "auténtico"


def test_uploaded_pdf_detects_change_to_issued_document(monkeypatch, signed_pdf):
    pdf, signature = signed_pdf
    code = str(uuid4())
    row = (pdf, signature, hashlib.sha256(pdf).hexdigest(),
           datetime.now(timezone.utc), "E001", code)
    monkeypatch.setattr(verificacion, "_leer_codigo", lambda _: row)
    monkeypatch.setattr(verificacion, "_verificar", lambda *_: True)
    result = run_immediate(verificacion.verificar_documento_emitido(
        code, uploaded("roadmap.pdf", pdf + b"changed", "application/pdf")
    ))
    assert result["resultado"] == "alterado"
