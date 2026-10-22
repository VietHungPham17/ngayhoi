import os
import sqlite3
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Cấu hình CORS để cho phép frontend từ localhost:5173 gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.getenv("DB_PATH", "ngayhoi.db")
db = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30.0)

def init_db():
    if DB_PATH != ":memory:":
        db.execute("PRAGMA journal_mode=WAL")
    cursor = db.cursor()
    # Tạo bảng với ràng buộc UNIQUE trên (ma_sv, ma_phien)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dang_ky (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_sv TEXT NOT NULL,
            ma_phien TEXT NOT NULL,
            UNIQUE(ma_sv, ma_phien)
        )
    ''')
    db.commit()

# Khởi tạo database khi chạy app
init_db()

class DangKy(BaseModel):
    ma_sv: str
    ma_phien: str

def get_connection():
    if DB_PATH == ":memory:":
        return db
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

SUC_CHUA = 30

@app.post("/api/dang-ky", status_code=status.HTTP_201_CREATED)
def dang_ky(data: DangKy):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # 1. Kiểm tra đã đăng ký phiên này chưa
        cursor.execute("SELECT 1 FROM dang_ky WHERE ma_sv = ? AND ma_phien = ?", (data.ma_sv, data.ma_phien))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="DA_DANG_KY")

        # 2. Gộp đếm và ghi vào duy nhất một câu lệnh SQL
        cursor.execute("""
            INSERT INTO dang_ky (ma_sv, ma_phien)
            SELECT ?, ?
            WHERE (SELECT COUNT(*) FROM dang_ky WHERE ma_phien = ?) < ?
        """, (data.ma_sv, data.ma_phien, data.ma_phien, SUC_CHUA))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=409, detail="HET_CHO")

        return {"ok": True}
    finally:
        if DB_PATH != ":memory:":
            conn.close()

@app.get("/api/con-cho")
def con_cho(ma_phien: str):
    cur = db.execute(
        "SELECT COUNT(*) FROM dang_ky WHERE ma_phien=?", (ma_phien,)
    )
    n = cur.fetchone()[0]
    return {"con_cho": SUC_CHUA - n}
