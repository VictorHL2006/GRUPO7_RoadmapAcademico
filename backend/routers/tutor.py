from fastapi import APIRouter, Depends, HTTPException
from backend.auth import exigir_tutor, usuario_actual
from backend.db import get_conn

router = APIRouter(prefix="/tutor", tags=["tutor"])


@router.get("/estudiantes")
def listar_estudiantes(usuario=Depends(usuario_actual)):
    exigir_tutor(usuario)
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("""
            SELECT u.codigo, u.nombre AS nombres,
                   (SELECT r.especialidad FROM roadmaps_emitidos r
                    WHERE r.usuario_id=u.id ORDER BY r.emitido_en DESC, r.id DESC LIMIT 1) AS especialidad,
                   COUNT(r.id)::int AS cantidad_roadmaps
            FROM usuarios u
            LEFT JOIN roadmaps_emitidos r ON r.usuario_id=u.id
            WHERE u.rol='estudiante'
            GROUP BY u.id, u.codigo, u.nombre
            ORDER BY u.nombre
        """)
        return [dict(zip(("codigo", "nombres", "especialidad", "cantidad_roadmaps"), row)) for row in cur.fetchall()]


@router.get("/estudiantes/{codigo}/roadmaps")
def listar_roadmaps_estudiante(codigo: str, usuario=Depends(usuario_actual)):
    exigir_tutor(usuario)
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute("""
            SELECT r.id, r.emitido_en, r.especialidad, r.creditos
            FROM roadmaps_emitidos r JOIN usuarios u ON u.id=r.usuario_id
            WHERE u.codigo=%s ORDER BY r.emitido_en DESC, r.id DESC
        """, (codigo.upper(),))
        return [{"id": row[0], "emitido": row[1].isoformat(), "especialidad": row[2], "creditos": row[3]}
                for row in cur.fetchall()]
