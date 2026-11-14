import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import auth, perfil, roadmaps, tutor, verificacion
from backend.routes import intereses, roadmap

app = FastAPI(title="Roadmap Académico API")
app.include_router(auth.router)
app.include_router(perfil.router)
app.include_router(roadmaps.router)
app.include_router(tutor.router)
app.include_router(verificacion.router)
app.include_router(intereses.router)
app.include_router(roadmap.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health")
def health():
    return {"estado": "ok"}
