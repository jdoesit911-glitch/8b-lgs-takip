"""
Risk Haritası — Tek Sayfa Yatay A4 Word Exporteri
Özel Eğitim ve Rehberlik Hizmetleri Genel Müdürlüğü S.İ.4.a formatı
Tüm öğrenciler + 35 faktör → 1 sayfa Yatay A4
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from lxml import etree

from core.risk_mapper import RISK_FACTORS


# ─── Renk Paleti ───────────────────────────────────────────────────────────────
CAT_COLORS = {
    "Aile Yapısı":    {"header": "1F5C99", "active": "BDD7EE", "label_fg": "FFFFFF"},
    "Özel Durum":     {"header": "833C00", "active": "F4CCCC", "label_fg": "FFFFFF"},
    "Aile Sağlığı":   {"header": "9C2323", "active": "F9D9D9", "label_fg": "FFFFFF"},
    "Öğrenci Durumu": {"header": "375623", "active": "D9EAD3", "label_fg": "FFFFFF"},
}
ROW_EVEN_BG  = "F5F5F5"
ROW_ODD_BG   = "FFFFFF"
TOTAL_BG     = "E8E8E8"
TICK_COLOR   = RGBColor(0xC0, 0x00, 0x00)

# ─── Boyutlar (Twips) — A4 Yatay, kenar boşlukları 7mm ─────────────────────
# Kullanılabilir genişlik: 297mm - 14mm = 283mm = 16,029 twips (1mm≈56.69tw)
COL_W_NO   = int(6   * 56.7)   # 6mm  — Sıra
COL_W_OKNO = int(8   * 56.7)   # 8mm  — Okul No
COL_W_NAME = int(38  * 56.7)   # 38mm — Ad Soyad
COL_W_FACT = int(6.8 * 56.7)   # 6.8mm × 35 = 238mm

ROW_H_HDR  = int(32  * 56.7)   # 32mm — döndürülmüş başlık
ROW_H_DATA = int(5.1 * 56.7)   # 5.1mm × 31 satır (29+Toplam+Sıra hdr)
ROW_H_TOTAL= int(6   * 56.7)


def _set_bg(cell, hex_color: str):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    # remove existing shd
    for old in tcPr.findall(qn("w:shd")):
        tcPr.remove(old)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_color.upper())
    tcPr.append(shd)


def _set_row_height(row, twips: int, exact: bool = True):
    tr = row._tr
    trPr = tr.get_or_add_trPr()
    for old in trPr.findall(qn("w:trHeight")):
        trPr.remove(old)
    trH = OxmlElement("w:trHeight")
    trH.set(qn("w:val"),   str(twips))
    trH.set(qn("w:hRule"), "exact" if exact else "atLeast")
    trPr.append(trH)


def _set_col_width(cell, twips: int):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    for old in tcPr.findall(qn("w:tcW")):
        tcPr.remove(old)
    tcW = OxmlElement("w:tcW")
    tcW.set(qn("w:w"),    str(twips))
    tcW.set(qn("w:type"), "dxa")
    tcPr.append(tcW)


def _rotate_text(cell):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    textDir = OxmlElement("w:textDirection")
    textDir.set(qn("w:val"), "btLr")
    tcPr.append(textDir)


def _set_cell_borders(cell, border_size=2):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"),  "single")
        el.set(qn("w:sz"),   str(border_size))
        el.set(qn("w:space"),"0")
        el.set(qn("w:color"),"AAAAAA")
        tcBorders.append(el)
    tcPr.append(tcBorders)


def _no_space_para(cell):
    for para in cell.paragraphs:
        pPr = para._p.get_or_add_pPr()
        # remove spacing
        for old in pPr.findall(qn("w:spacing")):
            pPr.remove(old)
        spacing = OxmlElement("w:spacing")
        spacing.set(qn("w:before"), "0")
        spacing.set(qn("w:after"),  "0")
        spacing.set(qn("w:line"),   "240")
        spacing.set(qn("w:lineRule"),"auto")
        pPr.append(spacing)


def _keep_table_together(table):
    """Tablonun sayfa kırılmamasını zorla."""
    for row in table.rows:
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        cantSplit = OxmlElement("w:cantSplit")
        cantSplit.set(qn("w:val"), "1")
        trPr.append(cantSplit)


def export_risk_pdf(students: list, risk_data: dict, output_path: str,
                    school_name: str = "……", class_name: str = "8/B"):
    """
    students : [{id, school_no, name}]
    risk_data: {student_id: set(factor_ids)}
    """
    doc = Document()

    # ── Sayfa ayarı — Yatay A4, 7mm kenar ────────────────────────────────────
    sec = doc.sections[0]
    sec.page_width        = Cm(29.7)
    sec.page_height       = Cm(21.0)
    sec.left_margin       = Cm(0.7)
    sec.right_margin      = Cm(0.7)
    sec.top_margin        = Cm(0.7)
    sec.bottom_margin     = Cm(0.7)
    sec.header_distance   = Cm(0.3)
    sec.footer_distance   = Cm(0.3)

    # ── Başlık ────────────────────────────────────────────────────────────────
    title_para = doc.add_paragraph()
    title_para.paragraph_format.space_before = Pt(0)
    title_para.paragraph_format.space_after  = Pt(2)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = title_para.add_run(
        f"{school_name}  {class_name} SINIFI RİSK HARİTASI     "
        f"Özel Eğitim ve Rehberlik Hizmetleri Genel Müdürlüğü — S.İ.4.a"
    )
    run_t.bold = True
    run_t.font.size = Pt(7)
    run_t.font.color.rgb = RGBColor(0x1F, 0x38, 0x96)

    # ── Tablo ─────────────────────────────────────────────────────────────────
    # Satırlar: 1 başlık + N öğrenci + 1 toplam
    n_rows = 1 + len(students) + 1
    n_cols = 3 + len(RISK_FACTORS)
    table = doc.add_table(rows=n_rows, cols=n_cols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # ── Sütun genişlikleri (tüm hücrelere uygula) ────────────────────────────
    widths = [COL_W_NO, COL_W_OKNO, COL_W_NAME] + [COL_W_FACT] * len(RISK_FACTORS)
    for row in table.rows:
        for j, cell in enumerate(row.cells):
            _set_col_width(cell, widths[j])

    # ── Row heights ───────────────────────────────────────────────────────────
    _set_row_height(table.rows[0], ROW_H_HDR)
    for i in range(1, len(students) + 1):
        _set_row_height(table.rows[i], ROW_H_DATA)
    _set_row_height(table.rows[-1], ROW_H_TOTAL)

    _keep_table_together(table)

    # ── BAŞLIK SATIRI ─────────────────────────────────────────────────────────
    hdr_row = table.rows[0]
    hdr_row.cells[0].vertical_alignment = WD_ALIGN_VERTICAL.BOTTOM
    hdr_row.cells[1].vertical_alignment = WD_ALIGN_VERTICAL.BOTTOM
    hdr_row.cells[2].vertical_alignment = WD_ALIGN_VERTICAL.BOTTOM

    def _hdr_fixed(col_idx, text, bg="2E4057"):
        cell = hdr_row.cells[col_idx]
        _set_bg(cell, bg)
        _no_space_para(cell)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(5.5)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    _hdr_fixed(0, "Sıra")
    _hdr_fixed(1, "No")
    _hdr_fixed(2, "Öğrencinin Adı Soyadı")

    for i, f in enumerate(RISK_FACTORS):
        cell = hdr_row.cells[3 + i]
        cat  = f["category"]
        cols = CAT_COLORS.get(cat, {"header": "333333", "label_fg": "FFFFFF"})
        _set_bg(cell, cols["header"])
        _rotate_text(cell)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.BOTTOM
        _no_space_para(cell)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(f["label"])
        run.font.size = Pt(5)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        _set_cell_borders(cell)

    # ── VERİ SATIRLARI ────────────────────────────────────────────────────────
    for row_i, stu in enumerate(students):
        row   = table.rows[row_i + 1]
        sid   = stu["id"]
        active = risk_data.get(sid, set())
        bg_row = ROW_EVEN_BG if row_i % 2 == 0 else ROW_ODD_BG

        def _data_cell(col_idx, text, bold=False, center=True, bg=None):
            cell = row.cells[col_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            _set_bg(cell, bg or bg_row)
            _no_space_para(cell)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(str(text))
            run.font.size = Pt(5.5)
            if bold:
                run.bold = True

        _data_cell(0, row_i + 1)
        _data_cell(1, stu.get("school_no", ""))
        _data_cell(2, stu.get("name", ""), center=False)

        for j, f in enumerate(RISK_FACTORS):
            cell = row.cells[3 + j]
            cat  = f["category"]
            cols = CAT_COLORS.get(cat, {"active": "DDDDDD"})
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            _no_space_para(cell)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _set_cell_borders(cell, border_size=2)

            if f["id"] in active:
                _set_bg(cell, cols["active"])
                run = p.add_run("✓")
                run.bold = True
                run.font.size = Pt(7)
                run.font.color.rgb = TICK_COLOR
            else:
                _set_bg(cell, bg_row)

    # ── TOPLAM SATIRI ─────────────────────────────────────────────────────────
    total_row = table.rows[-1]
    _set_bg(total_row.cells[0], TOTAL_BG)
    _set_bg(total_row.cells[1], TOTAL_BG)
    total_row.cells[2].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    _set_bg(total_row.cells[2], TOTAL_BG)
    _no_space_para(total_row.cells[2])
    p_tot = total_row.cells[2].paragraphs[0]
    p_tot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tot = p_tot.add_run("TOPLAM")
    run_tot.bold = True
    run_tot.font.size = Pt(6)

    for j, f in enumerate(RISK_FACTORS):
        cnt  = sum(1 for stu in students if f["id"] in risk_data.get(stu["id"], set()))
        cell = total_row.cells[3 + j]
        cat  = f["category"]
        cols = CAT_COLORS.get(cat, {"header": "888888"})
        _set_bg(cell, TOTAL_BG)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        _no_space_para(cell)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _set_cell_borders(cell, border_size=2)
        if cnt > 0:
            run = p.add_run(str(cnt))
            run.bold = True
            run.font.size = Pt(6)
            run.font.color.rgb = TICK_COLOR

    # ── Altbilgi ──────────────────────────────────────────────────────────────
    foot_diger = doc.add_paragraph()
    foot_diger.paragraph_format.space_before = Pt(3)
    foot_diger.paragraph_format.space_after  = Pt(0)
    foot_diger.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_fd = foot_diger.add_run("📌 * NOT (35. Faktör — 'Diğer'): İlk 34 standart MEB risk kategorisinde tanımlanmamış; ancak rehberlik takibini gerektiren durumları (ağır sınav kaygısı, son 1-2 yılda yaşanan travmatik/önemli olaylar, duygusal tükenmişlik veya öğrencinin bildirdiği özel güçlükler) ifade eder.")
    r_fd.font.size = Pt(5)
    r_fd.italic = True

    foot = doc.add_paragraph()
    foot.paragraph_format.space_before = Pt(2)
    foot.paragraph_format.space_after  = Pt(0)
    foot.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    foot.add_run("🔒 Kişisel veri — Gizli   |   "
                 "🟦 Aile Yapısı   🟫 Özel Durum   🟥 Aile Sağlığı   🟩 Öğrenci Durumu"
                 ).font.size = Pt(5.5)

    doc.save(output_path)
    return output_path


# ─── HTML Önizleme (Streamlit'te yazdır butonu için) ─────────────────────────
def build_risk_html(students: list, risk_data: dict,
                    school_name: str = "……", class_name: str = "8/B") -> str:
    """
    Tarayıcıda Ctrl+P ile tek sayfaya sığacak HTML tablosu üretir.
    """
    CAT_HDR  = {
        "Aile Yapısı":    "#1F5C99",
        "Özel Durum":     "#833C00",
        "Aile Sağlığı":   "#9C2323",
        "Öğrenci Durumu": "#375623",
    }
    CAT_CELL = {
        "Aile Yapısı":    "#BDD7EE",
        "Özel Durum":     "#F4CCCC",
        "Aile Sağlığı":   "#F9D9D9",
        "Öğrenci Durumu": "#D9EAD3",
    }

    html = [f"""<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8">
<title>{class_name} Risk Haritası</title>
<style>
@page {{ size: A4 landscape; margin: 7mm; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: Arial, sans-serif; font-size: 5.5pt; }}
h2 {{ font-size: 7pt; text-align: center; color: #1F3864; margin-bottom: 3px; }}
table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
th, td {{ border: 0.3pt solid #AAAAAA; vertical-align: middle; padding: 0 1px; overflow: hidden; white-space: nowrap; }}
.col-no   {{ width: 6mm;  text-align: center; }}
.col-okno {{ width: 8mm;  text-align: center; }}
.col-name {{ width: 38mm; text-align: left; padding-left: 2px; }}
.col-fact {{ width: 6.5mm; text-align: center; }}
.hdr-fixed {{ color: #fff; font-weight: bold; font-size: 5.5pt; text-align: center; background: #2E4057; height: 32mm; }}
.hdr-fact  {{ color: #fff; font-weight: bold; font-size: 4.8pt; writing-mode: vertical-rl; transform: rotate(180deg); height: 32mm; vertical-align: bottom; padding-bottom: 2px; }}
.row-even  {{ background: #F5F5F5; }}
.row-odd   {{ background: #FFFFFF; }}
.tick      {{ color: #C00000; font-weight: bold; font-size: 7pt; }}
.total-row {{ background: #E8E8E8; font-weight: bold; }}
.total-cnt {{ color: #C00000; font-weight: bold; }}
.legend    {{ font-size: 5pt; text-align: right; margin-top: 2px; color: #555; }}
@media print {{ .no-print {{ display: none; }} body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }} }}
</style></head><body>
<h2>{school_name} &nbsp; {class_name} SINIFI RİSK HARİTASI &nbsp;&nbsp;
Özel Eğitim ve Rehberlik Hizmetleri Genel Müdürlüğü — S.İ.4.a</h2>
<table>
<thead><tr>
  <th class="hdr-fixed col-no">Sıra</th>
  <th class="hdr-fixed col-okno">No</th>
  <th class="hdr-fixed col-name">Öğrencinin Adı Soyadı</th>
"""]

    for f in RISK_FACTORS:
        bg = CAT_HDR.get(f["category"], "#333")
        html.append(f'  <th class="hdr-fact col-fact" style="background:{bg}">{f["label"]}</th>\n')

    html.append("</tr></thead>\n<tbody>\n")

    for i, stu in enumerate(students):
        sid    = stu["id"]
        active = risk_data.get(sid, set())
        row_cls = "row-even" if i % 2 == 0 else "row-odd"
        html.append(f'<tr class="{row_cls}">'
                    f'<td class="col-no">{i+1}</td>'
                    f'<td class="col-okno">{stu.get("school_no","")}</td>'
                    f'<td class="col-name">{stu.get("name","")}</td>')
        for f in RISK_FACTORS:
            if f["id"] in active:
                bg = CAT_CELL.get(f["category"], "#EEE")
                html.append(f'<td class="col-fact" style="background:{bg}"><span class="tick">✓</span></td>')
            else:
                html.append('<td class="col-fact"></td>')
        html.append("</tr>\n")

    # Toplam satırı
    html.append('<tr class="total-row">'
                '<td class="col-no"></td>'
                '<td class="col-okno"></td>'
                '<td class="col-name" style="text-align:center">TOPLAM</td>')
    for f in RISK_FACTORS:
        cnt = sum(1 for stu in students if f["id"] in risk_data.get(stu["id"], set()))
        html.append(f'<td class="col-fact"><span class="total-cnt">{cnt if cnt else ""}</span></td>')
    html.append("</tr>\n")

    html.append("""</tbody></table>
<div class="legend">
🔒 Kişisel veri — Gizli &nbsp;|&nbsp;
<span style="color:#1F5C99">■</span> Aile Yapısı &nbsp;
<span style="color:#833C00">■</span> Özel Durum &nbsp;
<span style="color:#9C2323">■</span> Aile Sağlığı &nbsp;
<span style="color:#375623">■</span> Öğrenci Durumu
</div>
<div style="font-size: 5pt; text-align: left; margin-top: 3px; color: #1F497D; line-height: 1.3;">
  <b>📌 35. Faktör ("Diğer") Açıklaması:</b> İlk 34 standart MEB risk kategorisinde tanımlanmamış; ancak öğrencinin rehberlik takibini gerektiren istisnai durumları ifade eder (Ağır sınav kaygısı, son 1-2 yılda yaşanan travmatik/önemli olaylar, duygusal tükenmişlik veya öğrencinin bildirdiği özel güçlükler).
</div>
</body></html>""")

    return "".join(html)



def export_risk_excel(students: list, risk_data: dict, output_path: str,
                      school_name: str = "Şehit Öğretmen Neşe Alten Ortaokulu",
                      class_name: str = "8/B"):
    """
    Sınıf Risk Haritasını MEB S.İ.4.a standart şablonunda Excel (.xlsx) formatında oluşturur.
    Ekran görüntüsündeki formatın birebir aynısıdır:
    - 35 faktör dikey (90 derece) döndürülmüş turuncu başlıklar
    - Aktif faktörler için 'X' işaretleri
    - Öğrenci bazında ve faktör bazında Genel Toplam satır/sütunları
    """
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sınıf Risk Haritası"
    ws.views.sheetView[0].showGridLines = True

    font_title = Font(name="Calibri", size=13, bold=True, color="1F497D")
    font_sub = Font(name="Calibri", size=9, italic=True, color="595959")
    font_hdr_num = Font(name="Calibri", size=10, bold=True, color="000000")
    font_hdr_text = Font(name="Calibri", size=9, bold=True, color="000000")
    font_data = Font(name="Calibri", size=10)
    font_x = Font(name="Calibri", size=11, bold=True, color="C00000")
    font_total = Font(name="Calibri", size=10, bold=True, color="000000")

    fill_orange_hdr = PatternFill(start_color="F8CBAD", end_color="F8CBAD", fill_type="solid")
    fill_num_hdr = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    fill_active_x = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    fill_total = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    fill_zebra = PatternFill(start_color="F9FBFD", end_color="F9FBFD", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='B0B0B0'),
        right=Side(style='thin', color='B0B0B0'),
        top=Side(style='thin', color='B0B0B0'),
        bottom=Side(style='thin', color='B0B0B0')
    )
    thick_bottom = Border(
        left=Side(style='thin', color='B0B0B0'),
        right=Side(style='thin', color='B0B0B0'),
        top=Side(style='thin', color='B0B0B0'),
        bottom=Side(style='medium', color='1F497D')
    )

    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_vertical = Alignment(horizontal="center", vertical="center", textRotation=90, wrap_text=True)

    # Row 1: Title
    ws.merge_cells("A1:AL1")
    title_cell = ws["A1"]
    title_cell.value = f"T.C. MİLLÎ EĞİTİM BAKANLIĞI — {school_name.upper()} {class_name} ŞUBESİ SINIF RİSK HARİTASI (S.İ.4.a)"
    title_cell.font = font_title
    title_cell.alignment = align_center
    ws.row_dimensions[1].height = 25

    # Row 2: Subtitle
    ws.merge_cells("A2:AL2")
    sub_cell = ws["A2"]
    sub_cell.value = "Özel Eğitim ve Rehberlik Hizmetleri Genel Müdürlüğü Standart Risk Faktörleri Tablosu"
    sub_cell.font = font_sub
    sub_cell.alignment = align_center
    ws.row_dimensions[2].height = 17

    # Row 3: Header Numbers
    headers_info = ["Sıra", "No", "Adı Soyadı"]
    for c_idx, h_text in enumerate(headers_info, 1):
        cell = ws.cell(row=3, column=c_idx, value=h_text)
        cell.font = font_hdr_num
        cell.fill = fill_num_hdr
        cell.alignment = align_center
        cell.border = thin_border

    for i, f in enumerate(RISK_FACTORS, 4):
        cell = ws.cell(row=3, column=i, value=f["id"])
        cell.font = font_hdr_num
        cell.fill = fill_num_hdr
        cell.alignment = align_center
        cell.border = thin_border

    tot_col_idx = len(RISK_FACTORS) + 4
    cell_tot_hdr = ws.cell(row=3, column=tot_col_idx, value="Toplam")
    cell_tot_hdr.font = font_hdr_num
    cell_tot_hdr.fill = fill_total
    cell_tot_hdr.alignment = align_center
    cell_tot_hdr.border = thin_border
    ws.row_dimensions[3].height = 20

    # Row 4: Header Vertical Labels
    for c_idx, h_text in enumerate(headers_info, 1):
        cell = ws.cell(row=4, column=c_idx, value=h_text)
        cell.font = font_hdr_num
        cell.fill = fill_orange_hdr
        cell.alignment = align_center
        cell.border = thick_bottom

    for i, f in enumerate(RISK_FACTORS, 4):
        cell = ws.cell(row=4, column=i, value=f["label"])
        cell.font = font_hdr_text
        cell.fill = fill_orange_hdr
        cell.alignment = align_vertical
        cell.border = thick_bottom

    cell_tot_lbl = ws.cell(row=4, column=tot_col_idx, value="Risk Sayısı")
    cell_tot_lbl.font = font_hdr_text
    cell_tot_lbl.fill = fill_total
    cell_tot_lbl.alignment = align_vertical
    cell_tot_lbl.border = thick_bottom
    ws.row_dimensions[4].height = 135

    # Column Widths
    ws.column_dimensions['A'].width = 5.5
    ws.column_dimensions['B'].width = 8.5
    ws.column_dimensions['C'].width = 24.0
    for i in range(4, tot_col_idx):
        col_letter = get_column_letter(i)
        ws.column_dimensions[col_letter].width = 4.3
    ws.column_dimensions[get_column_letter(tot_col_idx)].width = 8.0

    # Data Rows
    start_row = 5
    col_counts = {f["id"]: 0 for f in RISK_FACTORS}

    for s_idx, stu in enumerate(students, 1):
        r_idx = start_row + s_idx - 1
        stu_id = stu["id"]
        active_f = risk_data.get(stu_id, set())

        is_even = (s_idx % 2 == 0)
        row_fill = fill_zebra if is_even else None

        c_no = ws.cell(row=r_idx, column=1, value=s_idx)
        c_no.font = font_data
        c_no.alignment = align_center
        c_no.border = thin_border
        if row_fill: c_no.fill = row_fill

        c_okno = ws.cell(row=r_idx, column=2, value=str(stu.get("school_no", "")))
        c_okno.font = font_data
        c_okno.alignment = align_center
        c_okno.border = thin_border
        if row_fill: c_okno.fill = row_fill

        c_name = ws.cell(row=r_idx, column=3, value=stu.get("name", ""))
        c_name.font = font_data
        c_name.alignment = align_left
        c_name.border = thin_border
        if row_fill: c_name.fill = row_fill

        stu_risk_count = 0
        for f_idx, f in enumerate(RISK_FACTORS, 4):
            fid = f["id"]
            cell_f = ws.cell(row=r_idx, column=f_idx)
            cell_f.border = thin_border

            if fid in active_f:
                cell_f.value = "X"
                cell_f.font = font_x
                cell_f.fill = fill_active_x
                cell_f.alignment = align_center
                stu_risk_count += 1
                col_counts[fid] += 1
            else:
                cell_f.value = ""
                cell_f.alignment = align_center
                if row_fill: cell_f.fill = row_fill

        c_tot = ws.cell(row=r_idx, column=tot_col_idx, value=stu_risk_count)
        c_tot.font = font_total if stu_risk_count > 0 else font_data
        c_tot.alignment = align_center
        c_tot.border = thin_border
        c_tot.fill = fill_total if stu_risk_count > 0 else (row_fill or PatternFill(fill_type=None))
        ws.row_dimensions[r_idx].height = 19

    # Total Row
    total_r_idx = start_row + len(students)
    ws.merge_cells(start_row=total_r_idx, start_column=1, end_row=total_r_idx, end_column=3)
    c_tot_lbl = ws.cell(row=total_r_idx, column=1, value="GENEL TOPLAM")
    c_tot_lbl.font = font_total
    c_tot_lbl.fill = fill_total
    c_tot_lbl.alignment = align_center
    c_tot_lbl.border = thin_border
    ws.cell(row=total_r_idx, column=2).border = thin_border
    ws.cell(row=total_r_idx, column=3).border = thin_border

    grand_total = 0
    for f_idx, f in enumerate(RISK_FACTORS, 4):
        fid = f["id"]
        cnt = col_counts[fid]
        grand_total += cnt
        cell_c_tot = ws.cell(row=total_r_idx, column=f_idx, value=cnt)
        cell_c_tot.font = font_total
        cell_c_tot.fill = fill_total
        cell_c_tot.alignment = align_center
        cell_c_tot.border = thin_border

    c_grand = ws.cell(row=total_r_idx, column=tot_col_idx, value=grand_total)
    c_grand.font = font_total
    c_grand.fill = fill_total
    c_grand.alignment = align_center
    c_grand.border = thin_border
    ws.row_dimensions[total_r_idx].height = 22

    # Note / Legend Row for F35 (Diğer)
    note_r1 = total_r_idx + 2
    ws.merge_cells(start_row=note_r1, start_column=1, end_row=note_r1, end_column=tot_col_idx)
    c_note1 = ws.cell(row=note_r1, column=1)
    c_note1.value = "📌 35. FAKTÖR ('DİĞER') AÇIKLAMASI: İlk 34 standart MEB risk kategorisinde yer almayan; ancak öğrencinin akademik ve psikososyal takibini gerektiren özel durumları ifade eder (Ağır sınav kaygısı, son 1-2 yılda yaşanan travmatik/önemli olaylar, duygusal tükenmişlik veya öğrencinin bildirdiği özel güçlükler)."
    c_note1.font = Font(name="Calibri", size=9, italic=True, bold=True, color="1F497D")
    c_note1.alignment = align_left
    ws.row_dimensions[note_r1].height = 22

    note_r2 = total_r_idx + 3
    ws.merge_cells(start_row=note_r2, start_column=1, end_row=note_r2, end_column=tot_col_idx)
    c_note2 = ws.cell(row=note_r2, column=1)
    c_note2.value = "* 8/B Sınıfı 'Diğer' Kapsamındaki Durumlar: Melek Rana Kesici ('yaşamak' - psikososyal takip), Halit Eren Hatunoğlu ('kaygı'), Derin Yılmaz (önemli ailevi olay), Meryem Bozdemir (önemli ailevi olay), Tuna Koç (akran uyumu), Sümeyye Taşkın & Beren Koç (ulaşım problemi)."
    c_note2.font = Font(name="Calibri", size=8.5, italic=True, color="404040")
    c_note2.alignment = align_left
    ws.row_dimensions[note_r2].height = 20

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    wb.save(output_path)
    return output_path
