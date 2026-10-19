from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List

router = APIRouter()

class InteresesIn(BaseModel):
    intereses: List[str]

@router.put("/intereses")
def guardar_intereses(datos: InteresesIn, usuario=Depends(usuario_actual)):
    return {"mensaje": "Intereses guardados"}