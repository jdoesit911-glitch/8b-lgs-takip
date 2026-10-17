import numpy as np
import pandas as pd
from config import SUBJECTS, TIER_THRESHOLDS, KAZANIM_LEVELS

def analyze_class_performance(students):
    df = pd.DataFrame(students)
    if df.empty:
        return {}
        
    for col in ['tur_net', 'ink_net', 'din_net', 'ing_net', 'mat_net', 'fen_net', 'top_net', 'puan', 'score']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            
    score_col = 'score' if 'score' in df.columns and df['score'].sum() > 0 else ('puan' if 'puan' in df.columns else None)
    
    stats = {
        'count': len(df),
        'mean_net': float(df['top_net'].mean()),
        'median_net': float(df['top_net'].median()),
        'std_net': float(df['top_net'].std()),
        'min_net': float(df['top_net'].min()),
        'max_net': float(df['top_net'].max()),
        'mean_score': float(df[score_col].mean()) if score_col else 0.0,
        'subject_stats': {}
    }
    
    for sub, info in SUBJECTS.items():
        s_short = info['short']
        net_col = f"{s_short}_net"
        d_col = f"{s_short}_d"
        y_col = f"{s_short}_y"
        b_col = f"{s_short}_b"
        
        stats['subject_stats'][sub] = {
            'mean_net': float(df[net_col].mean()) if net_col in df.columns else 0.0,
            'total_d': int(df[d_col].sum()) if d_col in df.columns else 0,
            'total_y': int(df[y_col].sum()) if y_col in df.columns else 0,
            'total_b': int(df[b_col].sum()) if b_col in df.columns else 0,
            'total_net': float(df[net_col].sum()) if net_col in df.columns else 0.0
        }
        
    tiers = {t['tier']: [] for t in TIER_THRESHOLDS}
    for idx, r in df.iterrows():
        t_net = r['top_net']
        assigned = False
        for t in TIER_THRESHOLDS:
            if t['min_net'] <= t_net <= t['max_net']:
                tiers[t['tier']].append(r['name'])
                assigned = True
                break
        if not assigned:
            tiers[TIER_THRESHOLDS[-1]['tier']].append(r['name'])
            
    stats['tiers'] = tiers
    return stats

def calculate_pareto(students):
    df = pd.DataFrame(students)
    n = len(df)
    pareto_list = []
    
    total_loss_all = 0.0
    for sub, info in SUBJECTS.items():
        s_short = info['short']
        q_count = info['questions']
        max_possible = q_count * n
        actual_net = df[f"{s_short}_net"].sum() if f"{s_short}_net" in df.columns else 0.0
        lost_net = max_possible - actual_net
        total_y = int(df[f"{s_short}_y"].sum()) if f"{s_short}_y" in df.columns else 0
        total_b = int(df[f"{s_short}_b"].sum()) if f"{s_short}_b" in df.columns else 0
        total_loss_all += lost_net
        
        pareto_list.append({
            'subject': sub,
            'questions': q_count,
            'max_net': max_possible,
            'actual_net': actual_net,
            'lost_net': lost_net,
            'total_y': total_y,
            'total_b': total_b
        })
        
    df_p = pd.DataFrame(pareto_list).sort_values(by='lost_net', ascending=False).reset_index(drop=True)
    df_p['share_pct'] = (df_p['lost_net'] / total_loss_all) * 100.0 if total_loss_all > 0 else 0.0
    df_p['cum_pct'] = df_p['share_pct'].cumsum()
    df_p['rank'] = df_p.index + 1
    return df_p.to_dict('records')

def generate_support_groups(students, student_kazanims=None):
    groups = {
        "Grup 1: LGS Şampiyonlar & Full Hedefi (65+ Net)": [],
        "Grup 2: Matematik Atılım & Beceri Temelli Problem Grubu": [],
        "Grup 3: Türkçe Paragraf & Soru Kökü Modelleme Grubu": [],
        "Grup 4: Sınav Stratejisi & Negatif Net Engelleme Grubu": [],
        "Grup 5: Fen Bilimleri Kavram ve Deney Yorumlama Grubu": [],
        "Grup 6: Sözel Branşlar Kavram ve Full Çıkarma Grubu": []
    }
    
    for s in students:
        name = s['name']
        t_net = float(s.get('top_net', 0.0) or 0.0)
        mat_net = float(s.get('mat_net', 0.0) or 0.0)
        tur_net = float(s.get('tur_net', 0.0) or 0.0)
        fen_net = float(s.get('fen_net', 0.0) or 0.0)
        din_net = float(s.get('din_net', 0.0) or 0.0)
        ing_net = float(s.get('ing_net', 0.0) or 0.0)
        top_y = int(s.get('top_y', 0) or 0)
        
        if t_net >= 65.0:
            groups["Grup 1: LGS Şampiyonlar & Full Hedefi (65+ Net)"].append(name)
        if mat_net < 10.0:
            groups["Grup 2: Matematik Atılım & Beceri Temelli Problem Grubu"].append(name)
        if tur_net < 11.0:
            groups["Grup 3: Türkçe Paragraf & Soru Kökü Modelleme Grubu"].append(name)
        if top_y >= 30 or mat_net < 0 or din_net < 0 or ing_net < 0 or tur_net < 0:
            groups["Grup 4: Sınav Stratejisi & Negatif Net Engelleme Grubu"].append(name)
        if fen_net < 12.0:
            groups["Grup 5: Fen Bilimleri Kavram ve Deney Yorumlama Grubu"].append(name)
        if din_net < 6.0 or ing_net < 6.0:
            groups["Grup 6: Sözel Branşlar Kavram ve Full Çıkarma Grubu"].append(name)
            
    return groups

def diagnose_student(student, kazanims=None):
    t_net = float(student.get('top_net', 0.0) or 0.0)
    
    if t_net >= 75:
        t14 = round(min(t_net + 2.5, 90.0), 2)
        t28 = round(min(t_net + 5.0, 90.0), 2)
        quota = 450
        strat = "Türkiye derecesi ve zaman sınırlı zor soru pratiği."
    elif t_net >= 60:
        t14 = round(min(t_net + 3.5, 90.0), 2)
        t28 = round(min(t_net + 7.0, 90.0), 2)
        quota = 400
        strat = "Matematik yeni nesil problem modelleme ve süre tutma."
    elif t_net >= 40:
        t14 = round(min(t_net + 4.0, 90.0), 2)
        t28 = round(min(t_net + 8.0, 90.0), 2)
        quota = 350
        strat = "Matematik temel/orta seviye problem çözümü + Türkçe paragraf."
    elif t_net >= 25:
        t14 = round(min(t_net + 4.5, 90.0), 2)
        t28 = round(min(t_net + 9.0, 90.0), 2)
        quota = 280
        strat = "Kontrolsüz tahmini durdurma, iki şık arasında kalınca boş bırakma."
    else:
        t14 = round(min(t_net + 5.0, 90.0), 2)
        t28 = round(min(t_net + 10.0, 90.0), 2)
        quota = 210
        strat = "Acil sınav taktiği: Bilmediğini kesinlikle boş bırakma, temel kavramlar."
        
    zero_kaz = []
    low_kaz = []
    mastered_kaz = []
    
    if kazanims:
        for k in kazanims:
            rate_val = k.get('rate') if k.get('rate') is not None else k.get('success_rate', 0.0)
            try:
                rate = float(rate_val)
            except:
                rate = 0.0
                
            kaz_name = k.get('kazanim') or k.get('kazanim_name') or ''
            sub = k.get('subject', '')
            title = f"{sub}: {kaz_name}" if sub else kaz_name
            
            if rate == 0.0:
                zero_kaz.append(title)
            elif rate < 50.0:
                low_kaz.append(f"{title} (%{rate:.0f})")
            elif rate == 100.0:
                mastered_kaz.append(title)
                
    return {
        'target_14d': t14,
        'target_28d': t28,
        'weekly_quota': quota,
        'strategy': strat,
        'zero_kaz': zero_kaz,
        'low_kaz': low_kaz,
        'mastered_kaz': mastered_kaz
    }
