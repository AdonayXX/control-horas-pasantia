from __future__ import annotations

from pathlib import Path
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from db import ReportEntry


def generate_report_pdf(entries: List[ReportEntry], output_path: Path, report_id: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(str(output_path), pagesize=A4, title=f"Reporte Horas #{report_id}")
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Reporte de horas de pasantía #{report_id}", styles["Title"]))
    elements.append(Spacer(1, 12))

    data = [["Semana", "Día", "Total de horas", "Observaciones"]]
    for e in entries:
        data.append([e.semana, e.dia, str(e.total_horas), e.observaciones or "-"])

    table = Table(data, colWidths=[90, 90, 90, 240], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("ALIGN", (3, 1), (3, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 28))
    elements.append(Paragraph("Firma manual: ____________________________", styles["Normal"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Nombre: _________________________________", styles["Normal"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Fecha: __________________________________", styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(
        Paragraph(
            "Firma digital: abre este PDF en un lector compatible (Adobe Acrobat/Foxit) y aplica una firma digital certificada en el área indicada.",
            styles["Italic"],
        )
    )

    doc.build(elements, onFirstPage=_draw_signature_box, onLaterPages=_draw_signature_box)


def _draw_signature_box(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.black)
    canvas.rect(50, 60, 220, 40, stroke=1, fill=0)
    canvas.setFont("Helvetica", 9)
    canvas.drawString(55, 84, "Área sugerida para firma digital")
    canvas.restoreState()
