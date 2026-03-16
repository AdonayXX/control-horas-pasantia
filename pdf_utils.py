from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import List
from xml.sax.saxutils import escape

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, KeepTogether, LongTable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from db import ReportEntry

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
PT_LOGO_PATH = STATIC_DIR / "pt.png"
UTN_LOGO_PATH = STATIC_DIR / "utn.png"


def generate_report_pdf(entries: List[ReportEntry], output_path: Path, report_id: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total_horas = sum(entry.total_horas for entry in entries)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        title=f"Reporte Horas #{report_id}",
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )
    styles = getSampleStyleSheet()
    elements = []
    available_width = doc.width

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=17,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=0,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["BodyText"],
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#4b5563"),
    )
    header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.black,
    )
    centered_cell_style = ParagraphStyle(
        "CenteredCell",
        parent=styles["BodyText"],
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        splitLongWords=True,
    )
    text_cell_style = ParagraphStyle(
        "TextCell",
        parent=styles["BodyText"],
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
        splitLongWords=True,
    )
    label_style = ParagraphStyle(
        "SignatureLabel",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
    )
    note_style = ParagraphStyle(
        "SignatureNote",
        parent=styles["Italic"],
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#444444"),
    )
    digital_box_style = ParagraphStyle(
        "DigitalBox",
        parent=styles["BodyText"],
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#444444"),
    )

    elements.append(
        _build_report_header(
            available_width=available_width,
            report_id=report_id,
            title_style=title_style,
            subtitle_style=subtitle_style,
        )
    )
    elements.append(Spacer(1, 16))

    semana_width = available_width * 0.17
    dia_width = available_width * 0.17
    horas_width = available_width * 0.14
    observaciones_width = available_width - semana_width - dia_width - horas_width

    data = [
        [
            Paragraph("Semana", header_style),
            Paragraph("Día", header_style),
            Paragraph("Total de horas", header_style),
            Paragraph("Observaciones", header_style),
        ]
    ]
    for e in entries:
        data.append(
            [
                _as_paragraph(e.semana, centered_cell_style),
                _as_paragraph(e.dia, centered_cell_style),
                _as_paragraph(str(e.total_horas), centered_cell_style),
                _as_paragraph(e.observaciones or "-", text_cell_style),
            ]
        )

    total_row_index = len(data)
    data.append(
        [
            _as_paragraph("Total de horas", header_style),
            "",
            _as_paragraph(str(total_horas), centered_cell_style),
            "",
        ]
    )

    table = LongTable(
        data,
        colWidths=[semana_width, dia_width, horas_width, observaciones_width],
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                ("SPAN", (0, total_row_index), (1, total_row_index)),
                ("BACKGROUND", (0, total_row_index), (-1, total_row_index), colors.HexColor("#eef2f3")),
                ("FONTNAME", (0, total_row_index), (-1, total_row_index), "Helvetica-Bold"),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 24))
    elements.append(
        KeepTogether(
            [
                _build_signature_table(
                    available_width=available_width,
                    label_style=label_style,
                    normal_style=styles["Normal"],
                ),
            ]
        )
    )

    doc.build(elements)


def _build_report_header(
    available_width: float,
    report_id: int,
    title_style: ParagraphStyle,
    subtitle_style: ParagraphStyle,
) -> Table:
    header = Table(
        [
            [
                _build_logo(PT_LOGO_PATH, target_height=22 * mm, max_width=28 * mm, tint_hex="#124f36"),
                [
                    Paragraph("Control de Horas de Pasantía", title_style),
                    Spacer(1, 3),
                    Paragraph(f"Reporte de horas de pasantía #{report_id}", subtitle_style),
                ],
                _build_logo(UTN_LOGO_PATH, target_height=20 * mm, max_width=48 * mm),
            ]
        ],
        colWidths=[available_width * 0.18, available_width * 0.47, available_width * 0.35],
        hAlign="LEFT",
    )
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("ALIGN", (1, 0), (1, 0), "CENTER"),
                ("ALIGN", (2, 0), (2, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return header


def _build_signature_table(
    available_width: float,
    label_style: ParagraphStyle,
    normal_style: ParagraphStyle,
) -> Table:
    signature_image_path = _resolve_image_path("firma")
    name_image_path = _resolve_image_path("nombre")

    left_cell = [
        Paragraph("Firma y Nombre", label_style),
        Spacer(1, 10),
        _build_signature_asset(signature_image_path, width=available_width * 0.4, max_height=25 * mm),
        Spacer(1, -8),
        Paragraph("______________________________", normal_style),
        Spacer(1, 6),
        _build_signature_asset(name_image_path, width=available_width * 0.45, max_height=16 * mm),
        Spacer(1, -8),
        Paragraph("______________________________", normal_style),
    ]

    signature_table = Table(
        [[left_cell]],
        colWidths=[available_width],
        hAlign="LEFT",
    )
    signature_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return signature_table


def _build_signature_asset(path: Path, width: float, max_height: float):
    if not path.exists():
        return Paragraph("______________________________", getSampleStyleSheet()["Normal"])

    image_source = _prepare_signature_source(path)
    original_width, original_height = ImageReader(image_source).getSize()
    scale = width / original_width
    scaled_width = width
    scaled_height = original_height * scale

    if scaled_height > max_height:
        resize_ratio = max_height / scaled_height
        scaled_width *= resize_ratio
        scaled_height *= resize_ratio

    return Image(image_source, width=scaled_width, height=scaled_height)


def _prepare_signature_source(path: Path):
    """Convert near-black or near-white background pixels to transparent for cleaner signatures and crop to ink."""
    with PILImage.open(path).convert("RGBA") as img:
        pixels = img.getdata()
        processed = []
        for r, g, b, a in pixels:
            # Tolerancia para considerar un píxel como "fondo negro"
            if r < 30 and g < 30 and b < 30:
                processed.append((r, g, b, 0))
            # Tolerancia para considerar un píxel como "fondo blanco"
            elif r > 220 and g > 220 and b > 220:
                processed.append((255, 255, 255, 0))
            else:
                processed.append((r, g, b, a))

        img.putdata(processed)
        
        # Recortar la imagen al tamaño real del contenido (ignorando fondo transparente)
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer


def _resolve_image_path(base_name: str) -> Path:
    for ext in (".png", ".jpg", ".jpeg"):
        candidate = STATIC_DIR / f"{base_name}{ext}"
        if candidate.exists():
            return candidate
    return STATIC_DIR / f"{base_name}.png"


def _build_logo(path: Path, target_height: float, max_width: float, tint_hex: str | None = None):
    if not path.exists():
        return Spacer(max_width, target_height)

    image_source = _prepare_logo_source(path, tint_hex=tint_hex)
    original_width, original_height = ImageReader(image_source).getSize()
    scale = target_height / original_height
    scaled_width = original_width * scale
    scaled_height = target_height

    if scaled_width > max_width:
        resize_ratio = max_width / scaled_width
        scaled_width *= resize_ratio
        scaled_height *= resize_ratio

    return Image(image_source, width=scaled_width, height=scaled_height)


def _prepare_logo_source(path: Path, tint_hex: str | None = None):
    if tint_hex is None:
        return str(path)

    with PILImage.open(path).convert("RGBA") as logo:
        alpha = logo.getchannel("A")
        rgb = colors.HexColor(tint_hex).rgb()
        tinted_logo = PILImage.new(
            "RGBA",
            logo.size,
            (
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255),
                0,
            ),
        )
        tinted_logo.putalpha(alpha)

        buffer = BytesIO()
        tinted_logo.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer


def _as_paragraph(value: str, style: ParagraphStyle) -> Paragraph:
    safe_value = escape(value).replace("\n", "<br/>")
    return Paragraph(safe_value, style)
