@router.post("/roadmap/generar")
def generar(max_creditos: int = 22, usuario=Depends(usuario_actual)):
    estudiante = construir_estudiante(usuario["id"])
    rec = generar_recomendacion(MALLA, estudiante, max_creditos)
 
    id_roadmap = 101
    url = "http://localhost:3000/verificar.html?id=" + str(id_roadmap)
 
    pdf = generar_pdf(rec, url)
    hash_hex, firma = firmar_pdf(pdf)
 
    return {
        "id": id_roadmap, 
        "especialidad": rec["especialidad"], 
        "puntajes": rec["puntajes"],
        "cursos": rec["cursos"], 
        "creditos": rec["creditos"], 
        "hash": hash_hex
    }