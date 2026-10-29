import os
import sys
import sqlite3

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Set workspace root in python path
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

from core.parser import parse_lgs_workbook
from core.database import save_exam, list_exams, get_all_students, ensure_all_pins, get_exam_results

excel_path = r"C:\Users\ELRA\Desktop\8B sınıfı veriler\NARTEST LGS 1 Sonuç ve Analiz Raporları.xlsx"

print(f"=== NARTEST Ingestion Script ===")
print(f"Source file: {excel_path}")

parsed = parse_lgs_workbook(excel_path, target_class="8/B")
print(f"Parsed Exam Name: {parsed['exam_name']}")
print(f"Publisher: {parsed['publisher']}")
print(f"Total participating students: {len(parsed['students'])}")
print(f"Total students with kazanim: {len(parsed['kazanim_data'])}")
print(f"Comparisons count: {len(parsed['comparison_data'])}")

# Ingest to DB
exam_id = save_exam(
    exam_name=parsed['exam_name'],
    exam_date="2026-10-26",
    publisher=parsed['publisher'],
    students_data=parsed['students'],
    kazanim_data=parsed['kazanim_data'],
    comparison_data=parsed['comparison_data']
)

print(f"\nExam saved with ID: {exam_id}")

# Ensure all students have PINs
updated_pins = ensure_all_pins()
print(f"Ensured PINs. Newly generated PINs: {updated_pins}")

# Audit Exams
exams = list_exams()
print(f"\nExams in DB ({len(exams)}):")
for e in exams:
    print(f" - ID: {e['id']} | Name: {e['name']} | Date: {e['exam_date']} | Publisher: {e['publisher']}")

# Audit Students
students = get_all_students()
print(f"\nTotal Students in DB ({len(students)}):")
for s in students:
    print(f" - ID: {s['id']:2d} | No: {s['school_no']:>4s} | Name: {s['name']:<25s} | PIN: {s['pin']}")

# Audit Results for NARTEST
results = get_exam_results(exam_id)
print(f"\nNARTEST Exam Results ({len(results)} rows):")
for r in results[:5]:
    print(f" Rank {r['class_rank']:2d} | No: {r['school_no']:>4s} | {r['name']:<25s} | Net: {r['top_net']:5.2f} | Score: {r['puan']:6.2f}")
print(" ...")
for r in results[-3:]:
    print(f" Rank {r['class_rank']:2d} | No: {r['school_no']:>4s} | {r['name']:<25s} | Net: {r['top_net']:5.2f} | Score: {r['puan']:6.2f}")

print("\nIngestion completed successfully!")
