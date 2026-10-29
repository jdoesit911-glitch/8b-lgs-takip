import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the broken generator expression
old_line = (
    'total_at_risk = sum(1 for sid, _ in '
    '[(s[0], all_risk.get(s[0], set())) for s in _students_r] '
    'if all_risk.get(s[0]))'
)
new_line = (
    'total_at_risk = sum(1 for s in _students_r if all_risk.get(s[0]))'
)

if old_line in content:
    content2 = content.replace(old_line, new_line, 1)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content2)
    print('FIXED OK')
else:
    # Find surrounding context
    idx = content.find('total_at_risk')
    print('NOT FOUND. Context:')
    print(repr(content[idx:idx+300]))
