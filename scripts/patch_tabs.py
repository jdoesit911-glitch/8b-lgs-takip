import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace tabs_list
idx = content.find('tabs_list = [')
end_idx = content.find('= st.tabs(tabs_list)', idx)
end_idx = content.find('\n', end_idx) + 1

old_block = content[idx:end_idx]
print("OLD BLOCK:")
print(repr(old_block))

new_block = ('tabs_list = [\n'
             '    "\U0001f4ca S\u0131n\u0131f Genel G\u00f6r\u00fcn\u00fcm\u00fc",\n'
             '    "\U0001f3af Kazan\u0131m & Pareto Analizi",\n'
             '    "\U0001f464 Bireysel \u00d6\u011frenci Karneleri",\n'
             '    "\U0001f4da Bran\u015f \u00d6\u011fretmen Raporlar\u0131",\n'
             '    "\U0001f4c8 \u00c7oklu Deneme Geli\u015fim Takibi",\n'
             '    "\U0001f5fa\ufe0f Risk Haritas\u0131",\n'
             '    "\u26a1 Otomatik Rapor & Karne \u00dcretici"\n'
             ']\n'
             'tab1, tab2, tab3, tab_branch, tab4, tab_risk, tab5 = st.tabs(tabs_list)\n')

print("\nNEW BLOCK:")
print(repr(new_block))

content2 = content[:idx] + new_block + content[end_idx:]

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content2)

print("\nDONE. Verifying...")
with open('app.py', 'r', encoding='utf-8') as f:
    c2 = f.read()
if 'tab_risk' in c2 and 'Risk Haritas' in c2:
    print("SUCCESS: tab_risk and Risk Haritasi found in app.py")
else:
    print("FAILED")
