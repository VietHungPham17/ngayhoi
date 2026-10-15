from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Cấu hình CORS để cho phép frontend từ localhost:5173 gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "ngayhoi.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Tạo bảng với ràng buộc UNIQUE trên ma_sv
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dang_ky (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_sv TEXT NOT NULL UNIQUE,
            ma_phien TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Khởi tạo database khi chạy app
init_db()

class DangKy(BaseModel):
    ma_sv: str
    ma_phien: str

@app.post("/api/dang-ky", status_code=status.HTTP_201_CREATED)
def dang_ky(data: DangKy):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO dang_ky (ma_sv, ma_phien) VALUES (?, ?)", (data.ma_sv, data.ma_phien))
        conn.commit()
        conn.close()
        return {"ok": True}
    except sqlite3.IntegrityError:
        # Nếu ma_sv đã tồn tại thì sqlite3 sẽ quăng lỗi IntegrityError (do UNIQUE constraint)
        raise HTTPException(status_code=409, detail="DA_DANG_KY")
