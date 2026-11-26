# Manual de instalación y despliegue

Esta guía instala Roadmap Académico en otro equipo. Describe el modo local y el acceso desde otros dispositivos conectados a la misma red. El frontend es estático y no necesita Node.js.

## 1. Requisitos del equipo

- Windows 10/11, Linux o macOS.
- Python 3.11 o posterior.
- PostgreSQL 15 o posterior, iniciado como servicio.
- Git para descargar el repositorio.
- Git Bash y OpenSSL en Windows para generar las llaves RSA (en Linux/macOS basta OpenSSL).
- Acceso de red/firewall a los puertos 3000 y 8000 para dispositivos LAN.

## 2. Descargar e instalar dependencias

Clona el repositorio y entra a su carpeta:

```bash
git clone <URL_DEL_REPOSITORIO>
cd GRUPO7_RoadmapAcademico
```

Crea un entorno Python, instala paquetes y copia la plantilla de configuración. En Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

En Linux/macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Edita `.env`. Cambia `DB_PASSWORD` y `JWT_SECRET`; el secreto JWT debe tener al menos 32 caracteres aleatorios. Para un uso no local, también configura `DEMO_ESTUDIANTE_PASSWORD` y `DEMO_TUTOR_PASSWORD` con claves propias. No compartas `.env` ni la llave privada.

## 3. Crear la base de datos

Como administrador de PostgreSQL, crea un usuario y la base de datos. Sustituye la contraseña de ejemplo por una propia y usa la misma en `DB_PASSWORD` de `.env`:

```sql
CREATE USER roadmap_user WITH PASSWORD 'CAMBIAR_ESTA_CLAVE';
CREATE DATABASE roadmap_db OWNER roadmap_user;
```

Ejecuta `psql` desde la raíz del proyecto para aplicar el esquema:

```bash
psql -U roadmap_user -h localhost -d roadmap_db -f database/schema.sql
```

El esquema es idempotente para instalaciones actuales: se puede volver a ejecutar y no elimina tablas ni datos. Si vas a actualizar una instalación antigua, haz antes un respaldo de PostgreSQL.

## 4. Crear las llaves RSA

Desde la raíz del repositorio:

```bash
bash scripts/generar_llaves.sh
```

Se crearán `keys/private_key.pem` y `keys/public_key.pem`. La llave privada firma los documentos y debe conservarse en el servidor; la pública se usa al verificar. Las llaves no se incluyen en Git. Cada servidor que necesite verificar documentos emitidos previamente debe conservar la llave pública correspondiente y configurar `PUBLIC_KEY_PATH`.

## 5. Cargar usuarios ficticios (opcional)

Configura las dos variables `DEMO_*_PASSWORD` en `.env` y ejecuta:

```bash
python scripts/cargar_demo.py
```

Usa `.venv\Scripts\python.exe` en PowerShell si el entorno virtual no está activado. Esto crea/actualiza estudiante E001 y tutor T001. Para crear una cuenta individual:

```bash
python scripts/crear_usuario.py --codigo T002 --nombres "Tutor de prueba" --correo tutor2@example.com --rol tutor
```

## 6. Ejecutar localmente

Desde la raíz, inicia la API:

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

En otra terminal sirve el frontend:

```bash
python -m http.server 3000 --directory frontend --bind 127.0.0.1
```

En PowerShell, si Python no está activado, usa la ruta al ejecutable dentro de `.venv`. Abre `http://localhost:3000`. Comprueba la API en `http://localhost:8000/health`; debe responder `{"estado":"ok"}`. La documentación de la API está en `http://localhost:8000/docs`.

## 7. Acceder desde otro dispositivo de la misma red

1. Conecta el servidor y el otro dispositivo a la misma red. Obtén la IPv4 privada del servidor, por ejemplo `192.168.1.50` (`ipconfig` en Windows, `ip addr` en Linux).
2. En `.env` del servidor reemplaza `localhost` por esa IP:

   ```dotenv
   API_BASE_URL=http://192.168.1.50:8000
   FRONTEND_URL=http://192.168.1.50:3000
   CORS_ORIGINS=http://192.168.1.50:3000,http://localhost:3000,http://127.0.0.1:3000
   ```

   Sustituye la IP del ejemplo por la IPv4 real. `API_BASE_URL` determina el destino de los QR emitidos. `FRONTEND_URL` determina la página a la que abre el QR. La interfaz selecciona la API usando el hostname desde el cual se cargó.
3. Reinicia la API tras editar `.env` y enlázala a todas las interfaces:

   ```bash
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

4. En otra terminal sirve la interfaz en todas las interfaces:

   ```bash
   python -m http.server 3000 --directory frontend --bind 0.0.0.0
   ```

5. Permite conexiones entrantes TCP a los puertos 3000 y 8000 en el firewall del servidor, solo para la red privada/local. Desde el otro dispositivo abre `http://192.168.1.50:3000` (con la IP real). Comprueba `http://192.168.1.50:8000/health`.

La IP debe permanecer estable mientras se usa el servicio; para una instalación recurrente, reserva una dirección DHCP en el router. La API se conecta a PostgreSQL en el mismo equipo por defecto. Si PostgreSQL está en otra máquina, cambia `DB_HOST` y permite allí el acceso de red para el usuario de la aplicación.

## 8. Verificación funcional

- La pantalla inicial indica que la API está conectada.
- Registra un estudiante o inicia con un usuario demo.
- Guarda historial e intereses y genera una recomendación.
- Emite un PDF firmado y comprueba su código o QR.
- Inicia sesión con una cuenta de tutor para comprobar el panel.

## 9. Detener y respaldar

Detén cada servidor con `Ctrl+C`. Respalda PostgreSQL con `pg_dump` y guarda en un lugar seguro `keys/private_key.pem`, la configuración `.env` y la llave pública. No envíes la llave privada por correo o repositorios.

## Nota de despliegue público

Los comandos de esta guía son adecuados para laboratorio o una red local de confianza. `http.server` y el servidor de desarrollo Uvicorn no son servidores de producción; además, HTTP expone credenciales y tokens en tránsito. Para publicar en Internet, usa HTTPS con un proxy inverso y servidores de producción, limita CORS a los dominios reales, protege PostgreSQL y completa la integración del cifrado de los datos personales antes de usar datos reales.
