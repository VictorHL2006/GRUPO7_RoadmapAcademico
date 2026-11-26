# Roadmap Académico

Aplicación académica con API FastAPI, PostgreSQL y páginas HTML/CSS/JavaScript estáticas. No requiere Node.js, npm ni un proceso de compilación del frontend.

## Instalación y despliegue

La guía detallada para instalar el proyecto en otro equipo, ejecutarlo en la red local y desplegarlo en un servidor está en [docs/INSTALACION_DESPLIEGUE.md](docs/INSTALACION_DESPLIEGUE.md).

## Requisitos

- Python 3.11 o superior.
- PostgreSQL 15 o superior.
- Git y OpenSSL/Git Bash para generar las llaves RSA.
- Navegador web moderno.

## Inicio rápido en Windows

Desde PowerShell, en la raíz del repositorio:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env`, configura una contraseña PostgreSQL y reemplaza `JWT_SECRET` por un secreto aleatorio de al menos 32 caracteres. Crea una base de datos y un usuario PostgreSQL, y aplica el esquema no destructivo:

```powershell
psql -U postgres -h localhost -c "CREATE USER roadmap_user WITH PASSWORD 'TU_CLAVE';"
psql -U postgres -h localhost -c "CREATE DATABASE roadmap_db OWNER roadmap_user;"
psql -U roadmap_user -h localhost -d roadmap_db -f database/schema.sql
```

Desde Git Bash en la raíz del proyecto, genera las llaves:

```bash
bash scripts/generar_llaves.sh
```

Inicia API e interfaz en dos terminales:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

```powershell
Set-Location frontend
..\.venv\Scripts\python.exe -m http.server 3000 --bind 127.0.0.1
```

Abre `http://localhost:3000`. Para usar datos ficticios, configura `DEMO_ESTUDIANTE_PASSWORD` y `DEMO_TUTOR_PASSWORD` en `.env` y ejecuta desde la raíz:

```powershell
.\.venv\Scripts\python.exe scripts/cargar_demo.py
```

No uses contraseñas de demostración al exponer el servicio fuera de una red de confianza.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Configuración

`.env.example` es la plantilla de las variables locales. Las principales son:

| Variable | Uso |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Conexión PostgreSQL |
| `JWT_SECRET` | Firma de sesiones; mínimo 32 caracteres aleatorios |
| `PRIVATE_KEY_PATH`, `PUBLIC_KEY_PATH` | Llaves RSA para firma/verificación de PDFs |
| `MALLA_PATH` | Archivo JSON de cursos y prerrequisitos |
| `MAX_CREDITOS` | Límite de créditos recomendado |
| `API_BASE_URL` | URL de API incluida en el QR del PDF |
| `FRONTEND_URL` | URL de frontend a la que redirige el QR |
| `CORS_ORIGINS` | Orígenes del frontend autorizados, separados por coma |
| `DEMO_ESTUDIANTE_PASSWORD`, `DEMO_TUTOR_PASSWORD` | Claves de usuarios ficticios |

Los scripts y la API cargan `.env`; ejecuta los comandos desde la raíz del repositorio para que las rutas relativas funcionen correctamente.

## Alcance y limitaciones

- La firma RSA se guarda separada del PDF; no es una firma PAdES embebida.
- `crypto/cifrado.py` contiene funciones de cifrado, pero la API actual persiste correo, intereses y notas sin integrarlas. No se debe considerar listo para producción con datos personales reales.
- La malla incluida es ficticia y debe sustituirse por la malla académica autorizada.
- El servidor de desarrollo usa HTTP. El despliegue público requiere HTTPS, servidor de producción, proxy inverso y controles adicionales.

## Estructura

```text
backend/          API, autenticación, servicios, PDF y motor de recomendación
frontend/         páginas estáticas
database/         esquema PostgreSQL y datos de demostración
data/             malla ficticia
keys/             llaves locales ignoradas por Git
scripts/          utilidades de instalación y cuentas demo
tests/            pruebas automatizadas
docs/             manual y diagramas
```
