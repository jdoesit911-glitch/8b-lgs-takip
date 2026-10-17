import sqlite3
import os
from config import DATABASE_PATH

def get_connection():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        exam_date TEXT,
        publisher TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_no TEXT,
        name TEXT UNIQUE,
        class_name TEXT DEFAULT '8/B'
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS exam_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER,
        student_id INTEGER,
        tur_d INTEGER, tur_y INTEGER, tur_b INTEGER, tur_net REAL,
        ink_d INTEGER, ink_y INTEGER, ink_b INTEGER, ink_net REAL,
        din_d INTEGER, din_y INTEGER, din_b INTEGER, din_net REAL,
        ing_d INTEGER, ing_y INTEGER, ing_b INTEGER, ing_net REAL,
        mat_d INTEGER, mat_y INTEGER, mat_b INTEGER, mat_net REAL,
        fen_d INTEGER, fen_y INTEGER, fen_b INTEGER, fen_net REAL,
        top_d INTEGER, top_y INTEGER, top_b INTEGER, top_net REAL,
        score REAL,
        class_rank INTEGER,
        school_rank INTEGER,
        tg_rank INTEGER,
        tg_percentile REAL,
        FOREIGN KEY (exam_id) REFERENCES exams (id),
        FOREIGN KEY (student_id) REFERENCES students (id),
        UNIQUE (exam_id, student_id)
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS student_kazanim (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER,
        student_id INTEGER,
        subject TEXT,
        kazanim_name TEXT,
        success_rate REAL,
        FOREIGN KEY (exam_id) REFERENCES exams (id),
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS class_comparisons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER,
        subject TEXT,
        class_8a REAL,
        class_8b REAL,
        class_8c REAL,
        class_8d REAL,
        school_avg REAL,
        FOREIGN KEY (exam_id) REFERENCES exams (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def save_exam(exam_name, exam_date, publisher, students_data, kazanim_data=None, comparison_data=None):
    init_db()
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("INSERT OR IGNORE INTO exams (name, exam_date, publisher) VALUES (?, ?, ?)", (exam_name, exam_date, publisher))
    c.execute("SELECT id FROM exams WHERE name = ?", (exam_name,))
    exam_id = c.fetchone()['id']
    
    for s in students_data:
        name = s['name'].strip()
        num = str(s.get('num') or s.get('school_no') or '').strip()
        cls_name = s.get('class_name', '8/B')
        
        c.execute("INSERT OR IGNORE INTO students (school_no, name, class_name) VALUES (?, ?, ?)", (num, name, cls_name))
        if num and num != '':
            c.execute("UPDATE students SET school_no = ? WHERE name = ?", (num, name))
        c.execute("SELECT id FROM students WHERE name = ?", (name,))
        student_id = c.fetchone()['id']
        
        score_val = float(s.get('puan') if s.get('puan') is not None else s.get('score', 0.0))
        cls_r = int(s.get('cls_rank') if s.get('cls_rank') is not None else s.get('class_rank', 0))
        okul_r = int(s.get('okul_rank') if s.get('okul_rank') is not None else s.get('school_rank', 0))
        tg_r = int(s.get('tg_rank', 0) or 0)
        dilim_val = float(s.get('dilim') if s.get('dilim') is not None else s.get('tg_percentile', 0.0) or 0.0)
        
        c.execute('''
        INSERT OR REPLACE INTO exam_results (
            exam_id, student_id,
            tur_d, tur_y, tur_b, tur_net,
            ink_d, ink_y, ink_b, ink_net,
            din_d, din_y, din_b, din_net,
            ing_d, ing_y, ing_b, ing_net,
            mat_d, mat_y, mat_b, mat_net,
            fen_d, fen_y, fen_b, fen_net,
            top_d, top_y, top_b, top_net,
            score, class_rank, school_rank, tg_rank, tg_percentile
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            exam_id, student_id,
            s.get('tur_d', 0), s.get('tur_y', 0), s.get('tur_b', 0), s.get('tur_net', 0.0),
            s.get('ink_d', 0), s.get('ink_y', 0), s.get('ink_b', 0), s.get('ink_net', 0.0),
            s.get('din_d', 0), s.get('din_y', 0), s.get('din_b', 0), s.get('din_net', 0.0),
            s.get('ing_d', 0), s.get('ing_y', 0), s.get('ing_b', 0), s.get('ing_net', 0.0),
            s.get('mat_d', 0), s.get('mat_y', 0), s.get('mat_b', 0), s.get('mat_net', 0.0),
            s.get('fen_d', 0), s.get('fen_y', 0), s.get('fen_b', 0), s.get('fen_net', 0.0),
            s.get('top_d', 0), s.get('top_y', 0), s.get('top_b', 0), s.get('top_net', 0.0),
            score_val, cls_r, okul_r, tg_r, dilim_val
        ))
        
        if kazanim_data and name in kazanim_data:
            c.execute("DELETE FROM student_kazanim WHERE exam_id = ? AND student_id = ?", (exam_id, student_id))
            for k in kazanim_data[name]:
                c.execute('''
                INSERT INTO student_kazanim (exam_id, student_id, subject, kazanim_name, success_rate)
                VALUES (?, ?, ?, ?, ?)
                ''', (exam_id, student_id, k['subject'], k['kazanim'], k['rate']))
                
    if comparison_data:
        c.execute("DELETE FROM class_comparisons WHERE exam_id = ?", (exam_id,))
        for comp in comparison_data:
            c.execute('''
            INSERT INTO class_comparisons (exam_id, subject, class_8a, class_8b, class_8c, class_8d, school_avg)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (exam_id, comp['subject'], comp.get('8/A', 0.0), comp.get('8/B', 0.0), comp.get('8/C', 0.0), comp.get('8/D', 0.0), comp.get('school', 0.0)))

    conn.commit()
    conn.close()
    return exam_id

def list_exams():
    init_db()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM exams ORDER BY id ASC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_exam_results(exam_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
    SELECT r.*,
           r.score as puan,
           r.class_rank as cls_rank,
           r.school_rank as okul_rank,
           r.tg_percentile as dilim,
           s.name,
           s.school_no,
           s.school_no as num,
           s.class_name
    FROM exam_results r
    JOIN students s ON r.student_id = s.id
    WHERE r.exam_id = ?
    ORDER BY r.class_rank ASC
    ''', (exam_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_student_history(student_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
    SELECT e.name as exam_name, e.exam_date, r.*, r.score as puan
    FROM exam_results r
    JOIN exams e ON r.exam_id = e.id
    JOIN students s ON r.student_id = s.id
    WHERE s.name = ?
    ORDER BY e.id ASC
    ''', (student_name,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_student_kazanims(exam_id, student_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
    SELECT k.*, k.kazanim_name as kazanim, k.success_rate as rate
    FROM student_kazanim k
    JOIN students s ON k.student_id = s.id
    WHERE k.exam_id = ? AND s.name = ?
    ORDER BY k.id ASC
    ''', (exam_id, student_name))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_class_comparison(exam_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM class_comparisons WHERE exam_id = ?", (exam_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows
