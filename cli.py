import sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import argparse
import os
import sys

from core.parser import parse_lgs_workbook
from core.database import save_exam, init_db, list_exams, get_exam_results
from core.word_generator import generate_word_report
from core.excel_generator import generate_excel_tracker
from core.student_card_gen import generate_all_student_cards
from config import EXPORTS_DIR

def run_pipeline(file_path, target_class="8/B", export_dir=EXPORTS_DIR):
    print(f"[*] Dosya okunuyor: {file_path}")
    data = parse_lgs_workbook(file_path, target_class)
    
    exam_name = data['exam_name']
    students = data['students']
    kazanim_data = data['kazanim_data']
    comp_data = data['comparison_data']
    
    print(f"[+] Sınav: {exam_name}")
    print(f"[+] {target_class} sınıfından {len(students)} öğrenci başarıyla ayrıştırıldı.")
    
    # Save to SQLite database
    exam_id = save_exam(exam_name, data['exam_date'], data['publisher'], students, kazanim_data, comp_data)
    print(f"[+] Sınav sonuçları yerel veritabanına kaydedildi (Exam ID: {exam_id}).")
    
    # Generate Word Report
    word_path = os.path.join(export_dir, f"{target_class.replace('/', '')}_LGS_Akademik_Basari_ve_Strateji_Raporu.docx")
    try:
        generate_word_report(exam_name, students, kazanim_data, comp_data, word_path)
        print(f"[+] Kapsamlı Word Raporu oluşturuldu: {word_path}")
    except Exception as e:
        alt_word = os.path.join(export_dir, f"{target_class.replace('/', '')}_LGS_Akademik_Rapor_Yeni.docx")
        generate_word_report(exam_name, students, kazanim_data, comp_data, alt_word)
        print(f"[+] Kapsamlı Word Raporu alternatif dosyaya kaydedildi: {alt_word}")

    # Generate Excel Tracker
    excel_path = os.path.join(export_dir, f"{target_class.replace('/', '')}_LGS_Takip_Sistemi.xlsx")
    try:
        generate_excel_tracker(exam_name, students, kazanim_data, comp_data, excel_path)
        print(f"[+] Master Excel Takip Dosyası oluşturuldu: {excel_path}")
    except PermissionError:
        alt_excel = os.path.join(export_dir, f"{target_class.replace('/', '')}_LGS_Takip_Sistemi_Guncel.xlsx")
        generate_excel_tracker(exam_name, students, kazanim_data, comp_data, alt_excel)
        print(f"[+] Dosya kilitliydi, güncel dosya oluşturuldu: {alt_excel}")

    # Generate Individual Student Report Cards
    cards_dir = os.path.join(export_dir, "karneler")
    created_cards = generate_all_student_cards(students, exam_name, kazanim_data, cards_dir)
    print(f"[+] {len(created_cards)} öğrenci için bireysel karne oluşturuldu -> {cards_dir}")
    print("[✓] Tüm işlemler başarıyla tamamlandı!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LGS Akademik Başarı ve Takip Otomasyonu")
    parser.add_argument("--file", "-f", help="İşlenecek Deneme Sınavı Excel Dosyası Yolu")
    parser.add_argument("--class-name", "-c", default="8/B", help="Hedef Sınıf (Varsayılan: 8/B)")
    parser.add_argument("--export-dir", "-o", default=EXPORTS_DIR, help="Çıktı Klasörü")
    parser.add_argument("--list-exams", action="store_true", help="Kayıtlı sınavları listele")
    
    args = parser.parse_args()
    
    if args.list_exams:
        exams = list_exams()
        print("=== Kayıtlı Sınavlar ===")
        for e in exams:
            print(f"ID: {e['id']} | Ad: {e['name']} | Tarih: {e['exam_date']} | Yayın: {e['publisher']}")
    elif args.file:
        run_pipeline(args.file, args.class_name, args.export_dir)
    else:
        # Default run with PARAF 1
        default_file = r"C:\Users\ELRA\Downloads\PARAF LGS 1 Sonuç ve Analiz Raporları.xlsx"
        if os.path.exists(default_file):
            run_pipeline(default_file, "8/B", EXPORTS_DIR)
        else:
            parser.print_help()
