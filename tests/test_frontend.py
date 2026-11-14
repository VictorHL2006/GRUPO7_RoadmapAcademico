from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"


def test_static_entry_points_to_demo():
    page = (FRONTEND / "index.html").read_text(encoding="utf-8")
    assert "demo.html" in page
    assert (FRONTEND / "demo.html").is_file()


def test_demo_checks_python_api_health():
    page = (FRONTEND / "demo.html").read_text(encoding="utf-8")
    assert "api('/health')" in page
    assert "registro.html" in page
    assert "login.html" in page
    assert "verificar.html" in page


def test_generator_separates_preview_from_signed_emission():
    page = (FRONTEND / "generar.html").read_text(encoding="utf-8")
    assert "'/roadmaps/recomendar'" in page
    assert "'/roadmaps/emitir'" in page
    assert page.index("'/roadmaps/recomendar'") < page.index("'/roadmaps/emitir'")


def test_verification_page_accepts_qr_uuid_and_legacy_id():
    page = (FRONTEND / "verificar.html").read_text(encoding="utf-8")
    assert "params.get('codigo')||params.get('id')" in page


def test_react_and_vite_files_are_removed():
    assert not (FRONTEND / "package.json").exists()
    assert not (FRONTEND / "vite.config.js").exists()
    assert not (FRONTEND / ".env.example").exists()
    assert not list(FRONTEND.rglob("*.jsx"))
