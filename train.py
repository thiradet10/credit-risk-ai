import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# 1. โหลดข้อมูลจริงจากไฟล์ CSV
CSV_FILE_PATH = 'credit_risk_dataset.csv' if os.path.exists('credit_risk_dataset.csv') else 'data.csv'

if not os.path.exists(CSV_FILE_PATH):
    raise FileNotFoundError(f"❌ ไม่พบไฟล์ '{CSV_FILE_PATH}' กรุณาตรวจสอบโฟลเดอร์โปรเจกต์")

print(f"📥 กำลังโหลดข้อมูลจริงจากไฟล์: {CSV_FILE_PATH}")
df = pd.read_csv(CSV_FILE_PATH)

# 2. คัดเลือกเฉพาะคอลัมน์ตัวเลขที่มีอยู่จริงในไฟล์ credit_risk_dataset.csv
FEATURE_COLS = [
    'person_age',                  # อายุ (ปี)
    'person_income',               # รายได้ต่อปี
    'loan_amnt',                   # วงเงินกู้
    'loan_int_rate',               # อัตราดอกเบี้ย (%)
    'cb_person_cred_hist_length'   # ระยะเวลาประวัติเครดิต (ปี)
]
TARGET_COL = 'loan_status'         # 0 = ความเสี่ยงต่ำ (ผ่าน), 1 = ความเสี่ยงสูง (ไม่ผ่าน)

# ตรวจสอบว่ามีคอลัมน์ครบถ้วนใน CSV หรือไม่
missing_cols = [col for col in FEATURE_COLS + [TARGET_COL] if col not in df.columns]
if missing_cols:
    raise KeyError(f"❌ ไม่พบคอลัมน์ {missing_cols} ในไฟล์ CSV")

# 3. เคลียร์ค่าว่าง (Missing Values) ที่มีอยู่ในชุดข้อมูลจริง
data_clean = df[FEATURE_COLS + [TARGET_COL]].dropna().copy()

X = data_clean[FEATURE_COLS]
y = data_clean[TARGET_COL]

print(f"✅ จำนวนข้อมูลจริงที่สมบูรณ์สำหรับฝึก AI: {len(X):,} แถว")

# 4. แบ่งข้อมูลจริงเป็น Train / Test (80 / 20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 5. เทรนโมเดล AI (Random Forest)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 6. วัดประสิทธิภาพจากข้อมูลจริง
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n🎯 ความแม่นยำของโมเดล (Accuracy): {accuracy * 100:.2f}%")
print("\n📊 รายงานผลประเมินโมเดล:")
print(classification_report(y_test, y_pred))

# 7. บันทึกโมเดล
joblib.dump(model, 'model.pkl')
print("\n💾 บันทึกโมเดลลงไฟล์ 'model.pkl' สำเร็จ!")