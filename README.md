# Grupo7_RoadmapAcademico

## Descripción
ROADMAP ACADÉMICO es un sistema de recomendación académica segura y certificación
digital. Genera un plan de estudios personalizado según el historial e intereses del
estudiante, y lo emite en un documento verificable criptográficamente (hash SHA-256
y firma digital RSA).

## Integrantes
- Humpiri Lipa Victor Alejandro
- Minaya López Patrick Joel
- Quiroz Llanto Hugo Rolando
- Román Pinto Leroy Raúl

## Tecnologías
| Categoría | Tecnología |
|-----------|-----------|
| Lenguaje | Python 3.11 |
| Backend | FastAPI + Uvicorn |
| Base de datos | PostgreSQL 15 |
| Criptografía | OpenSSL 3.x, librería cryptography |
| Otras librerías | qrcode, reportlab, psycopg2, pytest |

## Requisitos
- Python 3.11 o superior
- Git
- OpenSSL 3.x
- PostgreSQL 15 o superior

## Instalación y ejecución
```bash
git clone https://github.com/VictorHL2006/GRUPO7_RoadmapAcademico.git
cd GRUPO7_RoadmapAcademico
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # editar .env con valores locales
```
Los comandos de base de datos, llaves y ejecución del backend se completarán cuando
los demás integrantes suban sus scripts.

## Estructura del repositorio
```
backend/          código del servidor (API REST)
  recomendacion/  motor de recomendación
frontend/         interfaz de usuario 
crypto/           utilidades criptográficas
database/         esquema SQL y datos de prueba
docs/diagramas/   diagramas del informe
data/             datos de ejemplo (ficticios)
keys/             llaves locales (NO se suben)
scripts/          scripts de llaves, firma y TLS
tests/            pruebas automáticas
```

## Estado del proyecto
### Hecho
- Estructura base del repositorio, .gitignore, .env.example y dependencias.
### En curso
- Motor de recomendación, base de datos, scripts criptográficos y backend.
### Pendiente
- Frontend, generación de PDF con QR, portal de verificación y cifrado
  AES-256-GCM de columnas sensibles.

## Seguridad (qué no se sube al repositorio)
- Llaves y certificados (`*.pem`, `*.key`, `*.sig`).
- El archivo `.env` con contraseñas locales.
- Datos reales de estudiantes: solo se usan datos ficticios.
