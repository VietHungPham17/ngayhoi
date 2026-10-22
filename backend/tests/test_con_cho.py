import os
os.environ["DB_PATH"] = ":memory:"
import pytest
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)

@pytest.fixture(autouse=True)
def so_trong():
    main.db.execute("DELETE FROM dang_ky"); main.db.commit()

def test_con_cho_khi_chua_dang_ky():
    r = client.get("/api/con-cho?ma_phien=P01")
    assert r.status_code == 200
    assert r.json() == {"con_cho": 30}

def test_con_cho_khi_co_dang_ky():
    client.post("/api/dang-ky", json={"ma_sv": "SV001", "ma_phien": "P01"})
    r = client.get("/api/con-cho?ma_phien=P01")
    assert r.json() == {"con_cho": 29}
