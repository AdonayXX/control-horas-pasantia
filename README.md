# Control de Horas de Pasantía

Aplicación web para registrar horas de pasantía y generar un PDF descargable con estas 4 columnas:

- Semana
- Día (`yyyy/mm/dd`)
- Total de horas (entero)
- Observaciones

Además, el PDF contempla **firma manual** (líneas de firma) y un **área sugerida para firma digital** en lectores compatibles.

## Ejecutar localmente (desarrollo)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir `http://localhost:5000`.

## Variables de entorno

- `SECRET_KEY`: clave de sesión de Flask.
- `DATABASE_PATH`: ruta del SQLite (por defecto `./database.sqlite3`).
- `REPORTS_DIR`: carpeta donde se guardan los PDF (por defecto `./tmp/reports`).

## Despliegue en Dokploy (Docker)

Sí, **la puedes subir a Dokploy**.

### 1) Subir el código a GitHub/GitLab

Sube este repositorio a una rama principal (`main`/`master`) para que Dokploy pueda hacer pull.

### 2) Crear la aplicación en Dokploy

1. En Dokploy, entra a tu proyecto.
2. Click en **Create Application**.
3. Fuente: **Git Repository**.
4. Conecta GitHub/GitLab y selecciona este repo + rama.
5. Build type: **Dockerfile** (Dokploy detecta el archivo automáticamente).

### 3) Configurar variables de entorno

En la sección **Environment Variables** agrega:

- `SECRET_KEY` = una clave larga y privada.
- `DATABASE_PATH` = `/data/database.sqlite3`
- `REPORTS_DIR` = `/data/reports`

### 4) Configurar persistencia (muy importante)

En **Volumes** crea un volumen persistente y móntalo en:

- Host/Volume: (el que definas en Dokploy)
- Container path: `/data`

Esto evita perder:

- la base SQLite (`/data/database.sqlite3`)
- los PDFs generados (`/data/reports`)

### 5) Red, puertos y dominio

- Puerto interno de la app: `5000`.
- Si usas dominio, configura el dominio en Dokploy y habilita TLS.

### 6) Deploy

Haz click en **Deploy**. Si todo está bien, debe iniciar con Gunicorn usando:

```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

### 7) Verificación rápida post-deploy

- Healthcheck: `GET /health` debe responder `{"status":"ok"}`.
- Abre la raíz `/` y crea un reporte de prueba.
- Descarga el PDF para confirmar escritura en volumen.
- Reinicia/redeploy y valida que el reporte siga existiendo.

## Solución de problemas en Dokploy

- Si no abre la app: revisa que el puerto interno sea `5000`.
- Si los reportes se pierden: faltó montar volumen en `/data`.
- Si falla sesión/login flash: verifica que `SECRET_KEY` esté definida.

## Persistencia

Los reportes se guardan en SQLite y cada fila queda asociada al reporte.

## PDF

Cada reporte genera un archivo PDF `reporte_<id>.pdf` descargable desde la vista de detalle.
