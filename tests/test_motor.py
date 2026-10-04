from backend.recomendacion.motor import *

MALLA = cargar_json("data/malla.json")

def test_habilitados():
    codigos = [c["codigo"] for c in cursos_habilitados(MALLA, ["MAT101"])]
    assert "MAT102" in codigos

def test_carga_no_supera_maximo():
    _, total = armar_carga(cursos_habilitados(MALLA, ["MAT101", "PRG101"]), MALLA, 8)
    assert total <= 8

def test_especialidad():
    esp, _ = sugerir_especialidad(["seguridad", "redes"], MALLA["especialidades"])
    assert esp == "Redes y Seguridad"

def test_prerrequisitos_existen_en_malla():
    codigos = {curso["codigo"] for curso in MALLA["cursos"]}
    faltantes = {
        prerequisito
        for curso in MALLA["cursos"]
        for prerequisito in curso["prerrequisitos"]
        if prerequisito not in codigos
    }
    assert faltantes == set()