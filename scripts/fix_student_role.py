import sys
sys.path.insert(0, r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu')
sys.stdout.reconfigure(encoding='utf-8')

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ── DÜZELTME 1: current_role == "student" kontrolü ekle ─────────────────────
# Mevcut: if current_role not in ("admin", "teacher"):
# Yeni:   if current_role == "student":
old_cond = '    if current_role not in ("admin", "teacher"):\n        # ─── Öğrenci Anket Bolumu'
new_cond = '    if current_role == "student":\n        # ─── Öğrenci Tanıma Formu'

if old_cond in content:
    content = content.replace(old_cond, new_cond, 1)
    print("DÜZELTME 1: current_role == student OK")
else:
    print("DÜZELTME 1 bulunamadı, alternatif aranıyor...")
    idx = content.find('if current_role not in ("admin", "teacher"):')
    if idx > 0:
        line_no = content[:idx].count('\n') + 1
        print(f"  Satır {line_no}: {content[idx:idx+60]}")

# ── DÜZELTME 2: stu_id_form boşsa daha iyi mesaj ──────────────────────────
old_warn = '        stu_id_form = st.session_state.get("student_id")\n        if not stu_id_form:\n            st.warning("⚠️ Oturum bilgisi eksik. Lütfen çıkış yapıp tekrar giriş yapın.")'
new_warn = (
    '        stu_id_form = st.session_state.get("student_id")\n'
    '        # Fallback: student_name üzerinden ID bul\n'
    '        if not stu_id_form and st.session_state.get("student_name"):\n'
    '            import sqlite3 as _sq_fb\n'
    '            from config import DATABASE_PATH as _DB_FB\n'
    '            _row_fb = _sq_fb.connect(_DB_FB).execute(\n'
    '                "SELECT id FROM students WHERE name = ?",\n'
    '                (st.session_state.student_name,)\n'
    '            ).fetchone()\n'
    '            if _row_fb:\n'
    '                st.session_state.student_id = _row_fb[0]\n'
    '                stu_id_form = _row_fb[0]\n'
    '        if not stu_id_form:\n'
    '            st.warning("⚠️ Oturum bilgisi eksik. Lütfen çıkış yapıp tekrar giriş yapın.")'
)

if old_warn in content:
    content = content.replace(old_warn, new_warn, 1)
    print("DÜZELTME 2: Fallback student_id OK")
else:
    print("DÜZELTME 2 bulunamadı")
    idx = content.find('stu_id_form = st.session_state.get("student_id")')
    if idx > 0:
        print(repr(content[idx:idx+200]))

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

import ast
with open('app.py', 'r', encoding='utf-8') as f:
    src = f.read()
try:
    ast.parse(src)
    print(f"SYNTAX OK — {len(src.splitlines())} satır")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
