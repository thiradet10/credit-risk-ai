import streamlit as st
import database as db

def render_register():
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 25px 0;">
            <h1 style="color: #1E3A8A; font-weight: 700;">📝 สมัครสมาชิกใหม่</h1>
            <p style="color: #6B7280; font-size: 16px;">สร้างบัญชีผู้ใช้เพื่อเริ่มต้นใช้งานระบบประเมินสินเชื่อ</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("register_form"):
            username = st.text_input("👤 ชื่อผู้ใช้ (Username)", placeholder="เช่น john_doe")
            email = st.text_input("📧 อีเมล (Email)", placeholder="เช่น example@email.com")
            password = st.text_input("🔒 รหัสผ่าน (Password)", type="password", placeholder="อย่างน้อย 6 ตัวอักษร")
            confirm_password = st.text_input("🔒 ยืนยันรหัสผ่าน", type="password", placeholder="กรอกรหัสผ่านอีกครั้ง")
            
            submit = st.form_submit_button("ลงทะเบียนใช้งาน ✍️", use_container_width=True, type="primary")
            
            if submit:
                if not username or not email or not password:
                    st.error("⚠️ กรุณากรอกข้อมูลให้ครบทุกช่อง")
                elif password != confirm_password:
                    st.error("⚠️ รหัสผ่านทั้งสองช่องไม่ตรงกัน")
                elif len(password) < 6:
                    st.warning("⚠️ รหัสผ่านต้องมีความยาวอย่างน้อย 6 ตัวอักษร")
                else:
                    success, msg = db.register_user(username, email, password)
                    if success:
                        st.success(f"🎉 {msg}")
                    else:
                        st.error(f"❌ {msg}")