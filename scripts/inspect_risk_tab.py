import sys
sys.path.insert(0, r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu')
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu\app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# tab_risk student bloğunu bul
in_risk = False
for i, l in enumerate(lines):
    if 'with tab_risk:' in l:
        in_risk = True
    if in_risk:
        print(f"{i+1}: {l.rstrip()}")
    if in_risk and i > 0 and '# ----------------- TAB 5:' in l:
        break
    if in_risk and (i+1) > 1300:  # güvenlik sınırı
        print("... (kesildi)")
        break
