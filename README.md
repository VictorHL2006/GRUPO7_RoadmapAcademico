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
| Aplicación | FastAPI + Uvicorn |
| Interfaz | HTML, CSS y JavaScript sin framework |
| Base de datos | PostgreSQL 15 |
| Criptografía | OpenSSL 3.x, librería cryptography |
| Otras librerías | qrcode, reportlab, psycopg2, python-multipart, pytest |
| Control de versiones | Git y GitHub |

## Requisitos
- Servidor: mínimo 4 vCPUs y 8 GB de RAM
- Python 3.11 o superior
- PostgreSQL 15 o superior
- OpenSSL 3.x
- Git
- Navegador web estándar (y cámara para escanear el QR)

## Instalación y ejecución

### 1. Clonar e instalar la aplicación Python
```bash
git clone https://github.com/VictorHL2006/GRUPO7_RoadmapAcademico.git
cd GRUPO7_RoadmapAcademico
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
touch .env                      # configurar las variables indicadas abajo
bash scripts/generar_llaves.sh  # crea keys/private.pem y keys/public_key.pem
```

### 2. Ejecutar el backend (puerto 8000)
Desde la raíz del repositorio:
```bash
uvicorn backend.main:app --port 8000
```
Comprobación: abrir http://localhost:8000/health

### 3. Ejecutar la interfaz HTML (puerto 3000)
```bash
cd frontend
python -m http.server 3000
```
Abrir http://localhost:3000. La interfaz consiste en páginas HTML, CSS y JavaScript sin React ni Vite.

### Variables de entorno
El backend lee estas variables del entorno o del archivo `.env` local:

| Variable | Uso | Valor predeterminado |
|----------|-----|----------------------|
| `DB_HOST` | Host de PostgreSQL | `localhost` |
| `DB_PORT` | Puerto de PostgreSQL | `5432` |
| `DB_NAME` | Base de datos | `roadmap_db` |
| `DB_USER` | Usuario de PostgreSQL | `roadmap_user` |
| `DB_PASSWORD` | Contraseña local de PostgreSQL | Vacío |
| `JWT_SECRET` | Secreto para firmar sesiones; mínimo 32 caracteres | Sin valor válido; debe configurarse |
| `PRIVATE_KEY_PATH` | Ruta de la llave privada RSA | `keys/private.pem` |
| `PUBLIC_KEY_PATH` | Ruta de la llave pública RSA | `keys/public_key.pem` |
| `MALLA_PATH` | Ruta del archivo de malla curricular | `data/malla.json` |
| `FRONTEND_URL` | URL incluida en el PDF al generar un roadmap | `http://localhost:3000` |

Para servir la interfaz local en el puerto 3000, configure `FRONTEND_URL=http://localhost:3000`.

### Rutas disponibles
| Método | Ruta | Acceso | Función |
|--------|------|--------|---------|
| `GET` | `/health` | Público | Estado de la API |
| `POST` | `/auth/registro` | Público | Registrar estudiante |
| `POST` | `/auth/login` | Público | Iniciar sesión y obtener JWT |
| `GET`, `PUT` | `/perfil` | Sesión | Consultar y actualizar perfil |
| `GET`, `POST` | `/historial` | Sesión | Consultar y agregar cursos aprobados |
| `GET`, `PUT` | `/intereses` | Estudiante | Consultar y guardar intereses |
| `POST` | `/roadmap/generar` | Estudiante | Generar y firmar un roadmap PDF |
| `GET` | `/roadmaps` | Sesión | Listar roadmaps propios |
| `GET` | `/roadmaps/{id}/pdf` | Propietario | Descargar PDF |
| `GET` | `/roadmaps/{id}/firma` | Propietario | Descargar firma `.sig` |
| `GET` | `/verificar/{id}` | Público | Verificar roadmap emitido por ID |
| `POST` | `/verificar` | Público | Verificar PDF y firma subidos |
| `GET` | `/tutor/estudiantes` | Tutor | Listar estudiantes y roadmaps |
| `GET` | `/tutor/estudiantes/{codigo}/roadmaps` | Tutor | Listar roadmaps de un estudiante |

La documentación interactiva de FastAPI está en `http://localhost:8000/docs`. La ruta `/auth/yo`, la emisión mediante `/roadmaps/emitir` y la verificación por código UUID descritas en la guía aún no existen con esos nombres en esta versión.

### 4. Pruebas
Desde la raíz del repositorio:
```bash
pytest -q
```

## Puertos
| Puerto | Uso | Estado |
|--------|-----|--------|
| 8000 | Backend (API REST) | Implementado |
| 5432 | PostgreSQL (solo local, no se expone) | Implementado |
| 4433 | Prueba de canal TLS 1.3 (openssl s_server) | Solo laboratorio |
| 3000 | Interfaz HTML estática | Disponible (`python -m http.server 3000`) |

Los puertos 80 (HTTP) y 21 (FTP) permanecen bloqueados; en producción se usa el 443 (HTTPS).

## Estructura del repositorio
```
backend/          código del servidor (API REST)
  recomendacion/  motor de recomendación
frontend/         páginas HTML, CSS y JavaScript sin framework
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
- API FastAPI con CORS, registro e inicio de sesión JWT, verificación manual y por ID, panel protegido para tutores y `/health`.
- Motor de recomendación con pruebas unitarias.
- Scripts de generación de llaves, firma, verificación y certificado TLS.
- Interfaz HTML para login, registro, panel, perfil, intereses, generación, roadmaps, visor, verificación y tutoría.

### En curso
- Cifrado AES-256-GCM de columnas sensibles.

### Pendiente
- Validar el flujo completo en el entorno local con PostgreSQL y navegador.

## Seguridad (qué no se sube al repositorio)
- Llaves y certificados (`*.pem`, `*.key`, `*.sig`).
- El archivo `.env` con contraseñas locales.
- Datos reales de estudiantes: solo se usan datos ficticios.
