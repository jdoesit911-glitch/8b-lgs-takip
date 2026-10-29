import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from core.database import get_exam_results, get_student_kazanims, get_class_comparison, list_exams
from core.branch_report_gen import generate_all_branch_reports

output_dir = r"C:\Users\ELRA\Desktop\8B sınıfı veriler\brans_raporlari"
print(f"Generating branch reports into: {output_dir}")

exams = list_exams()
nartest_exam = [e for e in exams if "NARTEST" in e['name'].upper()][0]
print(f"Active Exam: {nartest_exam['name']} (ID: {nartest_exam['id']})")

students = get_exam_results(nartest_exam['id'])
print(f"Participating students in NARTEST: {len(students)}")

# Load kazanım data
kazanim_data = {}
for s in students:
    k_list = get_student_kazanims(nartest_exam['id'], s['name'])
    kazanim_data[s['name']] = k_list

# Load comparisons
comparisons = get_class_comparison(nartest_exam['id'])
print(f"Comparisons loaded: {len(comparisons)} subjects")

# Generate 6 branch reports
reports, zip_p = generate_all_branch_reports(
    exam_name=nartest_exam['name'],
    students=students,
    kazanim_data=kazanim_data,
    comparisons=comparisons,
    output_dir=output_dir
)

print(f"\nGenerated {len(reports)} branch reports successfully:")
for r in reports:
    print(f" - {os.path.basename(r)} ({os.path.getsize(r):,} bytes)")
print(f"\nZIP package: {zip_p} ({os.path.getsize(zip_p):,} bytes)")
