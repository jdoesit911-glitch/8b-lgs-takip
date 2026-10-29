import os
import sys

# Ensure root path
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from core.database import get_exam_results, get_student_kazanims, list_exams, get_all_students
from core.comparative_analyzer import get_multi_exam_comparison
from core.student_card_gen import generate_all_student_cards

output_dir = r"C:\Users\ELRA\Desktop\8B sınıfı veriler\karneler"
print(f"Generating student cards into: {output_dir}")

exams = list_exams()
nartest_exam = [e for e in exams if "NARTEST" in e['name'].upper()][0]
print(f"Active Exam: {nartest_exam['name']} (ID: {nartest_exam['id']})")

students = get_exam_results(nartest_exam['id'])
print(f"Participating students in NARTEST: {len(students)}")

# Load kazanım data for participating students
kazanim_data = {}
for s in students:
    k_list = get_student_kazanims(nartest_exam['id'], s['name'])
    kazanim_data[s['name']] = k_list

# Load comparative data
comp_data = get_multi_exam_comparison()
print(f"Comparative data loaded for {len(comp_data)} students.")

# Generate all cards
created_files, zip_path = generate_all_student_cards(
    students=students,
    exam_name=nartest_exam['name'],
    kazanim_data=kazanim_data,
    output_dir=output_dir,
    comp_data=comp_data
)

print(f"\nGenerated {len(created_files)} student cards successfully!")
print(f"ZIP package created: {zip_path} (Size: {os.path.getsize(zip_path):,} bytes)")

# Sample check 3 files
for f in created_files[:3]:
    print(f" - {os.path.basename(f)} ({os.path.getsize(f):,} bytes)")
for f in created_files[-3:]:
    print(f" - {os.path.basename(f)} ({os.path.getsize(f):,} bytes)")
