import sys; sys.stdout.reconfigure(encoding='utf-8')
with open('app.py','r',encoding='utf-8') as f:
    lines = f.readlines()
for i,l in enumerate(lines):
    if 'elif current_role in' in l and 'admin' in l:
        print(f'{i+1}: {l.rstrip()}')
        for j in range(i+1, min(i+4, len(lines))):
            print(f'{j+1}: {lines[j].rstrip()}')
        break
