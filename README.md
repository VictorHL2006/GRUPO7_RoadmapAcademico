# Roadmap Académico

Aplicación académica con API Python/FastAPI, PostgreSQL y una interfaz de páginas HTML/CSS/JavaScript servida por Python. El frontend no usa React, Vite, Node ni npm.

## Requisitos

- Python 3.11 o superior
- PostgreSQL 15 o superior
- OpenSSL y Git Bash en Windows para los scripts de llaves
- Navegador web

## Instalación en Windows

Abre PowerShell en la carpeta del repositorio:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

Edita `.env` y reemplaza las contraseñas de ejemplo. `JWT_SECRET` debe tener al menos 32 caracteres aleatorios. No subas `.env` ni archivos de `keys/`.

Genera las llaves RSA desde Git Bash, en la raíz del repositorio:

```bash
bash scripts/generar_llaves.sh
```

El script crea `keys/private.pem` y `keys/public_key.pem` localmente.

## Preparar PostgreSQL

En `psql` como administrador, crea un usuario y las bases local y de pruebas:

```sql
CREATE USER roadmap_user WITH PASSWORD 'reemplazar_por_una_clave_local';
CREATE DATABASE roadmap_db OWNER roadmap_user;
CREATE DATABASE roadmap_test OWNER roadmap_user;
```

Si ya existen, no repitas esos comandos. Configura `DB_PASSWORD` en `.env` y aplica el esquema a la base de la aplicación:

```powershell
psql -U roadmap_user -h localhost -d roadmap_db -f database/schema.sql
```

El esquema crea las tablas que falten y agrega códigos UUID a roadmaps antiguos; no borra tablas existentes. Para añadir cuentas ficticias de estudiante y tutor, ejecuta:

```powershell
.\venv\Scripts\python.exe scripts\cargar_demo.py
```

Las contraseñas son las definidas en `DEMO_ESTUDIANTE_PASSWORD` y `DEMO_TUTOR_PASSWORD` del `.env` local.

## Ejecutar todo

Abre tres terminales en la raíz del repositorio.

**Terminal 1: PostgreSQL.** Confirma que el servicio PostgreSQL esté iniciado y que `roadmap_db` responda.

**Terminal 2: API Python.**

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Comprueba `http://localhost:8000/health`; la respuesta esperada es `{"estado":"ok"}`. La documentación de endpoints está en `http://localhost:8000/docs`.

**Terminal 3: interfaz Python estática.**

```powershell
Set-Location frontend
..\venv\Scripts\python.exe -m http.server 3000 --bind 127.0.0.1
```

Abre `http://localhost:3000`. La entrada conduce a `demo.html`, que comprueba la conexión con la API.

## Recorrido de prueba manual

1. En la demo, confirma que la API aparece conectada.
2. Registra un estudiante o inicia sesión con la cuenta E001 creada por `scripts/cargar_demo.py`.
3. En **Perfil**, guarda uno o más cursos con nota y periodo. En **Intereses**, selecciona áreas.
4. En **Generar**, calcula y revisa la recomendación; luego pulsa **Emitir PDF firmado**.
5. Abre el PDF, verifica el código y prueba el QR. La URL `/v/{codigo}` debe abrir el portal de verificación.
6. Cierra sesión e inicia como T001 para probar el panel de tutor y la descarga de roadmaps.
7. La verificación manual acepta un PDF y su firma `.sig`; si se altera el PDF debe aparecer como alterado.

Las contraseñas de las cuentas demo no se imprimen aquí: usa los valores locales de `.env`.

## Pruebas automáticas

Desde la raíz, con el entorno virtual activo o indicando su Python:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

La suite actual cubre handlers/servicios de API con dobles de base de datos, el motor de recomendación y comprobaciones estáticas de la interfaz. El recorrido manual anterior sí requiere que PostgreSQL esté iniciado y que se haya aplicado `database/schema.sql` a `roadmap_db`. Las futuras pruebas integradas deben usar `roadmap_test`, nunca la base de uso normal.

## Variables de entorno

`.env.example` contiene la plantilla completa. El backend reconoce:

| Variable | Propósito | Valor inicial |
|---|---|---|
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Conexión PostgreSQL | `localhost`, `5432`, `roadmap_db`, `roadmap_user`, definir localmente |
| `JWT_SECRET` | Firma de sesiones; mínimo 32 caracteres | Definir un secreto aleatorio |
| `PRIVATE_KEY_PATH`, `PUBLIC_KEY_PATH` | Llaves para firmar/verificar PDF | `keys/private.pem`, `keys/public_key.pem` |
| `MALLA_PATH` | Malla de cursos | `data/malla.json` |
| `MAX_CREDITOS` | Límite inicial de recomendación | `22` |
| `API_BASE_URL` | Origen del backend incluido en el QR | `http://localhost:8000` |
| `FRONTEND_URL` | Destino de la redirección del QR | `http://localhost:3000` |
| `CORS_ORIGINS` | Orígenes del navegador permitidos, separados por coma | `http://localhost:3000,http://127.0.0.1:3000` |
| `DEMO_ESTUDIANTE_PASSWORD`, `DEMO_TUTOR_PASSWORD` | Contraseñas locales de las cuentas ficticias | Definir antes de cargar las cuentas demo |

Si cambias los puertos, actualiza también `API_BASE_URL`, `FRONTEND_URL` y `CORS_ORIGINS` en `.env`.
Para escanear el QR desde otro dispositivo de la red local, reemplaza `localhost` en esas URLs por la IP de este equipo y permite esos orígenes en `CORS_ORIGINS`.

## Endpoints principales

| Método | Ruta | Acceso | Uso |
|---|---|---|---|
| `GET` | `/health` | Público | Estado de la API |
| `POST` | `/auth/registro` | Público | Registrar estudiante |
| `POST` | `/auth/login` | Público | Login y token JWT |
| `GET` | `/auth/yo` | Sesión | Identidad y rol |
| `GET`, `PUT` | `/perfil` | Sesión | Consultar/actualizar perfil |
| `GET`, `PUT` | `/perfil/intereses` | Estudiante | Consultar/guardar intereses |
| `GET`, `POST`, `PUT` | `/historial` | Sesión | Leer, agregar o reemplazar historial |
| `POST` | `/roadmaps/recomendar` | Estudiante | Vista previa de cursos |
| `POST` | `/roadmaps/emitir` | Estudiante | Guardar PDF firmado con UUID y QR |
| `GET` | `/roadmaps` | Sesión | Listar roadmaps propios |
| `GET` | `/roadmaps/{id_o_codigo}/pdf` y `/firma` | Propietario o tutor | Descargar documento/firma |
| `GET` | `/verificar/{id_o_codigo}` | Público | Verificar por ID o UUID |
| `POST` | `/verificar` | Público | Verificar PDF y firma subidos |
| `POST` | `/verificar/{codigo}/documento` | Público | Comparar PDF con emisión registrada |
| `GET` | `/v/{codigo}` | Público | Abrir portal de verificación desde el QR |
| `GET` | `/tutor/estudiantes` y `/tutor/estudiantes/{codigo}/roadmaps` | Tutor | Panel y roadmaps por estudiante |

La ruta anterior `POST /roadmap/generar` se conserva para compatibilidad con versiones previas de las páginas.

## Estado y límites actuales

- La emisión guarda el PDF, hash SHA-256, firma RSA desacoplada y UUID en PostgreSQL.
- El cifrado AES-256-GCM de correo, intereses y notas todavía está pendiente de integración.
- El servidor FastAPI de esta versión se ejecuta por HTTP local; el certificado de laboratorio no configura HTTPS en `backend.main`.
- La malla incluida es ficticia y debe reemplazarse por la malla académica autorizada con el mismo formato.

## Diagramas

- [Arquitectura de la aplicación](docs/diagramas/arquitectura.svg)
- [Emisión y verificación](docs/diagramas/emision_verificacion.svg)
- [Seguridad y estado de implementación](docs/diagramas/seguridad_estado.svg)
- [Mapa de navegación](docs/diagramas/mapa_navegacion.png)

## Estructura

```text
backend/          API, autenticación, servicios, PDF y motor
frontend/         páginas estáticas servidas por Python
database/         esquema PostgreSQL y datos de demostración
data/             malla y estudiantes ficticios
keys/             llaves locales ignoradas por Git
scripts/          generación de llaves y cuentas demo
tests/            pruebas del motor y handlers/servicios de API
docs/diagramas/   diagramas del sistema
```
