import sys; sys.stdout.reconfigure(encoding='utf-8')
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print(f'Total lines: {len(lines)}')
for i, l in enumerate(lines):
    ll = l.lower()
    if any(k in ll for k in ['admin', 'ogretmen', 'öğretmen', 'tab', 'def show']):
        if any(k in ll for k in ['section', 'tab', 'def ', 'admin', 'role']):
            print(f'{i+1}: {l.rstrip()[:120]}')
