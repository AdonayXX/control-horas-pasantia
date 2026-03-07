from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from db import ReportEntry


def generate_report_pdf(entries: List[ReportEntry], output_path: Path, report_id: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        title=f"Reporte Horas #{report_id}",
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        alignment=TA_LEFT,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#475569"),
        alignment=TA_LEFT,
    )
    header_cell_style = ParagraphStyle(
        "HeaderCell",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.white,
    )
    body_cell_center = ParagraphStyle(
        "BodyCellCenter",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111827"),
    )
    body_cell_left = ParagraphStyle(
        "BodyCellLeft",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=12,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#111827"),
    )
    note_style = ParagraphStyle(
        "Note",
        parent=styles["Italic"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
    )

    created_at = datetime.now().strftime("%Y/%m/%d %H:%M")

    elements = [
        Paragraph(f"Reporte de horas de pasantía #{report_id}", title_style),
        Paragraph(f"Generado: {created_at}", subtitle_style),
        Spacer(1, 12),
    ]

    data = [
        [
            Paragraph("Semana", header_cell_style),
            Paragraph("Día", header_cell_style),
            Paragraph("Total de horas", header_cell_style),
            Paragraph("Observaciones", header_cell_style),
        ]
    ]

    for entry in entries:
        data.append(
            [
                Paragraph(entry.semana, body_cell_center),
                Paragraph(entry.dia, body_cell_center),
                Paragraph(str(entry.total_horas), body_cell_center),
                Paragraph(entry.observaciones or "-", body_cell_left),
            ]
        )

    table = Table(
        data,
        colWidths=[30 * mm, 30 * mm, 30 * mm, 74 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )

    table_style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (2, -1), "CENTER"),
        ("ALIGN", (3, 1), (3, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
    ]

    for row_idx in range(1, len(data)):
        row_bg = colors.HexColor("#F8FAFC") if row_idx % 2 == 0 else colors.white
        table_style_commands.append(("BACKGROUND", (0, row_idx), (-1, row_idx), row_bg))

    table.setStyle(TableStyle(table_style_commands))

    elements.append(table)
    elements.append(Spacer(1, 18))

    signature_table = Table(
        [
            ["Firma manual", "Nombre", "Fecha"],
            ["\n", "\n", "\n"],
        ],
        colWidths=[55 * mm, 55 * mm, 54 * mm],
        hAlign="LEFT",
    )
    signature_table.setStyle(
        TableStyle(
            [
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("LINEBELOW", (0, 1), (-1, 1), 0.9, colors.HexColor("#475569")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )

    elements.append(signature_table)
    elements.append(Spacer(1, 14))
    elements.append(
        Paragraph(
            "Firma digital: utiliza el recuadro al pie de página en Adobe Acrobat/Foxit para aplicar una firma digital certificada.",
            note_style,
        )
    )

    doc.build(elements, onFirstPage=_draw_page_decorations, onLaterPages=_draw_page_decorations)


def _draw_page_decorations(canvas, doc) -> None:
    canvas.saveState()

    width, _ = A4

    # Franja superior sutil
    canvas.setFillColor(colors.HexColor("#E2E8F0"))
    canvas.rect(doc.leftMargin, A4[1] - 16 * mm, width - doc.leftMargin - doc.rightMargin, 1.3, fill=1, stroke=0)

    # Recuadro para firma digital alineado al pie
    box_x = doc.leftMargin
    box_y = doc.bottomMargin - 2 * mm
    box_w = 74 * mm
    box_h = 16 * mm

    canvas.setStrokeColor(colors.HexColor("#334155"))
    canvas.setLineWidth(0.9)
    canvas.roundRect(box_x, box_y, box_w, box_h, 2.5, stroke=1, fill=0)
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(colors.HexColor("#334155"))
    canvas.drawString(box_x + 4, box_y + box_h - 6.5, "Área de firma digital")

    # Numeración de página
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawRightString(width - doc.rightMargin, doc.bottomMargin - 6 * mm, f"Página {canvas.getPageNumber()}")

    canvas.restoreState()
