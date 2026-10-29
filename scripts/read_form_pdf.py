import sys; sys.stdout.reconfigure(encoding='utf-8')
import fitz, glob
files = glob.glob(r'C:\Users\ELRA\Desktop\*Bilgi*')
doc = fitz.open(files[0])
print(f'Sayfa sayisi: {doc.page_count}')
for i, page in enumerate(doc):
    print(f'\n=== SAYFA {i+1} ===')
    print(page.get_text())
doc.close()
