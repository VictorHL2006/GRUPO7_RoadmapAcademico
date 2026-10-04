# GRUPO7_RoadmapAcademico

## Descripción
ROADMAP ACADÉMICO es un sistema de recomendación académica segura y certificación
digital. Genera un plan de estudios personalizado según el historial e intereses del
estudiante, y lo emite en un documento verificable criptográficamente (hash SHA-256
y firma digital RSA).

> Estado: en desarrollo. Este repositorio refleja el avance actual.

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
| Frontend | React + Vite |
| Base de datos | PostgreSQL 15 |
| Criptografía | OpenSSL 3.x, librería cryptography |
| Otras librerías | qrcode, reportlab, psycopg2, python-multipart, pytest |
| Control de versiones | Git y GitHub |

## Requisitos
- Servidor: mínimo 4 vCPUs y 8 GB de RAM
- Python 3.11 o superior
- Node.js y npm (para el frontend)
- PostgreSQL 15 o superior
- OpenSSL 3.x
- Git
- Navegador web estándar (y cámara para escanear el QR)

## Instalación y ejecución

### 1. Clonar e instalar el backend
```bash
git clone https://github.com/VictorHL2006/GRUPO7_RoadmapAcademico.git
cd GRUPO7_RoadmapAcademico
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # editar .env con valores locales
```

### 2. Ejecutar el backend (puerto 8000)
Desde la raíz del repositorio:
```bash
uvicorn backend.main:app --port 8000
```
Comprobación: abrir http://localhost:8000/health

### 3. Ejecutar el frontend (puerto 5173)
```bash
cd frontend
npm install
npm run dev
```
Abrir http://localhost:5173

Los comandos de base de datos y de generación de llaves se completarán cuando los
demás integrantes suban sus scripts.

## Puertos
| Puerto | Uso | Estado |
|--------|-----|--------|
| 8000 | Backend (API REST) | Implementado (base) |
| 5432 | PostgreSQL (solo local, no se expone) | Implementado |
| 4433 | Prueba de canal TLS 1.3 (openssl s_server) | Solo laboratorio |
| 5173 | Frontend (Vite) | En desarrollo |

Los puertos 80 (HTTP) y 21 (FTP) permanecen bloqueados; en producción se usa el 443 (HTTPS).

## Estructura del repositorio
```
backend/          código del servidor (API REST)
  recomendacion/  motor de recomendación
frontend/         interfaz de usuario (React + Vite)
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
- Backend base con el endpoint de verificación (`/verificar`) y de estado (`/health`).
- Frontend base (React + Vite).

### En curso
- Motor de recomendación, base de datos, scripts criptográficos e integración
  del frontend con el backend.

### Pendiente
- Generación de PDF con QR, portal de verificación completo y cifrado
  AES-256-GCM de columnas sensibles.

## Seguridad (qué no se sube al repositorio)
- Llaves y certificados (`*.pem`, `*.key`, `*.sig`).
- El archivo `.env` con contraseñas locales.
- Datos reales de estudiantes: solo se usan datos ficticios.
