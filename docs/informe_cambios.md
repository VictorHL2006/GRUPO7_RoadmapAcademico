# Informe de cambios

## Alcance

Se retiró el frontend construido con React y Vite para dejar el backend Python y las vistas estáticas existentes. Para la parte de Román, completé las rutas de identidad, intereses, historial, recomendación, emisión, y verificación pública por UUID, y documenté el contrato actual de la API.

## Cambios realizados

- Eliminados los componentes, estilos y cliente API de React (`frontend/src/`), junto con `package.json`, `package-lock.json`, configuración de Vite y ESLint, la página de entrada React y su README de plantilla.
- Conservadas las pantallas HTML, CSS y JavaScript estáticas de `frontend/`.
- Actualizado el README raíz: ejecución sin Node.js, servidor estático en puerto 3000, endpoints reales y variables de entorno.
- Cambiado el enlace de verificación predeterminado de los PDFs al puerto 3000 para coincidir con el servidor estático.
- Añadida migración no destructiva que incorpora UUID de verificación y mantiene los IDs numéricos usados por las páginas existentes.
- Configurado CORS por `CORS_ORIGINS` y actualizado el `.env` local (ignorado por Git) para los orígenes 3000, el backend 8000 y la redirección del QR.
- Conservada compatibilidad con `/intereses` y `/roadmap/generar`; se agregaron los alias y endpoints nuevos de la guía.
- El README documenta los endpoints existentes, el esquema, variables de entorno, puertos y límites del despliegue actual.

## Verificación

`pytest -q`: 42 pruebas pasaron (38 pruebas de handlers/servicios API con dobles de base de datos y 4 del motor). La compilación de módulos Python terminó correctamente. La base PostgreSQL local no está activa, así que no se pudo ejecutar un recorrido integrado con persistencia real. La comprobación de secretos encontró que `.env`, llaves y firmas no están versionadas.

## Imagen de referencia

El diagrama de navegación existente del proyecto:

![Diagrama de navegación](diagramas/mapa_navegacion.png)
