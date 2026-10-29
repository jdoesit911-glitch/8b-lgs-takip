import sys, ast
sys.path.insert(0, r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu')
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu\app.py','r',encoding='utf-8') as f:
    src = f.read()
ast.parse(src)
print('SYNTAX OK -', len(src.splitlines()), 'satir')
checks = ['tab_risk', 'tab_profiles', 'student_profile', 'save_profile',
          'profile_to_risk_factors', 'get_all_profiles',
          'tab_grid, tab_summary, tab_export, tab_profiles']
for c in checks:
    status = 'OK' if c in src else 'MISSING!'
    print(f'  {c}: {status}')
