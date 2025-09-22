from pathlib import Path

from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)
FIXTURE_PDF = Path(__file__).parent / "samples" / "waterfalls_quick_guide.pdf"


def test_health_ping():
    print('PING')
    r = client.get("/ping")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") in {"ok", "healthy", "alive"} or data.get("message"), "Unexpected ping payload"
