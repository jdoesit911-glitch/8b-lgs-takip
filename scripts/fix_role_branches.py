import sys
sys.path.insert(0, r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu')
sys.stdout.reconfigure(encoding='utf-8')

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# tab_risk içinde "else:" bloğu (admin/teacher) — başına None kontrolü ekle
# Şu an: ...else:\n        # ─── Öğretmen / Admin Risk...
old_else = (
    '\n    else:\n'
    '        # ─── Öğretmen / Admin Risk Haritas\u0131 Paneli'
)
new_else = (
    '\n    elif current_role in ("admin", "teacher"):\n'
    '        # ─── Öğretmen / Admin Risk Haritas\u0131 Paneli'
)

# Ayrıca None (giriş yapılmamış) için mesaj
old_start = '    if current_role == "student":\n        # ─── Öğrenci Tanıma Formu'
new_start = (
    '    if current_role is None:\n'
    '        st.warning("🔐 Bu bölümü görmek için giriş yapmanız gerekiyor. Sol panelden PIN kodunuzla giriş yapın.")\n'
    '    elif current_role == "student":\n'
    '        # ─── Öğrenci Tanıma Formu'
)

if old_else in content:
    content = content.replace(old_else, new_else, 1)
    print("else → elif admin/teacher: OK")
else:
    print("else bulunamadı, aramaya devam...")
    idx = content.find('# ─── Öğretmen / Admin Risk')
    if idx > 0:
        print(repr(content[idx-60:idx+60]))

if old_start in content:
    content = content.replace(old_start, new_start, 1)
    print("None role check eklendi: OK")
else:
    print("student start bulunamadı")

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
