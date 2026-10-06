import sqlite3
from datetime import datetime

DB_NAME = "credit_risk.db"

def init_db():
    """สร้างตารางเก็บบันทึกประวัติถ้ายังไม่มีในฐานข้อมูล"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            age INTEGER,
            income REAL,
            loan_amount REAL,
            credit_score INTEGER,
            result TEXT,
            risk_prob REAL,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_evaluation(user_id, age, income, loan_amount, credit_score, result, risk_prob):
    """บันทึกประวัติการคำนวณลงฐานข้อมูล"""
    init_db()  # สร้างตารางอัตโนมัติหากยังไม่มี
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO evaluations (user_id, age, income, loan_amount, credit_score, result, risk_prob, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, age, income, loan_amount, credit_score, result, risk_prob, created_at))
    
    conn.commit()
    conn.close()

def get_user_history(user_id=1):
    """ดึงข้อมูลประวัติการประเมินย้อนหลัง"""
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT age, income, loan_amount, credit_score, result, risk_prob, created_at
        FROM evaluations
        WHERE user_id = ?
        ORDER BY id DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows