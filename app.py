import os
import datetime
import importlib
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import streamlit.components.v1 as components
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & SESSION STATE
# ---------------------------------------------------------
st.set_page_config(
    page_title="CreditGuard AI | Financial Risk Assessment System",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None

if 'registered_users' not in st.session_state:
    st.session_state['registered_users'] = {
        'admin': {
            'password': '123',
            'name': 'ผู้ดูแลระบบ (Admin)',
            'role': 'เจ้าหน้าที่อนุมัติสินเชื่อ'
        }
    }

if 'eval_history' not in st.session_state:
    st.session_state['eval_history'] = [
        {
            "อายุ": 28,
            "รายได้ประจำ/ปี (บาท)": "฿420,000",
            "วงเงินกู้ (บาท)": "฿150,000",
            "ประวัติเครดิต (ปี)": 3,
            "ผลการประเมิน": "Low Risk",
            "โอกาสเสี่ยง AI (%)": "12.5%",
            "วันที่ประเมิน": "2026-10-05 10:30:00"
        },
        {
            "อายุ": 35,
            "รายได้ประจำ/ปี (บาท)": "฿300,000",
            "วงเงินกู้ (บาท)": "฿400,000",
            "ประวัติเครดิต (ปี)": 1,
            "ผลการประเมิน": "High Risk",
            "โอกาสเสี่ยง AI (%)": "88.2%",
            "วันที่ประเมิน": "2026-10-06 14:15:20"
        }
    ]

if 'calc_amount' not in st.session_state:
    st.session_state['calc_amount'] = 150000
if 'calc_rate' not in st.session_state:
    st.session_state['calc_rate'] = 9.5
if 'calc_years' not in st.session_state:
    st.session_state['calc_years'] = 3

# ---------------------------------------------------------
# HELPER: BLOCK BROWSER AUTOFILL VIA JS
# ---------------------------------------------------------
def block_browser_autofill():
    components.html(
        """
        <script>
        const clearAutofill = () => {
            const inputs = window.parent.document.querySelectorAll('input');
            inputs.forEach(input => {
                input.setAttribute('autocomplete', 'new-password');
                input.setAttribute('aria-autocomplete', 'none');
                input.setAttribute('disableautocomplete', 'true');
            });
        };
        clearAutofill();
        setTimeout(clearAutofill, 300);
        setTimeout(clearAutofill, 800);
        </script>
        """,
        height=0,
        width=0
    )

# ---------------------------------------------------------
# 2. ULTRA-MODERN GLASSMORPHISM & STYLESHEET
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Prompt:wght@300;400;500;600;700;800&display=swap');

header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0px !important;
}
.main .block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 95% !important;
}

/* Full Page Gradient Background */
.stApp {
    background: linear-gradient(135deg, #060911 0%, #0f172a 35%, #1e1b4b 70%, #2e1065 100%) !important;
    background-attachment: fixed !important;
    font-family: 'Prompt', 'Plus Jakarta Sans', sans-serif !important;
    color: #ffffff !important;
}

/* HIDE EMPTY CONTAINERS & ARTIFACTS */
div[data-testid="stMarkdownContainer"]:empty,
div[data-testid="element-container"]:empty {
    display: none !important;
}

/* HIGH-CONTRAST LABELS & HEADINGS */
label, .stWidgetLabel, div[data-testid="stWidgetLabel"] label, label p, label span, label div {
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.9) !important;
    letter-spacing: 0.3px !important;
}
div[data-testid="stMarkdownContainer"] p, div[data-testid="stMarkdownContainer"] span, h1, h2, h3, h4, h5, h6 {
    color: #f8fafc !important;
}
.stCaption, caption, div[data-testid="stCaptionContainer"] p {
    color: #38bdf8 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

/* Sleek Dark Input Boxes */
div[data-baseweb="input"] input, div[data-baseweb="base-input"] input {
    background-color: #0f172a !important;
    color: #ffffff !important;
    border: 1px solid rgba(168, 85, 247, 0.5) !important;
    border-radius: 12px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    padding: 12px 16px !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.4) !important;
}
div[data-baseweb="input"] input:focus, div[data-baseweb="base-input"] input:focus {
    border-color: #d946ef !important;
    box-shadow: 0 0 15px rgba(217, 70, 239, 0.5) !important;
}

/* GLASS METRIC CARDS */
.metric-glass-card {
    background: rgba(15, 23, 42, 0.7) !important;
    backdrop-filter: blur(18px) !important;
    border: 1px solid rgba(168, 85, 247, 0.4) !important;
    border-radius: 20px !important;
    padding: 22px 16px !important;
    text-align: center !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
    transition: all 0.3s ease !important;
    height: 100% !important;
}
.metric-glass-card:hover {
    transform: translateY(-4px) !important;
    border-color: #d946ef !important;
    box-shadow: 0 12px 35px rgba(217, 70, 239, 0.35) !important;
}
.metric-glass-title {
    color: #38bdf8 !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    margin-bottom: 8px !important;
    letter-spacing: 0.5px !important;
}
.metric-glass-value {
    color: #ffffff !important;
    font-size: 28px !important;
    font-weight: 800 !important;
    text-shadow: 0 2px 10px rgba(168, 85, 247, 0.6) !important;
}

/* TAB STYLING - PILL SWITCHES */
div[data-baseweb="tab-list"] {
    gap: 10px !important;
    background: rgba(15, 23, 42, 0.7) !important;
    padding: 6px !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    margin-bottom: 20px !important;
}
button[data-baseweb="tab"] {
    border-radius: 12px !important;
    padding: 10px 22px !important;
    color: #cbd5e1 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 18px rgba(168, 85, 247, 0.45) !important;
}
div[data-baseweb="tab-highlight"] { display: none !important; }

/* FORM STYLING - ST.FORM BECOMES GLASS CARD */
div[data-testid="stForm"] {
    background: rgba(15, 23, 42, 0.75) !important;
    backdrop-filter: blur(25px) !important;
    -webkit-backdrop-filter: blur(25px) !important;
    border: 1px solid rgba(168, 85, 247, 0.35) !important;
    border-radius: 24px !important;
    padding: 32px 28px !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(168, 85, 247, 0.2) !important;
}

/* SUBMIT & ACTION BUTTONS */
div[data-testid="stFormSubmitButton"] > button,
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #d946ef 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 14px 28px !important;
    box-shadow: 0 6px 20px rgba(168, 85, 247, 0.45) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 100% !important;
    cursor: pointer !important;
    margin-top: 10px !important;
}
div[data-testid="stFormSubmitButton"] > button:hover,
.stButton > button:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 10px 30px rgba(217, 70, 239, 0.65) !important;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #c026d3 100%) !important;
}

/* TOP RADIO MENU STYLING */
div[data-testid="stRadio"] > label { display: none !important; }
div[data-testid="stRadio"] > div[role="radiogroup"] {
    flex-direction: row !important;
    justify-content: center !important;
    gap: 12px !important;
    background: rgba(15, 23, 42, 0.7) !important;
    padding: 8px 12px !important;
    border-radius: 50px !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    margin-bottom: 24px !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.4) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] label {
    display: inline-flex !important;
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 40px !important;
    padding: 10px 24px !important;
    color: #cbd5e1 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    cursor: pointer !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] label:hover {
    background: rgba(168, 85, 247, 0.25) !important;
    border-color: #a855f7 !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] label[data-checked="true"] {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #d946ef 100%) !important;
    border-color: #f472b6 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    box-shadow: 0 6px 20px rgba(168, 85, 247, 0.5) !important;
}

.logout-btn button {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4) !important;
    font-size: 13px !important;
    padding: 8px 18px !important;
    border-radius: 30px !important;
}

/* DATAFRAME GLASS STYLING */
div[data-testid="stDataFrame"] {
    background: rgba(15, 23, 42, 0.65) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(168, 85, 247, 0.35) !important;
    border-radius: 18px !important;
    padding: 12px !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
}

/* Risk KPI Cards & Badges */
.kpi-glass-card {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(14px);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    text-align: center;
    transition: transform 0.3s ease;
}
.kpi-glass-card:hover {
    transform: translateY(-3px);
    border-color: #a855f7;
}
.kpi-title { font-size: 13px; color: #cbd5e1; font-weight: 600; margin-bottom: 6px; }
.kpi-value { font-size: 24px; font-weight: 800; color: #ffffff; }
.kpi-badge {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 11px; font-weight: 700; margin-top: 8px;
}
.kpi-badge-success { background: rgba(34, 197, 94, 0.25); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4); }
.kpi-badge-warning { background: rgba(245, 158, 11, 0.25); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
.kpi-badge-danger { background: rgba(239, 68, 68, 0.25); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }

.status-pill {
    display: inline-block; padding: 6px 16px; border-radius: 50px;
    font-weight: 700; font-size: 12px; text-align: center;
}
.status-pill-pass { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.5); }
.status-pill-fail { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.5); }

.knowledge-card {
    background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 20px;
    padding: 26px; height: 100%; transition: all 0.3s ease;
}
.knowledge-card:hover {
    transform: translateY(-5px); border-color: #a855f7;
    box-shadow: 0 12px 35px rgba(168, 85, 247, 0.3);
}
.knowledge-card-tag { font-size: 11px; font-weight: 800; color: #38bdf8; letter-spacing: 1px; margin-bottom: 8px; }
.knowledge-card-title { font-size: 19px; font-weight: 800; color: #ffffff; margin-bottom: 12px; }
.knowledge-card-desc { font-size: 14px; color: #cbd5e1; line-height: 1.6; margin-bottom: 16px; }
.knowledge-card-benchmark {
    background: rgba(15, 23, 42, 0.7); border-radius: 12px; padding: 12px 16px;
    border: 1px solid rgba(255, 255, 255, 0.1); font-size: 13px; color: #a7f3d0;
}

.auth-logo-badge {
    display: inline-flex; align-items: center; justify-content: center;
    padding: 10px 24px; border-radius: 50px;
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
    box-shadow: 0 10px 25px rgba(168, 85, 247, 0.4);
    font-size: 15px; font-weight: 800; color: #ffffff; margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. AUTHENTICATION (SPLIT HERO LOGIN SCREEN)
# ---------------------------------------------------------
if not st.session_state.get('logged_in', False):
    st.markdown("<br>", unsafe_allow_html=True)
    c_hero_left, c_spacer, c_hero_right = st.columns([1.2, 0.1, 1])

    with c_hero_left:
        hero_left_html = """<div style="padding-top: 10px;">
<div class="auth-logo-badge">🛡️️ CreditGuard AI Intelligence</div>
<h1 style="font-size: 36px; font-weight: 800; line-height: 1.25; margin-bottom: 16px; color: #ffffff;">
ระบบวิเคราะห์และประเมิน<br>อนุมัติสินเชื่อทางการเงิน
</h1>
<p style="color: #cbd5e1; font-size: 15px; line-height: 1.6; margin-bottom: 24px;">
ยกระดับมาตรฐานการพิจารณาสินเชื่อด้วย AI Machine Learning วิเคราะห์ความเสี่ยงรายบุคคล แม่นยำ รวดเร็ว และเป็นสัดส่วนตามหลัก Underwriting
</p>

<div style="background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 16px; padding: 16px 20px; margin-bottom: 14px; display: flex; align-items: center; gap: 16px;">
<div style="width: 46px; height: 46px; border-radius: 14px; background: linear-gradient(135deg, #6366f1, #a855f7); display: flex; align-items: center; justify-content: center; font-size: 22px; color: #ffffff; box-shadow: 0 6px 18px rgba(168, 85, 247, 0.4); flex-shrink: 0;">🧠</div>
<div>
<div style="font-weight: 700; color: #ffffff; font-size: 15px;">AI Credit Scoring Engine</div>
<div style="font-size: 13px; color: #94a3b8;">ประเมินโอกาสผิดนัดชำระด้วยสถิติจากชุดข้อมูลจริงในระบบ</div>
</div>
</div>

<div style="background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 16px; padding: 16px 20px; margin-bottom: 14px; display: flex; align-items: center; gap: 16px;">
<div style="width: 46px; height: 46px; border-radius: 14px; background: linear-gradient(135deg, #6366f1, #a855f7); display: flex; align-items: center; justify-content: center; font-size: 22px; color: #ffffff; box-shadow: 0 6px 18px rgba(168, 85, 247, 0.4); flex-shrink: 0;">📊</div>
<div>
<div style="font-weight: 700; color: #ffffff; font-size: 15px;">Real-time DTI & LTI Analytics</div>
<div style="font-size: 13px; color: #94a3b8;">คำนวณสัดส่วนภาระหนี้และค่างวดอัตโนมัติ พร้อมตรวจจับ Outlier</div>
</div>
</div>

<div style="background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 16px; padding: 16px 20px; margin-bottom: 14px; display: flex; align-items: center; gap: 16px;">
<div style="width: 46px; height: 46px; border-radius: 14px; background: linear-gradient(135deg, #6366f1, #a855f7); display: flex; align-items: center; justify-content: center; font-size: 22px; color: #ffffff; box-shadow: 0 6px 18px rgba(168, 85, 247, 0.4); flex-shrink: 0;">🔒</div>
<div>
<div style="font-weight: 700; color: #ffffff; font-size: 15px;">Enterprise Underwriting Policy</div>
<div style="font-size: 13px; color: #94a3b8;">ควบคู่ด้วย Hard Cut-off Rules เพิ่มความแม่นยำในการอนุมัติ</div>
</div>
</div>
</div>"""
        st.markdown(hero_left_html, unsafe_allow_html=True)

    with c_hero_right:
        tab_login, tab_register = st.tabs(["🔐 เข้าสู่ระบบ (Sign In)", "📝 สมัครสมาชิก (Sign Up)"])
        
        with tab_login:
            block_browser_autofill()
            
            with st.form("clean_login_form"):
                st.markdown("<h4 style='color: #ffffff; margin-bottom: 16px;'>เข้าสู่ระบบพอร์ทัล</h4>", unsafe_allow_html=True)
                
                username_input = st.text_input(
                    "ชื่อผู้ใช้งานระบบ", 
                    value="", 
                    key="login_user_v2", 
                    placeholder="เช่น admin"
                )
                password_input = st.text_input(
                    "รหัสผ่านเข้าใช้งาน", 
                    type="password", 
                    value="", 
                    key="login_pass_v2", 
                    placeholder="เช่น 123"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit_login = st.form_submit_button("เข้าสู่ระบบทันที")
                
                if submit_login:
                    users = st.session_state['registered_users']
                    user_key = username_input.strip().lower()
    
                    if not username_input or not password_input:
                        st.error("กรุณากรอกชื่อผู้ใช้งานและรหัสผ่าน")
                    elif user_key in users and users[user_key]['password'] == password_input:
                        st.session_state['logged_in'] = True
        
                        st.session_state['user_info'] = {
                            'id': user_key,  # 1. แก้ตรงนี้: จาก 1 เปลี่ยนเป็น user_key
                            'name': users[user_key]['name'],
                            'username': user_key,
                            'role': users[user_key].get('role', 'ผู้ใช้งาน')
                        }
                        st.session_state['eval_history'] = []  # 2. เพิ่มบรรทัดนี้: ล้างประวัติชั่วคราวเก่าทิ้ง
        
                        st.success(f"เข้าสู่ระบบสำเร็จ ยินดีต้อนรับ {users[user_key]['name']}")
                        st.rerun()
                    else:
                        st.error("ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง")

        with tab_register:
            block_browser_autofill()
            with st.form("clean_register_form"):
                st.markdown("<h4 style='color: #ffffff; margin-bottom: 16px;'>ลงทะเบียนสมาชิกใหม่</h4>", unsafe_allow_html=True)
                reg_fullname = st.text_input("ชื่อ-นามสกุล", value="", placeholder="เช่น สมชาย ใจดี", key="reg_name_v2")
                reg_username = st.text_input("ชื่อผู้ใช้งานระบบ", value="", placeholder="เช่น somchai_c", key="reg_user_v2")
                reg_password = st.text_input("กำหนดรหัสผ่าน", type="password", value="", placeholder="กำหนดรหัสผ่าน", key="reg_pass_v2")
                reg_confirm_pass = st.text_input("ยืนยันรหัสผ่านอีกครั้ง", type="password", value="", placeholder="ยืนยันรหัสผ่านอีกครั้ง", key="reg_conf_v2")
                reg_role = st.selectbox(
                    "ตำแหน่ง / บทบาทหน้าที่",
                    ["เจ้าหน้าที่อนุมัติสินเชื่อ (Credit Officer)", "ผู้จัดการฝ่ายสินเชื่อ (Manager)", "นักวิเคราะห์ความเสี่ยง (Risk Analyst)"]
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit_register = st.form_submit_button("ยืนยันการสมัครสมาชิก")
                
                if submit_register:
                    reg_user_clean = reg_username.strip().lower()
                    users = st.session_state['registered_users']
                    if not reg_fullname or not reg_user_clean or not reg_password:
                        st.error("กรุณากรอกข้อมูลให้ครบถ้วนทุกช่อง")
                    elif reg_password != reg_confirm_pass:
                        st.error("รหัสผ่านทั้งสองช่องไม่ตรงกัน")
                    elif reg_user_clean in users:
                        st.error(f"ชื่อผู้ใช้งาน '{reg_user_clean}' ถูกใช้งานแล้ว")
                    else:
                        st.session_state['registered_users'][reg_user_clean] = {
                            'password': reg_password,
                            'name': reg_fullname,
                            'role': reg_role
                        }
                        st.session_state['logged_in'] = False
                        st.session_state['user_info'] = None
                        st.session_state['eval_history'] = []  # เคลียร์ประวัติค้าง
                        st.success("🎉 สมัครสมาชิกเสร็จสิ้น! ท่านสามารถสลับไปที่แท็บ 'เข้าสู่ระบบ' เพื่อใช้งานได้ทันที")
                        st.toast("สมัครสมาชิกเสร็จสิ้นเรียบร้อยแล้ว!", icon="✅")

                        st.balloons()

    st.stop()

# ---------------------------------------------------------
# 4. HELPER FUNCTIONS & DATASET ENGINE
# ---------------------------------------------------------
FEATURE_COLS = ['person_age', 'person_income', 'loan_amnt', 'loan_int_rate', 'cb_person_cred_hist_length']

class FallbackModel:
    def predict(self, df):
        probs = self.predict_proba(df)[:, 1]
        return (probs >= 0.5).astype(int)
    
    def predict_proba(self, df):
        results = []
        for _, row in df.iterrows():
            dti = ((row['loan_amnt'] / 36) + 5000) / (row['person_income'] / 12) * 100 if row['person_income'] > 0 else 100
            lti = row['loan_amnt'] / row['person_income'] if row['person_income'] > 0 else 10
            risk = 15.0
            if dti > 50: risk += 30.0
            if lti > 0.5: risk += 25.0
            if row['cb_person_cred_hist_length'] < 2: risk += 20.0
            if row['person_age'] < 22: risk += 10.0
            prob = min(max(risk, 5.0), 99.0) / 100.0
            results.append([1.0 - prob, prob])
        return np.array(results)

@st.cache_resource
def load_model():
    try:
        if os.path.exists('model.pkl'):
            return joblib.load('model.pkl')
    except Exception:
        pass
    return FallbackModel()

@st.cache_data
def load_raw_dataset():
    csv_file = 'credit_risk_dataset.csv' if os.path.exists('credit_risk_dataset.csv') else ('data.csv' if os.path.exists('data.csv') else None)
    if not csv_file:
        return None
    df = pd.read_csv(csv_file)
    data_clean = df.dropna(subset=FEATURE_COLS + ['loan_status']).copy()
    return data_clean

@st.cache_resource
def prepare_knn_engine():
    data_clean = load_raw_dataset()
    if data_clean is None or len(data_clean) < 5:
        return None, None
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(data_clean[FEATURE_COLS])
    nn_model = NearestNeighbors(n_neighbors=min(5, len(data_clean)), metric='euclidean')
    nn_model.fit(X_scaled)
    return scaler, nn_model

model = load_model()
raw_df = load_raw_dataset()
scaler_knn, knn_engine = prepare_knn_engine()

try:
    import database as db
    importlib.reload(db)
    if hasattr(db, 'init_db'):
        db.init_db()
except Exception:
    db = None

def calculate_monthly_payment(principal, annual_rate, years):
    if annual_rate == 0 or years == 0:
        return principal / (years * 12) if years > 0 else principal
    r = (annual_rate / 100) / 12
    n = years * 12
    pmt = principal * (r * (1 + r)**n) / ((1 + r)**n - 1)
    return pmt

def generate_amortization_schedule(principal, annual_rate, years):
    pmt = calculate_monthly_payment(principal, annual_rate, years)
    total_months = years * 12
    m_rate = (annual_rate / 100) / 12
    bal = principal
    schedule = []
    
    for month in range(1, total_months + 1):
        interest = bal * m_rate
        principal_paid = pmt - interest
        if month == total_months:
            principal_paid = bal
            pmt_final = principal_paid + interest
        else:
            pmt_final = pmt
        bal = max(0, bal - principal_paid)
        schedule.append({
            'งวดที่ (Month)': month,
            'ค่างวด (บาท)': round(pmt_final, 2),
            'เงินต้น (บาท)': round(principal_paid, 2),
            'ดอกเบี้ย (บาท)': round(interest, 2),
            'เงินต้นคงเหลือ (บาท)': round(bal, 2)
        })
    return pd.DataFrame(schedule)

def find_similar_records(input_df, k=5):
    if raw_df is None or knn_engine is None or scaler_knn is None:
        return None
    input_scaled = scaler_knn.transform(input_df[FEATURE_COLS])
    k_actual = min(k, len(raw_df))
    distances, indices = knn_engine.kneighbors(input_scaled, n_neighbors=k_actual)
    similar_rows = raw_df.iloc[indices[0]].copy()
    similar_rows['สถานะจริงในระบบ'] = similar_rows['loan_status'].apply(
        lambda x: "อนุมัติ (Low Risk)" if x == 0 else "ไม่อนุมัติ (High Risk)"
    )
    display_df = similar_rows[[
        'person_age', 'person_income', 'loan_amnt', 'loan_int_rate', 'cb_person_cred_hist_length', 'สถานะจริงในระบบ'
    ]].copy()
    display_df.columns = [
        'อายุ (ปี)', 'รายได้ต่อปี (บาท)', 'วงเงินกู้ (บาท)', 'อัตราดอกเบี้ย (%)', 'ประวัติเครดิต (ปี)', 'สถานะจริงในระบบ'
    ]
    display_df['รายได้ต่อปี (บาท)'] = display_df['รายได้ต่อปี (บาท)'].map('{:,.0f}'.format)
    display_df['วงเงินกู้ (บาท)'] = display_df['วงเงินกู้ (บาท)'].map('{:,.0f}'.format)
    display_df['อัตราดอกเบี้ย (%)'] = display_df['อัตราดอกเบี้ย (%)'].map('{:.2f}%'.format)
    return display_df

def create_risk_gauge(risk_prob):
    risk_prob = min(max(float(risk_prob), 0.0), 100.0)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_prob,
        number = {'suffix': "%", 'font': {'size': 26, 'color': "#ffffff", 'family': "Prompt"}},
        title = {'text': "มาตรวัดความเสี่ยง AI (Risk Gauge)", 'font': {'size': 13, 'color': "#38bdf8", 'family': "Prompt"}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#cbd5e1"},
            'bar': {'color': "#a855f7" if risk_prob < 50 else "#ef4444", 'thickness': 0.3},
            'bgcolor': "rgba(15, 23, 42, 0.5)",
            'borderwidth': 1,
            'bordercolor': "rgba(255, 255, 255, 0.2)",
            'steps': [
                {'range': [0, 30], 'color': 'rgba(34, 197, 94, 0.3)'},
                {'range': [30, 60], 'color': 'rgba(245, 158, 11, 0.3)'},
                {'range': [60, 100], 'color': 'rgba(239, 68, 68, 0.3)'}
            ],
        }
    ))
    fig.update_layout(
        height=200,
        margin=dict(l=15, r=15, t=25, b=15),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#ffffff", 'family': "Prompt"}
    )
    return fig

# ---------------------------------------------------------
# 5. TOP NAVBAR & NAVIGATION BAR
# ---------------------------------------------------------
c_top_left, c_top_right = st.columns([3, 1])

with c_top_left:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="background: linear-gradient(135deg, #6366f1, #a855f7); padding: 8px 20px; border-radius: 30px; font-weight: 800; font-size: 18px; color: #ffffff; box-shadow: 0 4px 15px rgba(168,85,247,0.4);">
                CreditGuard AI
            </div>
            <div>
                <h3 style="margin: 0; color: #ffffff; font-weight: 800; font-size: 22px;">ระบบวิเคราะห์และประเมินอนุมัติสินเชื่อ</h3>
                <p style="margin: 0; color: #38bdf8; font-size: 13px;">Financial Underwriting System & Risk Analytics Portal</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

with c_top_right:
    current_user_name = st.session_state.get('user_info', {}).get('name', 'ผู้ใช้งาน')
    current_user_role = st.session_state.get('user_info', {}).get('role', 'เจ้าหน้าที่')
    
    col_u1, col_u2 = st.columns([2, 1])
    with col_u1:
        st.markdown(f"""
            <div style="text-align: right;">
                <div style="font-weight: 700; color: #ffffff; font-size: 14px;">{current_user_name}</div>
                <div style="font-size: 12px; color: #38bdf8;">{current_user_role}</div>
            </div>
        """, unsafe_allow_html=True)
    with col_u2:
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("ออกจากระบบ", key="top_logout"):
            st.session_state['logged_in'] = False
            st.session_state['user_info'] = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

menu = st.radio(
    "",
    [
        "ประเมินและอนุมัติสินเชื่อ", 
        "คำนวณค่างวด และตารางผ่อน", 
        "ประวัติการประเมิน", 
        "ศูนย์ความรู้ Credit Risk"
    ],
    horizontal=True,
    key="top_navigation_menu"
)

# ---------------------------------------------------------
# 6. MAIN APPLICATION PAGES
# ---------------------------------------------------------

# =========================================================
# PAGE 1: ประเมินและอนุมัติสินเชื่อ
# =========================================================
if menu == "ประเมินและอนุมัติสินเชื่อ":
    col_input1, col_input2 = st.columns(2)

    with col_input1:
        st.markdown("<h4 style='color: #ffffff; margin-bottom: 16px;'>ข้อมูลส่วนบุคคลและรายได้</h4>", unsafe_allow_html=True)
        # เปลี่ยน value=30 เป็น value=None
        age = st.number_input(
            "อายุผู้ขอสินเชื่อ (ปี) [person_age]", 
            min_value=18, max_value=100, value=None, placeholder="เช่น 30", step=1
        )
        # เปลี่ยน value=45000 เป็น value=None
        monthly_income = st.number_input(
            "รายได้ประจำต่อเดือน (บาท)", 
            min_value=1000, value=None, placeholder="เช่น 45000", step=1000, format="%d"
        )
        
        annual_income = (monthly_income * 12) if monthly_income else 0
        st.caption(f"รายได้รวมต่อปี (person_income): ฿{annual_income:,.0f}")

        # เปลี่ยน value=5000 เป็น value=None
        existing_debt = st.number_input(
            "ภาระหนี้ผ่อนเดิมต่อเดือน (บาท)", 
            min_value=0, value=None, placeholder="เช่น 5000 (หากไม่มีให้ใส่ 0)", step=500, format="%d",
            help="รวมค่างวดผ่อนบ้าน รถ บัตรเครดิตที่มีอยู่แล้ว"
        )

    with col_input2:
        st.markdown("<h4 style='color: #ffffff; margin-bottom: 16px;'>ข้อมูลสินเชื่อและประวัติเครดิต</h4>", unsafe_allow_html=True)
        # เปลี่ยน value=150000 เป็น value=None
        loan_amount = st.number_input(
            "วงเงินกู้ที่ต้องการ (บาท) [loan_amnt]", 
            min_value=1000, value=None, placeholder="เช่น 150000", step=5000, format="%d"
        )
        # เปลี่ยน value=9.5 เป็น value=None
        interest_rate = st.number_input(
            "อัตราดอกเบี้ยต่อปี (%) [loan_int_rate]", 
            min_value=0.1, max_value=40.0, value=None, placeholder="เช่น 9.5", step=0.1
        )
        # เปลี่ยน value=4 เป็น value=None
        cred_hist_length = st.number_input(
            "ระยะเวลาประวัติเครดิต (ปี) [cb_person_cred_hist_length]", 
            min_value=0, max_value=50, value=None, placeholder="เช่น 4", step=1
        )
        loan_years = st.slider("ระยะเวลาผ่อนชำระที่ต้องการ (ปี)", min_value=1, max_value=7, value=int(st.session_state.get('calc_years', 3)))

    st.markdown("<br>", unsafe_allow_html=True)
    process_btn = st.button("ประมวลผลวิเคราะห์อนุมัติสินเชื่อ")

    # ตรวจสอบว่าผู้ใช้กรอกข้อมูลครบถ้วนหรือไม่ก่อนเริ่มประมวลผล
    if age is None or monthly_income is None or loan_amount is None or interest_rate is None or cred_hist_length is None:
        st.info("💡 กรุณากรอกข้อมูลผู้ขอสินเชื่อและข้อมูลการกู้ให้ครบถ้วนทุกช่องเพื่อประเมินผล")
        st.stop()

    debt_val = existing_debt if existing_debt is not None else 0

    st.session_state['calc_amount'] = loan_amount
    st.session_state['calc_rate'] = interest_rate
    st.session_state['calc_years'] = loan_years

    new_installment = calculate_monthly_payment(loan_amount, interest_rate, loan_years)
    total_monthly_debt = debt_val + new_installment
    dti_ratio = (total_monthly_debt / monthly_income) * 100 if monthly_income > 0 else 0
    lti_ratio = loan_amount / annual_income if annual_income > 0 else 0

    input_data = pd.DataFrame([{
        'person_age': age,
        'person_income': annual_income,
        'loan_amnt': loan_amount,
        'loan_int_rate': interest_rate,
        'cb_person_cred_hist_length': cred_hist_length
    }])

    model_prediction = model.predict(input_data)[0]
    if hasattr(model, 'predict_proba'):
        raw_prob_risk = model.predict_proba(input_data)[0][1] * 100
    else:
        raw_prob_risk = 75.0 if model_prediction == 1 else 15.0

    prob_risk = raw_prob_risk
    is_hard_rejected = False
    reject_reasons = []

    if dti_ratio > 70:
        is_hard_rejected = True
        reject_reasons.append(f"ภาระหนี้รวมต่อรายได้ (DTI = {dti_ratio:,.1f}%) สูงเกินเพดานความเสี่ยงวิกฤตของสถาบันการเงิน (ไม่เกิน 70%)")
        prob_risk = max(prob_risk, 99.9)

    if lti_ratio > 5.0:
        is_hard_rejected = True
        reject_reasons.append(f"สัดส่วนวงเงินกู้ต่อรายได้ปี (LTI = {lti_ratio:,.1f} เท่า) สูงเกินเกณฑ์เพดานอนุมัติ (ไม่เกิน 5 เท่า)")
        prob_risk = max(prob_risk, 99.9)

    result_text = "High Risk" if (is_hard_rejected or prob_risk >= 50 or model_prediction == 1) else "Low Risk"

    if process_btn:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_eval_record = {
            "อายุ": age,
            "รายได้ประจำ/ปี (บาท)": f"฿{annual_income:,.0f}",
            "วงเงินกู้ (บาท)": f"฿{loan_amount:,.0f}",
            "ประวัติเครดิต (ปี)": cred_hist_length,
            "ผลการประเมิน": result_text,
            "โอกาสเสี่ยง AI (%)": f"{prob_risk:.1f}%",
            "วันที่ประเมิน": now_str
        }
        st.session_state['eval_history'].insert(0, new_eval_record)
        
        if db is not None:
            try:
                user_id = st.session_state.get('user_info', {}).get('id', 1)
                if hasattr(db, 'save_evaluation'):
                    try:
                        db.save_evaluation(
                            user_id=user_id, age=age, income=annual_income,
                            loan_amount=loan_amount, credit_score=cred_hist_length,
                            result=result_text, risk_prob=prob_risk
                        )
                    except TypeError:
                        db.save_evaluation(user_id, age, annual_income, loan_amount, cred_hist_length, result_text, prob_risk)
            except Exception as e:
                pass
        st.toast("บันทึกประวัติการประเมินเข้าสู่ระบบเรียบร้อยแล้ว")

    # DISPLAY UNDERWRITING DASHBOARD
    st.markdown("---")
    st.markdown("<h3 style='color: #ffffff; margin-bottom: 20px;'>สรุปผลการวิเคราะห์ทางการเงิน (Underwriting Dashboard)</h3>", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
            <div class="kpi-glass-card">
                <div class="kpi-title">ค่างวดผ่อนใหม่ / เดือน</div>
                <div class="kpi-value">฿{new_installment:,.0f}</div>
                <div class="kpi-badge kpi-badge-success">คำนวณตามสัญญา</div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        badge_class = "kpi-badge-success" if dti_ratio <= 50 else "kpi-badge-danger"
        st.markdown(f"""
            <div class="kpi-glass-card">
                <div class="kpi-title">สัดส่วนภาระหนี้รวม (DTI)</div>
                <div class="kpi-value">{dti_ratio:,.1f}%</div>
                <div class="kpi-badge {badge_class}">{"เกณฑ์ปลอดภัย (<50%)" if dti_ratio <= 50 else "ภาระหนี้สูงเกินเกณฑ์"}</div>
            </div>
        """, unsafe_allow_html=True)
    with k3:
        badge_class = "kpi-badge-success" if lti_ratio <= 0.5 else "kpi-badge-warning"
        st.markdown(f"""
            <div class="kpi-glass-card">
                <div class="kpi-title">วงเงินกู้ / รายได้ปี (LTI)</div>
                <div class="kpi-value">{lti_ratio:,.2f} เท่า</div>
                <div class="kpi-badge {badge_class}">{"อยู่ในเกณฑ์ปกติ" if lti_ratio <= 0.5 else "วงเงินสูงเมื่อเทียบรายได้"}</div>
            </div>
        """, unsafe_allow_html=True)
    with k4:
        badge_class = "kpi-badge-success" if prob_risk < 30 else ("kpi-badge-warning" if prob_risk < 60 else "kpi-badge-danger")
        st.markdown(f"""
            <div class="kpi-glass-card">
                <div class="kpi-title">โอกาสผิดนัดชำระ (AI)</div>
                <div class="kpi-value">{prob_risk:.1f}%</div>
                <div class="kpi-badge {badge_class}">{"ความเสี่ยงต่ำ" if prob_risk < 30 else ("ความเสี่ยงปานกลาง" if prob_risk < 60 else "ความเสี่ยงสูงวิกฤต")}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c_status, c_gauge = st.columns([1.4, 1])
    with c_status:
        if is_hard_rejected or prob_risk >= 50 or model_prediction == 1:
            reasons_html = "".join([f"<li>{r}</li>" for r in reject_reasons])
            st.markdown(f"""
                <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.5); border-left: 6px solid #ef4444; border-radius: 18px; padding: 24px; height: 100%;">
                    <h4 style="color: #f87171; margin: 0 0 10px 0;">ปฏิเสธการอนุมัติ / ความเสี่ยงสูงวิกฤต (Rejected - High Risk)</h4>
                    <p style="color: #cbd5e1; margin: 0; font-size: 14px; line-height: 1.6;">
                        <b>สาเหตุที่ไม่ผ่านการอนุมัติ:</b>
                        <ul style="margin-top: 6px; padding-left: 20px; color: #fca5a5;">
                            {reasons_html if reject_reasons else '<li>โอกาสผิดนัดชำระประเมินโดย AI สูงเกินเกณฑ์ยอมรับได้</li>'}
                        </ul>
                    </p>
                </div>
            """, unsafe_allow_html=True)
        elif dti_ratio > 50:
            st.markdown(f"""
                <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.5); border-left: 6px solid #f59e0b; border-radius: 18px; padding: 24px; height: 100%;">
                    <h4 style="color: #fbbf24; margin: 0 0 10px 0;">อนุมัติแบบมีเงื่อนไข (Conditional Approval)</h4>
                    <p style="color: #cbd5e1; margin: 0; font-size: 14px; line-height: 1.6;">
                        ผลการวิเคราะห์ AI ผ่านเกณฑ์ แต่สัดส่วนภาระหนี้รวม (DTI) สูงถึง <b>{dti_ratio:.1f}%</b> แนะนำปรับลดวงเงินกู้ หรือขยายระยะเวลาผ่อน
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.5); border-left: 6px solid #22c55e; border-radius: 18px; padding: 24px; height: 100%;">
                    <h4 style="color: #4ade80; margin: 0 0 10px 0;">ผ่านการประเมินอนุมัติเบื้องต้น (Approved - Low Risk)</h4>
                    <p style="color: #cbd5e1; margin: 0; font-size: 14px; line-height: 1.6;">
                        ผู้ขอสินเชื่อมีความเสี่ยงต่ำ สัดส่วนภาระหนี้ต่อรายได้อยู่ในเกณฑ์ปลอดภัยตามมาตรฐานสถาบันการเงิน
                    </p>
                </div>
            """, unsafe_allow_html=True)

    with c_gauge:
        fig_g = create_risk_gauge(prob_risk)
        st.plotly_chart(fig_g, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #ffffff;'>ตารางวิเคราะห์ปัจจัยเสี่ยง (Risk Factor Badges)</h4>", unsafe_allow_html=True)

    pill_dti = f'<span class="status-pill status-pill-pass">ผ่านเกณฑ์</span>' if dti_ratio <= 50 else f'<span class="status-pill status-pill-fail">ไม่ผ่านเกณฑ์</span>'
    pill_hist = f'<span class="status-pill status-pill-pass">ผ่านเกณฑ์</span>' if cred_hist_length >= 2 else f'<span class="status-pill status-pill-fail">ไม่ผ่านเกณฑ์</span>'
    pill_lti = f'<span class="status-pill status-pill-pass">ผ่านเกณฑ์</span>' if lti_ratio <= 0.5 else f'<span class="status-pill status-pill-fail">ไม่ผ่านเกณฑ์</span>'

    rf_html = f"""
    <div style="background: rgba(15, 23, 42, 0.7); border-radius: 16px; padding: 18px; border: 1px solid rgba(255,255,255,0.15);">
        <table style="width: 100%; color: #ffffff; border-collapse: collapse;">
            <thead>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.2); text-align: left; font-size: 14px; color: #38bdf8;">
                    <th style="padding: 12px;">ปัจจัยการพิจารณา</th>
                    <th style="padding: 12px;">ค่าที่ได้</th>
                    <th style="padding: 12px;">เกณฑ์มาตรฐาน</th>
                    <th style="padding: 12px; text-align: center;">สถานะประเมิน</th>
                </tr>
            </thead>
            <tbody style="font-size: 14px;">
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);">
                    <td style="padding: 14px; font-weight: 600;">สัดส่วนภาระหนี้ต่อรายได้ (DTI Ratio)</td>
                    <td style="padding: 14px;">{dti_ratio:,.1f}%</td>
                    <td style="padding: 14px;">ไม่เกิน 50%</td>
                    <td style="padding: 14px; text-align: center;">{pill_dti}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.08);">
                    <td style="padding: 14px; font-weight: 600;">ระยะเวลาประวัติเครดิต (Credit History)</td>
                    <td style="padding: 14px;">{cred_hist_length} ปี</td>
                    <td style="padding: 14px;">2 ปีขึ้นไป</td>
                    <td style="padding: 14px; text-align: center;">{pill_hist}</td>
                </tr>
                <tr>
                    <td style="padding: 14px; font-weight: 600;">สัดส่วนวงเงินกู้ต่อรายได้ปี (LTI Ratio)</td>
                    <td style="padding: 14px;">{lti_ratio:,.2f} เท่า</td>
                    <td style="padding: 14px;">ไม่เกิน 0.5 เท่า</td>
                    <td style="padding: 14px; text-align: center;">{pill_lti}</td>
                </tr>
            </tbody>
        </table>
    </div>
    """
    st.markdown(rf_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #ffffff;'>ข้อมูลประวัติจริงในระบบที่ใกล้เคียงที่สุด (Top 5 Matches)</h3>", unsafe_allow_html=True)
    similar_df = find_similar_records(input_data, k=5)
    if similar_df is not None:
        st.dataframe(similar_df, use_container_width=True, hide_index=True)
    else:
        st.info("💡 ระบบกำลังประมวลผลด้วย Rule-based Engine (นำไฟล์ dataset มาใส่ในโฟลเดอร์เพื่อเปรียบเทียบ KNN Matches)")

# =========================================================
# PAGE 2: คำนวณค่างวด & ตารางผ่อน
# =========================================================
elif menu == "คำนวณค่างวด และตารางผ่อน":
    c1, c2, c3 = st.columns(3)
    with c1:
        calc_amount = st.number_input("วงเงินกู้ (บาท)", min_value=5000, value=int(st.session_state['calc_amount']), step=10000, format="%d", key="calc_p2_amount")
    with c2:
        calc_rate = st.number_input("อัตราดอกเบี้ยต่อปี (%)", min_value=0.1, value=float(st.session_state['calc_rate']), step=0.1, key="calc_p2_rate")
    with c3:
        calc_years = st.number_input("ระยะเวลาผ่อน (ปี)", min_value=1, value=int(st.session_state['calc_years']), step=1, key="calc_p2_years")

    st.session_state['calc_amount'] = calc_amount
    st.session_state['calc_rate'] = calc_rate
    st.session_state['calc_years'] = calc_years

    pmt = calculate_monthly_payment(calc_amount, calc_rate, calc_years)
    total_months = calc_years * 12
    total_payment = pmt * total_months
    total_interest = total_payment - calc_amount

    st.markdown("<br>", unsafe_allow_html=True)
    col_m1, col_m2, col_m3 = st.columns(3)
    
    with col_m1:
        st.markdown(f"""
            <div class="metric-glass-card">
                <div class="metric-glass-title">ค่างวดผ่อนต่อเดือน</div>
                <div class="metric-glass-value">฿{pmt:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_m2:
        st.markdown(f"""
            <div class="metric-glass-card">
                <div class="metric-glass-title">ดอกเบี้ยรวมทั้งหมด</div>
                <div class="metric-glass-value">฿{total_interest:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_m3:
        st.markdown(f"""
            <div class="metric-glass-card">
                <div class="metric-glass-title">ยอดชำระรวมทั้งสิ้น</div>
                <div class="metric-glass-value">฿{total_payment:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cg1, cg2 = st.columns(2)

    with cg1:
        fig_pie = px.pie(
            names=["เงินต้น (Principal)", "ดอกเบี้ยรวม (Interest)"],
            values=[calc_amount, max(0, total_interest)],
            title="สัดส่วนเงินต้นเทียบดอกเบี้ยรวม",
            color_discrete_sequence=["#6366f1", "#d946ef"],
            hole=0.4
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#ffffff", family="Prompt")
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with cg2:
        df_schedule = generate_amortization_schedule(calc_amount, calc_rate, calc_years)
        
        fig_line = px.line(
            df_schedule, 
            x='งวดที่ (Month)', 
            y='เงินต้นคงเหลือ (บาท)', 
            title="แนวโน้มการลดลงของเงินต้นคงเหลือตามงวดผ่อน",
            markers=True
        )
        fig_line.update_traces(line_color='#38bdf8', line_width=3)
        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#ffffff", family="Prompt"),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #ffffff;'>ตารางผ่อนชำระรายเดือน (Amortization Schedule)</h4>", unsafe_allow_html=True)
    
    st.dataframe(df_schedule, use_container_width=True, hide_index=True)
    
    csv_data = df_schedule.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 ดาวน์โหลดตารางผ่อนชำระ (CSV)",
        data=csv_data,
        file_name=f"Loan_Amortization_Schedule_{calc_amount}.csv",
        mime="text/csv"
    )

# =========================================================
# PAGE 3: ประวัติการประเมิน
# =========================================================
elif menu == "ประวัติการประเมิน":
    st.markdown("<h3 style='color: #ffffff; margin-bottom: 20px;'>ประวัติการประเมินและวิเคราะห์สินเชื่อ</h3>", unsafe_allow_html=True)
    
    db_rows = []
    if db is not None and hasattr(db, 'get_user_history'):
        try:
            user_id = st.session_state.get('user_info', {}).get('id', 1)
            db_rows = db.get_user_history(user_id)
        except Exception:
            pass

    # เริ่มต้นเป็นรายการว่าง (ไม่นำประวัติค้างของคนอื่นมาใส่)
    history_list = []
    
    if db_rows:
        cols = ["age", "income", "loan_amount", "credit_score", "result", "risk_prob", "created_at"]
        for r in db_rows:
            r_dict = dict(zip(cols, r)) if isinstance(r, (tuple, list)) else (r if isinstance(r, dict) else {})
            
            history_list.append({
                "อายุ": r_dict.get('age', '--'),
                "รายได้ประจำ/ปี (บาท)": f"฿{r_dict.get('income', 0):,.0f}" if isinstance(r_dict.get('income'), (int, float)) else str(r_dict.get('income', '--')),
                "วงเงินกู้ (บาท)": f"฿{r_dict.get('loan_amount', 0):,.0f}" if isinstance(r_dict.get('loan_amount'), (int, float)) else str(r_dict.get('loan_amount', '--')),
                "ประวัติเครดิต (ปี)": r_dict.get('credit_score', '--'),
                "ผลการประเมิน": r_dict.get('result', '--'),
                "โอกาสเสี่ยง AI (%)": f"{r_dict.get('risk_prob', 0):.1f}%" if isinstance(r_dict.get('risk_prob'), (int, float)) else str(r_dict.get('risk_prob', '--')),
                "วันที่ประเมิน": str(r_dict.get('created_at', '--'))
            })
            
    if history_list:
        df_hist = pd.DataFrame(history_list)
        
        # Summary KPI
        total_evals = len(df_hist)
        low_risk_count = sum(df_hist['ผลการประเมิน'] == 'Low Risk')
        pass_rate = (low_risk_count / total_evals) * 100 if total_evals > 0 else 0
        
        h1, h2, h3 = st.columns(3)
        with h1:
            st.markdown(f"""
                <div class="metric-glass-card">
                    <div class="metric-glass-title">จำนวนเคสประเมินทั้งหมด</div>
                    <div class="metric-glass-value">{total_evals} รายการ</div>
                </div>
            """, unsafe_allow_html=True)
        with h2:
            st.markdown(f"""
                <div class="metric-glass-card">
                    <div class="metric-glass-title">ผ่านการอนุมัติ (Low Risk)</div>
                    <div class="metric-glass-value">{low_risk_count} รายการ</div>
                </div>
            """, unsafe_allow_html=True)
        with h3:
            st.markdown(f"""
                <div class="metric-glass-card">
                    <div class="metric-glass-title">อัตราการอนุมัติ (Approval Rate)</div>
                    <div class="metric-glass-value">{pass_rate:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        c_filter1, c_filter2 = st.columns([2, 1])
        with c_filter1:
            search_query = st.text_input("🔍 ค้นหาในประวัติ", placeholder="พิมพ์คำค้น เช่น รายได้ หรือ วันที่...")
        with c_filter2:
            status_filter = st.selectbox("กรองตามสถานะ", ["ทั้งหมด", "Low Risk", "High Risk"])

        df_filtered = df_hist.copy()
        if status_filter != "ทั้งหมด":
            df_filtered = df_filtered[df_filtered['ผลการประเมิน'] == status_filter]
        if search_query:
            df_filtered = df_filtered[df_filtered.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)]

        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
    else:
        st.info("ยังไม่มีประวัติการประเมินสินเชื่อในระบบ สามารถเริ่มทดสอบประเมินได้ที่เมนู 'ประเมินและอนุมัติสินเชื่อ'")
# =========================================================
# PAGE 4: ศูนย์ความรู้ CREDIT RISK
# =========================================================
elif menu == "ศูนย์ความรู้ Credit Risk":
    st.markdown("<h3 style='color: #ffffff; margin-bottom: 24px;'>ศูนย์ความรู้และหลักเกณฑ์การพิจารณาสินเชื่อ (Credit Risk Knowledge Base)</h3>", unsafe_allow_html=True)
    
    col_k1, col_k2 = st.columns(2)
    
    with col_k1:
        st.markdown("""
            <div class="knowledge-card">
                <div class="knowledge-card-tag">UNDERWRITING METRIC 01</div>
                <div class="knowledge-card-title">DTI (Debt-to-Income Ratio)</div>
                <div class="knowledge-card-desc">
                    สัดส่วนภาระหนี้สินผ่อนชำระรวมต่อรายได้ประจำ คำนวณจาก (ภาระหนี้เดิม + ค่างวดใหม่) ÷ รายได้ประจำต่อเดือน
                    ใช้ประเมินความสามารถในการชำระหนี้ของผู้กู้ในชีวิตประจำวัน
                </div>
                <div class="knowledge-card-benchmark">
                    <b>💡 เกณฑ์มาตรฐาน:</b> ปลอดภัย &le; 50% | ความเสี่ยงปานกลาง 50-70% | ปฏิเสธทันที &gt; 70%
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="knowledge-card">
                <div class="knowledge-card-tag">UNDERWRITING METRIC 02</div>
                <div class="knowledge-card-title">LTI (Loan-to-Income Ratio)</div>
                <div class="knowledge-card-desc">
                    สัดส่วนวงเงินสินเชื่อขอกู้ต่อรายได้รวมต่อปี คำนวณจาก วงเงินกู้ ÷ รายได้ประจำต่อปี
                    เป็นมาตรวัดสัดส่วนขนาดหนี้สินเทียบกับศักยภาพการสร้างรายได้ระยะยาว
                </div>
                <div class="knowledge-card-benchmark">
                    <b>💡 เกณฑ์มาตรฐาน:</b> ปกติ &le; 0.5 เท่า | ระวัง 0.5-5.0 เท่า | เพดานสูงสุดไม่เกิน 5.0 เท่า
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_k2:
        st.markdown("""
            <div class="knowledge-card">
                <div class="knowledge-card-tag">AI ENGINE & SCORING</div>
                <div class="knowledge-card-title">Machine Learning Credit Scoring</div>
                <div class="knowledge-card-desc">
                    โมเดล AI วิเคราะห์รูปแบบพฤติกรรมจากประวัติเครดิต รายได้ อายุ และวงเงินกู้ของเคสในอดีต
                    ประมวลผลเป็นเปอร์เซ็นต์โอกาสผิดนัดชำระ (Probability of Default - PD)
                </div>
                <div class="knowledge-card-benchmark">
                    <b>💡 การแปลผล:</b> &lt; 30% ความเสี่ยงต่ำ | 30-60% ความเสี่ยงปานกลาง | &ge; 60% ความเสี่ยงสูงวิกฤต
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="knowledge-card">
                <div class="knowledge-card-tag">UNDERWRITING POLICY</div>
                <div class="knowledge-card-title">Hard Cut-off Overrides</div>
                <div class="knowledge-card-desc">
                    กฎควบคุมความเสี่ยงเด็ดขาด (Hard Policy Rules) ที่ใช้ควบคู่กับ AI Risk Model
                    เพื่อยับยั้งการอนุมัติสินเชื่อกรณีที่ตัวเลขภาระหนี้สินเข้าสู่วิกฤต แม้โมเดล AI จะให้คะแนนผ่านก็ตาม
                </div>
                <div class="knowledge-card-benchmark">
                    <b>💡 เงื่อนไข Hard Rejected:</b> DTI &gt; 70% หรือ LTI &gt; 5.0 เท่า
                </div>
            </div>
        """, unsafe_allow_html=True)