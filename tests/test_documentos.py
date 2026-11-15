from pathlib import Path
 
from backend import documentos
from backend.recomendacion.motor import cargar_json, generar_recomendacion
 
MALLA = cargar_json(Path(__file__).resolve().parent.parent / "data" / "malla.json")
EST = {"codigo": "E001", "aprobados": ["MAT101", "PRG101"], "intereses": ["seguridad", "redes"]}
 
 
def test_pdf_se_genera_con_acentos_y_caracteres_peligrosos():
    rec = generar_recomendacion(MALLA, EST)
    usuario = {"nombres": "Ñandú <b>Pérez</b> & Co.", "codigo": "E001"}
    pdf = documentos.generar_pdf(usuario, rec, MALLA, "11111111-1111-1111-1111-111111111111",
                                 "http://localhost:8000/v/11111111-1111-1111-1111-111111111111")
    assert pdf.startswith(b"%PDF") and len(pdf) > 3000
 
 
def test_pdf_sin_cursos_pendientes():
    todos = [c["codigo"] for c in MALLA["cursos"]]
    rec = generar_recomendacion(MALLA, {"codigo": "E9", "aprobados": todos, "intereses": []})
    pdf = documentos.generar_pdf({"nombres": "Ana", "codigo": "E9"}, rec, MALLA, "x", "http://x/v/x")
    assert pdf.startswith(b"%PDF")
