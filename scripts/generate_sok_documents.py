import os
import sys
import unicodedata

base_dir = r"C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu"
sys.path.insert(0, base_dir)

from core.sok_generator import fill_sok_madde_11_docx, fill_sok_gundem_ve_gozlem_docx, get_8b_students_sok_data
from config import EXPORTS_DIR

desktop_dir = r"C:\Users\ELRA\Desktop\8B sınıfı veriler"

# Find original template files on desktop
f_m11 = [f for f in os.listdir(desktop_dir) if "Madde 11" in f][0]
f_gundem = [f for f in os.listdir(desktop_dir) if "Gu\u0308ndem" in f or "Gundem" in unicodedata.normalize("NFKD", f)][0]

m11_in = os.path.join(desktop_dir, f_m11)
gundem_in = os.path.join(desktop_dir, f_gundem)

# Outputs on desktop and exports
m11_out_desktop = os.path.join(desktop_dir, "ŞÖK Madde 11.docx")
m11_out_named = os.path.join(desktop_dir, "8B_1_Donem_SOK_Madde_11_Bireysel_Degerlendirme.docx")
m11_out_exports = os.path.join(EXPORTS_DIR, "8B_1_Donem_SOK_Madde_11_Bireysel_Degerlendirme.docx")

gundem_out_desktop = os.path.join(desktop_dir, "2026_Ekim_ŞÖK_Gündem_Maddeleri_ve_Sınıf_Gözlem_Formu.docx")
gundem_out_named = os.path.join(desktop_dir, "8B_2026_Ekim_SOK_Toplanti_Tutanagi_ve_Sinif_Gozlem_Formu.docx")
gundem_out_exports = os.path.join(EXPORTS_DIR, "8B_2026_Ekim_SOK_Toplanti_Tutanagi_ve_Sinif_Gozlem_Formu.docx")

print("1. Filling SOK Madde 11 (Bireysel Ogrenci Degerlendirme Tablosu)...")
fill_sok_madde_11_docx(m11_in, m11_out_desktop)
fill_sok_madde_11_docx(m11_in, m11_out_named)
fill_sok_madde_11_docx(m11_in, m11_out_exports)
print("   -> SOK Madde 11 successfully filled and saved!")

print("\n2. Filling SOK Gundem Maddeleri ve Sinif Gozlem Formu...")
fill_sok_gundem_ve_gozlem_docx(gundem_in, gundem_out_desktop)
fill_sok_gundem_ve_gozlem_docx(gundem_in, gundem_out_named)
fill_sok_gundem_ve_gozlem_docx(gundem_in, gundem_out_exports)
print("   -> SOK Gundem ve Gozlem Formu successfully filled and saved!")

print("\nALL SOK DOCUMENTS GENERATED SUCCESSFULLY!")
