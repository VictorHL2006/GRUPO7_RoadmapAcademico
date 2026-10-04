import json
from pathlib import Path

def cargar_json(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))

def cursos_habilitados(malla, aprobados):
    return [c for c in malla["cursos"]
            if c["codigo"] not in aprobados
            and all(p in aprobados for p in c["prerrequisitos"])]

def prioridad(curso, malla):
    return sum(1 for c in malla["cursos"] if curso["codigo"] in c["prerrequisitos"])

def armar_carga(habilitados, malla, max_creditos=22):
    ordenados = sorted(habilitados, key=lambda c: prioridad(c, malla), reverse=True)
    carga, total = [], 0
    for c in ordenados:
        if total + c["creditos"] <= max_creditos:
            carga.append(c)
            total += c["creditos"]
    return carga, total

def sugerir_especialidad(intereses, especialidades):
    puntajes = {e["nombre"]: len(set(intereses) & set(e["areas"])) for e in especialidades}
    return max(puntajes, key=puntajes.get), puntajes

def generar_recomendacion(malla, estudiante, max_creditos=22):
    habilitados = cursos_habilitados(malla, estudiante["aprobados"])
    carga, total = armar_carga(habilitados, malla, max_creditos)
    esp, puntajes = sugerir_especialidad(estudiante["intereses"], malla["especialidades"])
    return {
        "estudiante": estudiante["codigo"],
        "especialidad": esp,
        "puntajes": puntajes,
        "cursos": [c["codigo"] for c in carga],
        "creditos": total
    }