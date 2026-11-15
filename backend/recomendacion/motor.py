"""Motor de recomendación académica de ROADMAP ACADÉMICO.
 
Es un motor de reglas (sin IA ni servicios externos): con el mismo historial
siempre devuelve el mismo plan, lo que permite probarlo y certificarlo.
"""
import json
from pathlib import Path
 
MAX_CREDITOS_DEFECTO = 22
MAX_CICLOS_DEFECTO = 12
MAX_DIFICULTAD_DEFECTO = 16   # suma de dificultades (1 a 5 por curso) permitida por ciclo
DIFICULTAD_DEFECTO = 3
 
 
def cargar_json(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))
 
 
def validar_malla(malla):
    """Devuelve una lista de errores de la malla (vacía si está bien)."""
    errores = []
    cursos = malla["cursos"]
    por_codigo = {c["codigo"]: c for c in cursos}
    if len(por_codigo) != len(cursos):
        errores.append("Hay códigos de curso repetidos.")
    for c in cursos:
        if not 1 <= c.get("dificultad", DIFICULTAD_DEFECTO) <= 5:
            errores.append(f"{c['codigo']}: la dificultad debe estar entre 1 y 5.")
    for c in cursos:
        for p in c["prerrequisitos"]:
            if p not in por_codigo:
                errores.append(f"{c['codigo']} exige {p}, que no existe en la malla.")
 
    visitado, en_pila = set(), set()
 
    def hay_ciclo(cod):
        if cod in en_pila:
            return True
        if cod in visitado or cod not in por_codigo:
            return False
        visitado.add(cod)
        en_pila.add(cod)
        hallado = any(hay_ciclo(p) for p in por_codigo[cod]["prerrequisitos"])
        en_pila.discard(cod)
        return hallado
 
    if any(hay_ciclo(cod) for cod in list(por_codigo)):
        errores.append("Hay prerrequisitos circulares.")
    return errores
 
 
def cursos_habilitados(malla, aprobados):
    """Cursos no aprobados cuyos prerrequisitos ya están aprobados."""
    return [c for c in malla["cursos"]
            if c["codigo"] not in aprobados
            and all(p in aprobados for p in c["prerrequisitos"])]
 
 
def prioridad(curso, malla):
    """Cuántos cursos dependen directamente de este curso."""
    return sum(1 for c in malla["cursos"] if curso["codigo"] in c["prerrequisitos"])
 
 
def prioridad_total(curso, malla):
    """Cuántos cursos dependen de este, directa o indirectamente (cadena completa)."""
    dependientes = {}
    for c in malla["cursos"]:
        for p in c["prerrequisitos"]:
            dependientes.setdefault(p, []).append(c["codigo"])
    visto, pendientes = set(), [curso["codigo"]]
    while pendientes:
        actual = pendientes.pop()
        for d in dependientes.get(actual, []):
            if d not in visto:
                visto.add(d)
                pendientes.append(d)
    return len(visto)
 
 
def armar_carga(habilitados, malla, max_creditos=MAX_CREDITOS_DEFECTO,
                areas_preferidas=None, max_cursos=None, max_dificultad=None):
    """Elige cursos sin pasar el máximo de créditos ni la suma máxima de dificultad.
 
    Balance de carga: la dificultad de cada curso (campo opcional "dificultad", 1 a 5)
    evita ciclos con demasiados cursos pesados a la vez.
 
    Orden: primero los que desbloquean más cursos; si empatan, los que
    coinciden con las áreas preferidas; si aún empatan, por código.
    """
    areas = {a.lower() for a in (areas_preferidas or [])}
 
    def clave(c):
        coincide = len(areas & {a.lower() for a in c.get("areas", [])})
        return (-prioridad_total(c, malla), -coincide, c["codigo"])
 
    carga, total, carga_dif = [], 0, 0
    for c in sorted(habilitados, key=clave):
        if max_cursos is not None and len(carga) >= max_cursos:
            break
        dif = c.get("dificultad", DIFICULTAD_DEFECTO)
        if max_dificultad is not None and carga_dif + dif > max_dificultad:
            continue
        if total + c["creditos"] <= max_creditos:
            carga.append(c)
            total += c["creditos"]
            carga_dif += dif
    return carga, total
 
 
def sugerir_especialidad(intereses, especialidades):
    """Devuelve (especialidad, puntajes).
 
    Si ningún interés coincide con ninguna especialidad devuelve (None, puntajes).
    En caso de empate elige la primera por orden alfabético (resultado estable).
    """
    intereses = {i.strip().lower() for i in intereses}
    puntajes = {e["nombre"]: len(intereses & {a.lower() for a in e["areas"]})
                for e in especialidades}
    mejor = max(puntajes.values(), default=0)
    if mejor == 0:
        return None, puntajes
    return sorted(n for n, p in puntajes.items() if p == mejor)[0], puntajes
 
 
def planificar_roadmap(malla, aprobados, max_creditos=MAX_CREDITOS_DEFECTO,
                       areas_preferidas=None, max_ciclos=MAX_CICLOS_DEFECTO,
                       max_dificultad=MAX_DIFICULTAD_DEFECTO):
    """Plan por ciclos hasta terminar la malla. Devuelve (ciclos, pendientes)."""
    aprobados = set(aprobados)
    ciclos = []
    for numero in range(1, max_ciclos + 1):
        habilitados = cursos_habilitados(malla, aprobados)
        carga, total = armar_carga(habilitados, malla, max_creditos, areas_preferidas,
                                   max_dificultad=max_dificultad)
        if not carga:
            break
        codigos = [c["codigo"] for c in carga]
        ciclos.append({"ciclo": numero, "cursos": codigos, "creditos": total})
        aprobados.update(codigos)
    pendientes = [c["codigo"] for c in malla["cursos"] if c["codigo"] not in aprobados]
    return ciclos, pendientes
 
 
def generar_recomendacion(malla, estudiante, max_creditos=MAX_CREDITOS_DEFECTO,
                          max_ciclos=MAX_CICLOS_DEFECTO,
                          max_dificultad=MAX_DIFICULTAD_DEFECTO):
    """Une todo. 'cursos' y 'creditos' son los del próximo ciclo (como antes);
    'roadmap' trae el plan completo por ciclos."""
    errores = validar_malla(malla)
    if errores:
        raise ValueError("Malla inválida: " + " ".join(errores))
 
    advertencias = []
    conocidos = {c["codigo"] for c in malla["cursos"]}
    aprobados = [a for a in estudiante["aprobados"] if a in conocidos]
    ignorados = [a for a in estudiante["aprobados"] if a not in conocidos]
    if ignorados:
        advertencias.append("Cursos aprobados que no están en la malla (ignorados): "
                            + ", ".join(ignorados))
 
    esp, puntajes = sugerir_especialidad(estudiante.get("intereses", []),
                                         malla["especialidades"])
    if esp is None:
        advertencias.append("Ningún interés coincide con las especialidades; "
                            "no se sugiere una especialidad.")
        areas = []
    else:
        areas = next(e["areas"] for e in malla["especialidades"] if e["nombre"] == esp)
        mejor = puntajes[esp]
        empatadas = sorted(n for n, p in puntajes.items() if p == mejor)
        if len(empatadas) > 1:
            advertencias.append("Empate entre: " + ", ".join(empatadas)
                                + f". Se muestra {esp}.")
 
    ciclos, pendientes = planificar_roadmap(malla, aprobados, max_creditos, areas,
                                            max_ciclos, max_dificultad)
    if pendientes:
        advertencias.append("Quedan cursos sin ubicar en el plan: " + ", ".join(pendientes))
 
    return {
        "estudiante": estudiante["codigo"],
        "especialidad": esp,
        "puntajes": puntajes,
        "cursos": ciclos[0]["cursos"] if ciclos else [],
        "creditos": ciclos[0]["creditos"] if ciclos else 0,
        "roadmap": ciclos,
        "pendientes": pendientes,
        "advertencias": advertencias,
    }
