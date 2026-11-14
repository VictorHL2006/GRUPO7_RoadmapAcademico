import os

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.auth import usuario_actual
from backend.services import emitir_para_usuario, recomendar_para_usuario

router = APIRouter(tags=["roadmaps"])
MAX_CREDITOS = int(os.getenv("MAX_CREDITOS", "22"))


def _max_creditos():
    return Query(default=MAX_CREDITOS, ge=1, le=40)


def _recomendar(usuario: dict, max_creditos: int) -> dict:
    if usuario.get("rol") != "estudiante":
        raise HTTPException(status_code=403, detail="Solo un estudiante puede generar una recomendación")
    try:
        rec = recomendar_para_usuario(usuario["id"], max_creditos)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if rec is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return rec


def _emitir(usuario: dict, max_creditos: int) -> dict:
    if usuario.get("rol") != "estudiante":
        raise HTTPException(status_code=403, detail="Solo un estudiante puede emitir un roadmap")
    try:
        resultado = emitir_para_usuario(usuario["id"], max_creditos)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if resultado is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return resultado


@router.post("/roadmaps/recomendar")
def recomendar(max_creditos: int = _max_creditos(), usuario=Depends(usuario_actual)):
    """Calcula una recomendación sin emitir ni guardar un PDF."""
    return _recomendar(usuario, max_creditos)


@router.post("/roadmaps/emitir")
def emitir(max_creditos: int = _max_creditos(), usuario=Depends(usuario_actual)):
    """Emite un PDF firmado y guarda su código de verificación."""
    return _emitir(usuario, max_creditos)


@router.post("/roadmap/generar", include_in_schema=False)
def generar(max_creditos: int = _max_creditos(), usuario=Depends(usuario_actual)):
    """Ruta anterior conservada para las pantallas HTML actuales."""
    return _emitir(usuario, max_creditos)
