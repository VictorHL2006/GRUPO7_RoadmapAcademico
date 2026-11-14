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
cp .env.example .env            # luego edita .env (ver paso siguiente)
bash scripts/generar_llaves.sh  # crea keys/private.pem y keys/public_key.pem
```

En Windows PowerShell, activa el entorno con `venv\Scripts\Activate.ps1`. `.env` y `keys/` son locales y no se suben al repositorio.

Edita `.env` y completa como mínimo:
- `DB_PASSWORD`: la contraseña que usarás para `roadmap_user` en PostgreSQL.
- `JWT_SECRET`: mínimo 32 caracteres. Genéralo con:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- `DEMO_ESTUDIANTE_PASSWORD` y `DEMO_TUTOR_PASSWORD` (solo si cargarás las cuentas de demostración).

Si usas Git Bash en Windows, `bash scripts/generar_llaves.sh` requiere que OpenSSL esté en el PATH (`openssl version` debe funcionar).

### 2. Preparar PostgreSQL
Crear un usuario y dos bases, una para la aplicación y otra reservada para pruebas:
```sql
CREATE USER roadmap_user WITH PASSWORD 'cambia_esta_clave';
CREATE DATABASE roadmap_db OWNER roadmap_user;
CREATE DATABASE roadmap_test OWNER roadmap_user;
```
Desde la raíz, aplicar el esquema a `roadmap_db`:
```bash
psql -U roadmap_user -h localhost -d roadmap_db -f database/schema.sql
```
El esquema crea las tablas si faltan y añade el UUID de verificación a los roadmaps existentes; no borra las tablas ni sus datos. Configura `DB_PASSWORD` en `.env` con la contraseña que elegiste.
Opcionalmente, crea las cuentas ficticias para probar los roles:
```bash
python scripts/cargar_demo.py
```
Define `DEMO_ESTUDIANTE_PASSWORD` y `DEMO_TUTOR_PASSWORD` en `.env` con contraseñas locales propias antes de iniciar la demo.

### 3. Ejecutar el backend (puerto 8000)
Desde la raíz del repositorio:
```bash
uvicorn backend.main:app --port 8000
```
Comprobación: abrir http://localhost:8000/health

### 4. Ejecutar la interfaz HTML (puerto 3000)
```bash
cd frontend
python -m http.server 3000
```
Abrir http://localhost:3000/login.html. La interfaz consiste en páginas HTML, CSS y JavaScript sin React ni Vite.

El cliente de la API es `frontend/js/api.js`. Para apuntar a otro backend, define `window.API_URL` antes de cargarlo (por defecto `http://localhost:8000`); ese origen del frontend debe estar en `CORS_ORIGINS`.

**Cuentas de demostración** (tras `python scripts/cargar_demo.py`): estudiante `e001@example.com` y tutor `t001@example.com`, con las contraseñas definidas en `.env`.

**Flujo para probar a mano:** iniciar sesión → Perfil e historial → Intereses → Generar roadmap → Mis Roadmaps (descargar PDF y firma) → escanear el QR o abrir `verificar.html`. El tutor entra por el mismo login y ve el panel de estudiantes.

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
| `MAX_CREDITOS` | Tope predeterminado para recomendar y emitir | `22` |
| `API_BASE_URL` | Origen del backend usado por el QR de verificación | `http://localhost:8000` |
| `FRONTEND_URL` | Origen al que redirige el enlace corto `/v/{codigo}` | `http://localhost:3000` |
| `CORS_ORIGINS` | Orígenes permitidos separados por coma | `http://localhost:3000,http://127.0.0.1:3000` |
| `DEMO_ESTUDIANTE_PASSWORD` | Contraseña local de la cuenta ficticia E001 | Valor de desarrollo del script si no se define |
| `DEMO_TUTOR_PASSWORD` | Contraseña local de la cuenta ficticia T001 | Valor de desarrollo del script si no se define |

Al servir la interfaz en el puerto 3000, añade `CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000` a `.env`. Para probar desde otra dirección, agrega su origen a esa lista.

### Rutas disponibles
| Método | Ruta | Acceso | Función |
|--------|------|--------|---------|
| `GET` | `/health` | Público | Estado de la API |
| `POST` | `/auth/registro` | Público | Registrar estudiante |
| `POST` | `/auth/login` | Público | Iniciar sesión y obtener JWT |
| `GET` | `/auth/yo` | Sesión | Obtener la identidad del usuario actual |
| `GET`, `PUT` | `/perfil` | Sesión | Consultar y actualizar perfil |
| `GET`, `PUT` | `/perfil/intereses` | Estudiante | Consultar y guardar intereses (alias de `/intereses`) |
| `GET`, `POST` | `/historial` | Sesión | Consultar y agregar cursos aprobados |
| `PUT` | `/historial` | Sesión | Reemplazar el historial completo |
| `GET`, `PUT` | `/intereses` | Estudiante | Consultar y guardar intereses |
| `POST` | `/roadmaps/recomendar` | Estudiante | Recomendar sin emitir un documento |
| `POST` | `/roadmaps/emitir` | Estudiante | Generar, firmar y guardar un PDF con UUID y QR |
| `GET` | `/roadmaps` | Sesión | Listar roadmaps propios |
| `GET` | `/roadmaps/{id_o_codigo}/pdf` | Propietario o tutor | Descargar PDF por ID o código UUID |
| `GET` | `/roadmaps/{id_o_codigo}/firma` | Propietario o tutor | Descargar firma `.sig` por ID o código UUID |
| `GET` | `/verificar/{id_o_codigo}` | Público | Verificar estado por ID o código UUID |
| `POST` | `/verificar` | Público | Verificar PDF y firma subidos |
| `POST` | `/verificar/{codigo}/documento` | Público | Comparar un PDF con el roadmap emitido |
| `GET` | `/v/{codigo}` | Público | Redirigir el QR al portal HTML de verificación |
| `GET` | `/tutor/estudiantes` | Tutor | Listar estudiantes y roadmaps |
| `GET` | `/tutor/estudiantes/{codigo}/roadmaps` | Tutor | Listar roadmaps de un estudiante |

La documentación interactiva de FastAPI está en `http://localhost:8000/docs`. La ruta anterior `/roadmap/generar` se conserva para las páginas HTML existentes.

### 5. Pruebas
Desde la raíz del repositorio:
```bash
pytest -q
```
La suite local actual prueba los handlers con dobles de base de datos. Para futuras pruebas integradas, usa exclusivamente `roadmap_test`, nunca `roadmap_db`.

## Diagramas
En `docs/diagramas/` (fuente `.dot` + PNG):
- `mapa_navegacion.png`: pantallas y roles.
- `arquitectura_general.png`: componentes, PDF/QR, firma, cifrado y HTTPS.
- `flujo_emision.png`: emisión de un roadmap firmado.
- `flujo_verificacion.png`: verificación por código QR, por archivos y por documento subido.

Los elementos aún no implementados aparecen con línea punteada.

## Puertos
| Puerto | Uso | Estado |
|--------|-----|--------|
| 8000 | Backend (API REST) | Implementado |
| 5432 | PostgreSQL (solo local, no se expone) | Implementado |
| 3000 | Interfaz HTML estática | Disponible (`python -m http.server 3000`) |

La API local se sirve por HTTP en el puerto 8000. El despliegue HTTPS no se configura desde esta versión de `backend.main`.

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
- Estructura base del repositorio, `.gitignore` y dependencias.
- API FastAPI con CORS configurable, registro/login JWT, perfil, historial, intereses, recomendación y emisión de PDF firmado, verificación por archivos o código, panel protegido para tutores y `/health`.
- Motor de recomendación con pruebas unitarias.
- Scripts de generación de llaves, firma, verificación y certificado TLS.
- Interfaz HTML para login, registro, panel, perfil, intereses, generación, roadmaps, visor, verificación y tutoría.

### En curso
- Cifrado AES-256-GCM de correo, intereses y notas, correspondiente al módulo de criptografía.

### Pendiente
- Ejecutar las pruebas integradas de la API y el recorrido completo con PostgreSQL en una instalación local.

## Seguridad (qué no se sube al repositorio)
- Llaves y certificados (`*.pem`, `*.key`, `*.sig`).
- El archivo `.env` con contraseñas locales; solo se sube `.env.example`, sin valores reales.
- Datos reales de estudiantes: solo se usan datos ficticios.
- Cada integrante genera sus propias llaves y secretos (`generar_llaves.sh`, `JWT_SECRET`).

**Sobre el token de sesión:** el frontend guarda el token JWT en `sessionStorage`, que se borra al cerrar la pestaña. Es suficiente para este proyecto, pero si alguna página tuviera una falla XSS, el token quedaría expuesto.

## Limitaciones conocidas (no implementado en esta versión)
| Tema | Estado |
|------|--------|
| Firma incrustada en el PDF (PAdES) | No se hace: la firma es desacoplada, guardada en la base y descargable como `.sig`. |
| Recuperación de contraseña | No disponible en esta versión. |
| Límite de intentos de inicio de sesión | No implementado; es una mejora recomendada antes de un uso real. |
| Cifrado en reposo de disco y copias de seguridad | Fuera del alcance. |
| Rotación de la clave de cifrado | No implementada: cambiar `ENCRYPTION_KEY` exige volver a cifrar los datos. |
| Despliegue en la nube y HTTPS | No se hizo. El sistema corre en local por HTTP; HTTPS usaría un certificado autofirmado de laboratorio. |
| Hash de contraseñas | Se usa PBKDF2-HMAC-SHA256 con sal (200 000 iteraciones, biblioteca estándar), no Argon2 ni bcrypt. |
