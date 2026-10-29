"""
Risk Haritası PDF Dışa Aktarıcı
Özel Eğitim ve Rehberlik Hizmetleri Genel Müdürlüğü S.İ.4.a formatı
"""
import sys
import os

try:
    from docx import Document
    from docx.shared import Pt, Cm, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_ALIGN_VERTICAL
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    DOCX_OK = True
except ImportError:
    DOCX_OK = False

from core.risk_mapper import RISK_FACTORS, get_all_risk_data


def set_cell_bg(cell, hex_color: str):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def export_risk_pdf(students: list, risk_data: dict, output_path: str,
                    school_name: str = "……", class_name: str = "8/B"):
    """
    students: list of dicts {id, name, school_no}
    risk_data: {student_id: set(factor_ids)}
    output_path: .docx dosya yolu
    """
    if not DOCX_OK:
        raise ImportError("python-docx kurulu değil.")

    doc = Document()

    # Sayfa ayarı — Yatay A4
    section = doc.sections[0]
    section.page_height = Cm(21.0)
    section.page_width = Cm(29.7)
    section.left_margin = Cm(0.8)
    section.right_margin = Cm(0.8)
    section.top_margin = Cm(1.2)
    section.bottom_margin = Cm(1.0)

    # Başlık
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(f"{school_name} OKULU {class_name} SINIFI RİSK HARİTASI")
    run.bold = True
    run.font.size = Pt(9)

    sub_title = doc.add_paragraph()
    sub_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run2 = sub_title.add_run("Özel Eğitim ve Rehberlik Hizmetleri Genel Müdürlüğü   S.İ.4.a")
    run2.font.size = Pt(7)
    run2.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    # Tablo — sütunlar: Sıra | Ad Soyad | 35 faktör
    factor_labels = [f["label"] for f in RISK_FACTORS]
    col_count = 3 + len(RISK_FACTORS)  # Sıra + Okul No + Ad Soyad + 35 faktör

    table = doc.add_table(rows=1 + len(students) + 1, cols=col_count)
    table.style = 'Table Grid'

    # Başlık satırı
    hdr = table.rows[0]

    def hdr_cell(idx, text, size=6, bold=True, rotate=False, bg="1F5C99"):
        cell = hdr.cells[idx]
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_bg(cell, bg)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = bold
        run.font.size = Pt(size)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        if rotate:
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            textDir = OxmlElement('w:textDirection')
            textDir.set(qn('w:val'), 'btLr')
            tcPr.append(textDir)

    hdr_cell(0, "Sıra", size=6)
    hdr_cell(1, "No", size=6)
    hdr_cell(2, "Öğrencinin Adı Soyadı", size=6)

    cat_colors = {
        "Aile Yapısı":    "2E75B6",
        "Özel Durum":     "833C00",
        "Aile Sağlığı":   "7B2C2C",
        "Öğrenci Durumu": "375623",
    }

    for i, f in enumerate(RISK_FACTORS):
        bg = cat_colors.get(f["category"], "1F5C99")
        hdr_cell(3 + i, f["label"], size=5, rotate=True, bg=bg)

    # Sütun genişlikleri
    COL_WIDTHS_CM = [0.6, 0.7, 3.2] + [0.4] * len(RISK_FACTORS)
    for row in table.rows:
        for j, cell in enumerate(row.cells):
            cell.width = Cm(COL_WIDTHS_CM[j])

    # Öğrenci satırları
    for i, stu in enumerate(students):
        row = table.rows[i + 1]
        sid = stu["id"]
        active = risk_data.get(sid, set())

        def data_cell(col_idx, text, size=6, align=WD_ALIGN_PARAGRAPH.LEFT, bold=False, bg=None):
            cell = row.cells[col_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if bg:
                set_cell_bg(cell, bg)
            p = cell.paragraphs[0]
            p.alignment = align
            run = p.add_run(str(text))
            run.font.size = Pt(size)
            if bold:
                run.bold = True

        data_cell(0, i + 1, align=WD_ALIGN_PARAGRAPH.CENTER)
        data_cell(1, stu.get("school_no", ""), align=WD_ALIGN_PARAGRAPH.CENTER)
        data_cell(2, stu.get("name", ""), size=6)

        for j, f in enumerate(RISK_FACTORS):
            cell = row.cells[3 + j]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if f["id"] in active:
                run = p.add_run("✓")
                run.font.size = Pt(7)
                run.bold = True
                run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
                bg = cat_colors.get(f["category"], "D9E1F2")
                # Light version
                light = {"Aile Yapısı": "DEEAF1", "Özel Durum": "FCE4D6",
                         "Aile Sağlığı": "FCE4D6", "Öğrenci Durumu": "E2EFDA"}
                set_cell_bg(cell, light.get(f["category"], "DEEAF1"))
            else:
                p.add_run("")

    # TOPLAM satırı
    total_row = table.rows[-1]
    total_row.cells[0].paragraphs[0].add_run("")
    tc = total_row.cells[0]
    tc2 = total_row.cells[2]
    p = tc2.paragraphs[0]
    run = p.add_run("TOPLAM")
    run.bold = True
    run.font.size = Pt(6)

    for j, f in enumerate(RISK_FACTORS):
        count = sum(1 for stu in students if f["id"] in risk_data.get(stu["id"], set()))
        cell = total_row.cells[3 + j]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(str(count) if count > 0 else "")
        run.font.size = Pt(6)
        run.bold = True
        if count > 0:
            run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)

    doc.save(output_path)
    return output_path
