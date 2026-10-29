import os
import sys
import sqlite3

# Ensure project root is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config import DATABASE_PATH
from core.database import get_connection, list_exams, get_exam_results, get_student_history

def get_multi_exam_comparison():
    conn = get_connection()
    c = conn.cursor()
    
    # Get the two exams
    exams = list_exams()
    if len(exams) < 2:
        return {}
        
    exam1 = exams[0] # Paraf
    exam2 = exams[1] # NARTEST
    
    res1 = {r['name']: r for r in get_exam_results(exam1['id'])}
    res2 = {r['name']: r for r in get_exam_results(exam2['id'])}
    
    c.execute("SELECT id, school_no, name, pin FROM students ORDER BY CAST(school_no AS INTEGER) ASC")
    all_students = [dict(r) for r in c.fetchall()]
    conn.close()
    
    comparisons = {}
    
    for s in all_students:
        name = s['name']
        s_no = s['school_no']
        r1 = res1.get(name)
        r2 = res2.get(name)
        
        comp = {
            'student_id': s['id'],
            'name': name,
            'school_no': s_no,
            'pin': s['pin'],
            'has_both': bool(r1 and r2),
            'exam1_name': exam1['name'],
            'exam2_name': exam2['name'],
            'r1': r1,
            'r2': r2,
        }
        
        if r1 and r2:
            d_net = round(r2['top_net'] - r1['top_net'], 2)
            d_puan = round(r2['puan'] - r1['puan'], 2)
            d_cls_rank = r1['class_rank'] - r2['class_rank'] # positive is rank improvement
            d_sch_rank = r1['school_rank'] - r2['school_rank']
            
            sub_diffs = {
                'Türkçe': round(r2['tur_net'] - r1['tur_net'], 2),
                'İnkılap Tarihi': round(r2['ink_net'] - r1['ink_net'], 2),
                'Din Kültürü': round(r2['din_net'] - r1['din_net'], 2),
                'İngilizce': round(r2['ing_net'] - r1['ing_net'], 2),
                'Matematik': round(r2['mat_net'] - r1['mat_net'], 2),
                'Fen Bilimleri': round(r2['fen_net'] - r1['fen_net'], 2),
            }
            
            # Find best and worst sub
            best_sub = max(sub_diffs.items(), key=lambda x: x[1])
            worst_sub = min(sub_diffs.items(), key=lambda x: x[1])
            
            # Status badge
            if d_net >= 5.0:
                trend = "Çok Güçlü İlerleme"
                trend_icon = "🚀"
                trend_color = "0E6655"
            elif d_net >= 1.0:
                trend = "İstikrarlı Artış"
                trend_icon = "📈"
                trend_color = "145A32"
            elif d_net >= -1.0:
                trend = "Dengeli Seyir"
                trend_icon = "⚖️"
                trend_color = "595959"
            elif d_net >= -5.0:
                trend = "Hafif Düşüş"
                trend_icon = "⚠️"
                trend_color = "B7950B"
            else:
                trend = "Ciddi Gerileme"
                trend_icon = "🚨"
                trend_color = "900C3F"
                
            comp.update({
                'status': 'normal',
                'delta_net': d_net,
                'delta_puan': d_puan,
                'delta_cls_rank': d_cls_rank,
                'delta_sch_rank': d_sch_rank,
                'd_net': d_net,
                'd_puan': d_puan,
                'd_cls_rank': d_cls_rank,
                'd_sch_rank': d_sch_rank,
                'sub_diffs': sub_diffs,
                'best_sub': best_sub,
                'worst_sub': worst_sub,
                'trend': trend,
                'trend_icon': trend_icon,
                'trend_color': trend_color
            })
            
        elif r2 and not r1:
            comp.update({
                'status': 'new_student',
                'delta_net': 0.0,
                'delta_puan': 0.0,
                'delta_cls_rank': 0,
                'delta_sch_rank': 0,
                'd_net': 0.0,
                'd_puan': 0.0,
                'd_cls_rank': 0,
                'd_sch_rank': 0,
                'trend': 'İlk Deneme (Baz Sınav)',
                'trend_icon': '🌟',
                'trend_color': '1F497D',
                'note': 'Öğrencinin sistemdeki ilk deneme sınavıdır. Gelişim analizi sonraki denemede başlayacaktır.'
            })
        elif r1 and not r2:
            comp.update({
                'status': 'absent',
                'delta_net': 0.0,
                'delta_puan': 0.0,
                'delta_cls_rank': 0,
                'delta_sch_rank': 0,
                'd_net': 0.0,
                'd_puan': 0.0,
                'd_cls_rank': 0,
                'd_sch_rank': 0,
                'trend': 'Sınava Katılmadı',
                'trend_icon': '💤',
                'trend_color': '7F8C8D',
                'note': 'Öğrenci bu sınava mazeretli/raporlu olarak katılmamıştır. Önceki sınav verileri korunmaktadır.'
            })
            
        comparisons[name] = comp
        
    return comparisons

if __name__ == "__main__":
    comps = get_multi_exam_comparison()
    print(f"Total students analyzed: {len(comps)}")
    
    # Sort students by delta_net descending
    valid = [c for c in comps.values() if c['status'] == 'normal']
    valid.sort(key=lambda x: x['delta_net'], reverse=True)
    
    print("\n--- İKİ DENEME ARASI GELİŞİM SIRALAMASI (PARAF 1 -> NARTEST 1) ---")
    print(f"{'Sıra':<4} {'Öğrenci Adı':<24} {'Paraf Net':<10} {'Nartest Net':<12} {'Fark (Net)':<12} {'Fark (Puan)':<12} {'En Çok Gelişen':<16} {'Trend'}")
    print("-" * 105)
    for idx, c in enumerate(valid, 1):
        r1 = c['r1']
        r2 = c['r2']
        best = f"{c['best_sub'][0]} ({c['best_sub'][1]:+.2f})"
        diff_net_str = f"{c['delta_net']:+.2f}"
        diff_puan_str = f"{c['delta_puan']:+.2f}"
        print(f"{idx:<4} {c['name']:<24} {r1['top_net']:<10.2f} {r2['top_net']:<12.2f} {diff_net_str:<12} {diff_puan_str:<12} {best:<16} {c['trend_icon']} {c['trend']}")

    print("\n--- DİĞER DURUMLAR (Yeni Kayıt / Katılmayan) ---")
    others = [c for c in comps.values() if c['status'] != 'normal']
    for c in others:
        print(f" * {c['name']:<24} (No: {c['school_no']}) -> {c['trend_icon']} {c['trend']}: {c.get('note', '')}")
