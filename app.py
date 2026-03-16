from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import List

from flask import Flask, abort, flash, redirect, render_template, request, send_file, url_for

from db import (
    ReportEntry,
    add_entries_to_report,
    create_report,
    delete_report,
    get_report,
    init_db,
    list_reports,
    update_report,
)
from pdf_utils import generate_report_pdf

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = Path(os.environ.get("REPORTS_DIR", BASE_DIR / "tmp" / "reports")).resolve()
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024

init_db()


def _parse_entries_from_form() -> List[ReportEntry]:
    semanas = request.form.getlist("semana[]")
    dias = request.form.getlist("dia[]")
    horas = request.form.getlist("horas[]")
    observaciones = request.form.getlist("observaciones[]")

    entries: List[ReportEntry] = []
    for i, (semana, dia, horas_raw, obs) in enumerate(zip(semanas, dias, horas, observaciones), start=1):
        if not any([semana.strip(), dia.strip(), horas_raw.strip(), obs.strip()]):
            continue

        if not semana.strip():
            raise ValueError(f"Fila {i}: la semana es obligatoria.")

        if not dia.strip():
            raise ValueError(f"Fila {i}: el día es obligatorio.")

        try:
            parsed = datetime.strptime(dia.strip(), "%Y/%m/%d")
            normalized_day = parsed.strftime("%Y/%m/%d")
        except ValueError as exc:
            raise ValueError(f"Fila {i}: día inválido, usa formato yyyy/mm/dd.") from exc

        try:
            total_horas = int(horas_raw)
        except ValueError as exc:
            raise ValueError(f"Fila {i}: total de horas debe ser entero.") from exc

        if total_horas < 0:
            raise ValueError(f"Fila {i}: total de horas no puede ser negativo.")

        entries.append(
            ReportEntry(
                semana=semana.strip(),
                dia=normalized_day,
                total_horas=total_horas,
                observaciones=obs.strip(),
            )
        )

    if not entries:
        raise ValueError("Debes ingresar al menos una fila con datos.")

    return entries


@app.get("/")
def index():
    reports = list_reports(limit=10)
    return render_template("index.html", reports=reports)


@app.post("/reports")
def create_report_view():
    try:
        entries = _parse_entries_from_form()
        report_id = create_report(entries)
        pdf_path = REPORTS_DIR / f"reporte_{report_id}.pdf"
        generate_report_pdf(entries, output_path=pdf_path, report_id=report_id)
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))

    flash("Reporte creado correctamente.", "success")
    return redirect(url_for("report_detail", report_id=report_id))


@app.get("/reports/<int:report_id>")
def report_detail(report_id: int):
    report = get_report(report_id)
    if not report:
        abort(404)

    return render_template("report_detail.html", report=report)


@app.post("/reports/<int:report_id>/entries")
def append_report_entries_view(report_id: int):
    report = get_report(report_id)
    if not report:
        abort(404)

    try:
        new_entries = _parse_entries_from_form()
        add_entries_to_report(report_id, new_entries)
        updated_report = get_report(report_id)
        pdf_path = REPORTS_DIR / f"reporte_{report_id}.pdf"
        generate_report_pdf(updated_report.entries, output_path=pdf_path, report_id=updated_report.id)
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("report_detail", report_id=report_id, _anchor="add-hours"))

    flash(f"Se agregaron {len(new_entries)} fila(s) al reporte #{report_id}.", "success")
    return redirect(url_for("report_detail", report_id=report_id))


@app.post("/reports/<int:report_id>/edit")
def edit_report_view(report_id: int):
    report = get_report(report_id)
    if not report:
        abort(404)

    report_number_raw = request.form.get("report_number", str(report_id)).strip()
    try:
        new_report_id = int(report_number_raw)
    except ValueError as exc:
        flash("El numero del reporte debe ser un entero.", "error")
        return redirect(url_for("report_detail", report_id=report_id, _anchor="edit-report"))

    try:
        entries = _parse_entries_from_form()
        final_report_id = update_report(report_id, entries, new_report_id=new_report_id)

        old_pdf_path = REPORTS_DIR / f"reporte_{report_id}.pdf"
        new_pdf_path = REPORTS_DIR / f"reporte_{final_report_id}.pdf"
        if report_id != final_report_id and old_pdf_path.exists():
            old_pdf_path.unlink()

        generate_report_pdf(entries, output_path=new_pdf_path, report_id=final_report_id)
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("report_detail", report_id=report_id, _anchor="edit-report"))

    if final_report_id != report_id:
        flash(f"Reporte actualizado y renumerado de #{report_id} a #{final_report_id}.", "success")
    else:
        flash(f"Reporte #{report_id} actualizado correctamente.", "success")

    return redirect(url_for("report_detail", report_id=final_report_id))


@app.post("/reports/<int:report_id>/delete")
def delete_report_view(report_id: int):
    deleted = delete_report(report_id)
    if not deleted:
        abort(404)

    pdf_path = REPORTS_DIR / f"reporte_{report_id}.pdf"
    if pdf_path.exists():
        pdf_path.unlink()

    flash(f"Reporte #{report_id} eliminado.", "success")
    return redirect(url_for("index"))


@app.get("/reports/<int:report_id>/download")
def download_report(report_id: int):
    report = get_report(report_id)
    if not report:
        abort(404)

    pdf_path = REPORTS_DIR / f"reporte_{report_id}.pdf"
    generate_report_pdf(report.entries, output_path=pdf_path, report_id=report.id)

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f"reporte_horas_{report_id}.pdf",
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
