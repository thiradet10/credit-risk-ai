import streamlit as st
import pandas as pd

def render_history():
    st.markdown("<h2 style='color: #ffffff; font-weight: 800; margin-bottom: 4px;'>📜 ประวัติการประเมินสินเชื่อของคุณ</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #38bdf8; font-size: 14px; margin-bottom: 24px;'>รายการประวัติย้อนหลังและการวิเคราะห์ภาพรวมการประเมินในระบบ</p>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 1. ดึงข้อมูลประวัติจาก Database หรือ Session
    # ---------------------------------------------------------
    rows = []
    try:
        import database as db
        if hasattr(db, 'get_user_history'):
            user_id = st.session_state.get('user_info', {}).get('id', 1)
            rows = db.get_user_history(user_id)
    except Exception:
        pass

    # หากไม่มีข้อมูลใน DB ให้ใช้ชุดตัวอย่างสำหรับแสดงผล
    if not rows:
        # ข้อมูลตัวอย่างสำหรับพรีวิว
        data_list = [
            {"age": 25, "income": 420000, "loan_amount": 150000, "credit_score": 3, "result": "Low Risk", "risk_prob": 10.0, "created_at": "2026-10-05 02:42:40"},
            {"age": 30, "income": 600000, "loan_amount": 1000000, "credit_score": 3, "result": "Low Risk", "risk_prob": 28.0, "created_at": "2026-10-05 02:38:06"},
            {"age": 45, "income": 300000, "loan_amount": 800000, "credit_score": 1, "result": "High Risk", "risk_prob": 82.5, "created_at": "2026-10-04 18:15:20"},
            {"age": 28, "income": 500000, "loan_amount": 200000, "credit_score": 4, "result": "Low Risk", "risk_prob": 12.3, "created_at": "2026-10-04 15:10:12"},
        ]
        total_evals = 40
        low_risk_cnt = 30
        high_risk_cnt = 10
    else:
        df_raw = pd.DataFrame(rows, columns=["age", "income", "loan_amount", "credit_score", "result", "risk_prob", "created_at"])
        total_evals = len(df_raw)
        low_risk_cnt = len(df_raw[df_raw['result'] == 'Low Risk'])
        high_risk_cnt = total_evals - low_risk_cnt
        data_list = df_raw.to_dict('records')

    low_pct = (low_risk_cnt / total_evals * 100) if total_evals > 0 else 0
    high_pct = (high_risk_cnt / total_evals * 100) if total_evals > 0 else 0

    # ---------------------------------------------------------
    # 2. ULTRA-MODERN GLASS KPI CARDS
    # ---------------------------------------------------------
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
            <div class="metric-glass-card">
                <div class="metric-glass-title">📊 จำนวนการประเมินทั้งหมด</div>
                <div class="metric-glass-value">{total_evals} ครั้ง</div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="metric-glass-card" style="border-color: rgba(34, 197, 94, 0.45);">
                <div class="metric-glass-title" style="color: #4ade80 !important;">✅ ผ่านเกณฑ์ (Low Risk)</div>
                <div class="metric-glass-value" style="color: #4ade80 !important;">{low_risk_cnt} ครั้ง <span style="font-size: 15px; color: #a7f3d0; font-weight: 600;">({low_pct:.0f}%)</span></div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div class="metric-glass-card" style="border-color: rgba(239, 68, 68, 0.45);">
                <div class="metric-glass-title" style="color: #f87171 !important;">❌ เสี่ยงสูง (High Risk)</div>
                <div class="metric-glass-value" style="color: #f87171 !important;">{high_risk_cnt} ครั้ง <span style="font-size: 15px; color: #fca5a5; font-weight: 600;">({high_pct:.0f}%)</span></div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 3. SLEEK GLASS DATAFRAME TABLE
    # ---------------------------------------------------------
    st.markdown("<h4 style='color: #ffffff; font-weight: 700; margin-bottom: 14px;'>📄 ตารางรายการประเมินย้อนหลัง</h4>", unsafe_allow_html=True)

    df_display = pd.DataFrame(data_list)
    
    # เปลี่ยนชื่อคอลัมน์และจัดรูปแบบการแสดงผล
    df_display = df_display.rename(columns={
        "age": "อายุ (ปี)",
        "income": "รายได้ประจำ/ปี (บาท)",
        "loan_amount": "วงเงินกู้ (บาท)",
        "credit_score": "ประวัติเครดิต (ปี)",
        "result": "ผลการประเมิน",
        "risk_prob": "โอกาสเสี่ยง AI (%)",
        "created_at": "วันที่-เวลาประเมิน"
    })

    # ฟอร์แมตตัวเลขการเงิน
    df_display["รายได้ประจำ/ปี (บาท)"] = df_display["รายได้ประจำ/ปี (บาท)"].apply(lambda x: f"฿{x:,.0f}")
    df_display["วงเงินกู้ (บาท)"] = df_display["วงเงินกู้ (บาท)"].apply(lambda x: f"฿{x:,.0f}")
    df_display["โอกาสเสี่ยง AI (%)"] = df_display["โอกาสเสี่ยง AI (%)"].apply(lambda x: f"{x:.1f}%")

    st.dataframe(df_display, use_container_width=True, hide_index=True)