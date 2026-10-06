import streamlit as st
import database as db

def render_login():
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 25px 0;">
            <h1 style="color: #1E3A8A; font-weight: 700;">🔑 เข้าสู่ระบบ</h1>
            <p style="color: #6B7280; font-size: 16px;">ยินดีต้อนรับกลับเข้าสู่ระบบประเมินวิเคราะห์สินเชื่อ AI</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 ชื่อผู้ใช้ (Username)", placeholder="กรอกชื่อผู้ใช้")
            password = st.text_input("🔒 รหัสผ่าน (Password)", type="password", placeholder="กรอกรหัสผ่าน")
            
            submit = st.form_submit_button("เข้าสู่ระบบ 🚀", use_container_width=True, type="primary")
            
            if submit:
                if not username or not password:
                    st.error("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")
                else:
                    user, msg = db.login_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_info = user
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")