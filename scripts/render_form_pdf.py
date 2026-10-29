import sys; sys.stdout.reconfigure(encoding='utf-8')
import fitz, glob, os
files = glob.glob(r'C:\Users\ELRA\Desktop\*Bilgi*')
doc = fitz.open(files[0])
page = doc[0]
# Render as image
mat = fitz.Matrix(2.5, 2.5)  # 2.5x zoom
pix = page.get_pixmap(matrix=mat)
out_path = r'C:\Users\ELRA\.gemini\antigravity\brain\8ab6ff7a-937e-46d8-9ad0-0412b8f2e489\ogrenci_bilgi_formu.png'
pix.save(out_path)
print(f'Saved: {out_path} ({os.path.getsize(out_path)} bytes)')
doc.close()
