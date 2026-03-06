# Control de Horas de Pasantía

Aplicación web para registrar horas de pasantía y generar un PDF descargable con estas 4 columnas:

- Semana
- Día (`yyyy/mm/dd`)
- Total de horas (entero)
- Observaciones

Además, el PDF contempla **firma manual** (líneas de firma) y un **área sugerida para firma digital** en lectores compatibles.

## Requisitos

- Python 3.10+

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir `http://localhost:5000`.

## Persistencia

Los reportes se guardan en SQLite (`database.sqlite3`) con sus filas asociadas.

## PDF

Cada reporte genera un archivo PDF en `tmp/reports/reporte_<id>.pdf`, y puede descargarse desde la vista de detalle.
