import streamlit as st
import pandas as pd
import database as db

def render_predict(model):
    st.markdown("""
        <div style="margin-bottom: 25px;">
            <h1 style="color: #1E3A8A;">📊 ประเมินความเสี่ยงการอนุมัติสินเชื่อ</h1>
            <p style="color: #4B5563;">ป้อนข้อมูลทางการเงินของผู้กู้เพื่อวิเคราะห์ความเสี่ยงด้วยโมเดล Machine Learning</p>
        </div>
    """, unsafe_allow_html=True)
    
    if model is None:
        st.error("❌ ไม่พบไฟล์โมเดล `credit_risk_model.pkl` กรุณารัน `python train.py` ใน Terminal ก่อน")
        return

    # ฟอร์มป้อนข้อมูล
    st.markdown("### 📋 ข้อมูลผู้ขอสินเชื่อ")
    
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("🎂 อายุ (ปี)", min_value=18, max_value=100, value=32, step=1)
        income = st.number_input("💵 รายได้ต่อเดือน (บาท)", min_value=0, value=45000, step=2500)
    with c2:
        loan_amount = st.number_input("🏦 วงเงินกู้ที่ต้องการ (บาท)", min_value=0, value=150000, step=5000)
        credit_score = st.slider("⭐ คะแนนเครดิต (Credit Score)", min_value=300, max_value=850, value=680)

    # คำนวณอัตราส่วนหนี้ต่อรายได้
    dti = (loan_amount / income) if income > 0 else 0
    st.caption(f"💡 อัตราส่วนวงเงินกู้ต่อรายได้ต่อเดือน: **{dti:.2f} เท่า**")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔮 เริ่มวิเคราะห์ความเสี่ยงด้วย AI", type="primary", use_container_width=True):
        input_df = pd.DataFrame([[age, income, loan_amount, credit_score]],
                                columns=['age', 'income', 'loan_amount', 'credit_score'])
        
        prediction = model.predict(input_df)[0]
        prob = model.predict_proba(input_df)[0][1] * 100
        result_str = "มีความเสี่ยงสูง (High Risk)" if prediction == 1 else "ความเสี่ยงต่ำ (Low Risk)"

        st.markdown("---")
        st.markdown("### 📌 ผลการวิเคราะห์จากระบบ AI")
        
        r1, r2 = st.columns([1.2, 1])
        
        with r1:
            if prediction == 1:
                st.markdown("""
                    <div style="background-color: #FEE2E2; border-left: 6px solid #EF4444; padding: 20px; border-radius: 8px;">
                        <h3 style="color: #991B1B; margin: 0;">⚠️ ผลลัพธ์: มีความเสี่ยงสูง (High Risk)</h3>
                        <p style="color: #7F1D1D; margin-top: 8px;">
                            คำแนะนำ: ผู้กู้มีโอกาสผิดนัดชำระหนี้สูง ควรพิจารณาปรับลดวงเงิน ขอหลักประกันเพิ่มเติม หรือปฏิเสธการอนุมัติ
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="background-color: #D1FAE5; border-left: 6px solid #10B981; padding: 20px; border-radius: 8px;">
                        <h3 style="color: #065F46; margin: 0;">✅ ผลลัพธ์: ความเสี่ยงต่ำ (Low Risk)</h3>
                        <p style="color: #064E3B; margin-top: 8px;">
                            คำแนะนำ: ผู้กู้มีความน่าเชื่อถือทางการเงินสูง ผ่านเกณฑ์ประเมินเบื้องต้น สามารถพิจารณาอนุมัติสินเชื่อได้
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
        with r2:
            st.metric(label="โอกาสความเสี่ยงสูง (Risk Probability)", value=f"{prob:.1f}%")
            st.progress(int(prob))
            
        # บันทึกเข้าฐานข้อมูล SQLite
        db.save_prediction(
            user_id=st.session_state.user_info['id'],
            age=age,
            income=income,
            loan_amount=loan_amount,
            credit_score=credit_score,
            risk_result=result_str,
            risk_probability=prob
        )
        st.toast("บันทึกประวัติผลประเมินเรียบร้อยแล้ว!", icon="💾")