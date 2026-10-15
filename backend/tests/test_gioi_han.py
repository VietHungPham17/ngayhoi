import os
os.environ["DB_PATH"] = ":memory:"   # CSDL tạm, không đụng dữ liệu thật
import pytest
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)

@pytest.fixture(autouse=True)
def so_trong():
    main.db.execute("DELETE FROM dang_ky"); main.db.commit()

def lap_day(ma_phien, n):
    for i in range(n):
        client.post("/api/dang-ky",
                    json={"ma_sv": f"SV{i:03}", "ma_phien": ma_phien})

def test_p01_trong_dang_ky_thanh_cong():
    r = client.post("/api/dang-ky", json={"ma_sv": "SV001", "ma_phien": "P01"})
    assert r.status_code == 201

def test_p01_co_29_dang_ky_thanh_cong():
    lap_day("P01", 29)
    r = client.post("/api/dang-ky", json={"ma_sv": "SV_MOI", "ma_phien": "P01"})
    assert r.status_code == 201

def test_nguoi_thu_31_bi_tu_choi():
    lap_day("P01", 30)
    r = client.post("/api/dang-ky", json={"ma_sv": "SV_MOI", "ma_phien": "P01"})
    assert r.status_code == 409
    assert r.json().get("detail") == "HET_CHO"

def test_p01_co_30_sv000_dang_ky_lai_bao_da_dang_ky():
    lap_day("P01", 30)
    r = client.post("/api/dang-ky", json={"ma_sv": "SV000", "ma_phien": "P01"})
    assert r.status_code == 409
    assert r.json().get("detail") == "DA_DANG_KY"

def test_p01_co_30_dang_ky_p02_thanh_cong():
    lap_day("P01", 30)
    r = client.post("/api/dang-ky", json={"ma_sv": "SV031", "ma_phien": "P02"})
    assert r.status_code == 201
