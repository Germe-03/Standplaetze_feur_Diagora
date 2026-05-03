from datetime import date, timedelta

from fastapi.testclient import TestClient

from UI.server import create_app


def test_booking_flow_end_to_end() -> None:
    app = create_app("sqlite+pysqlite:///:memory:")
    client = TestClient(app)

    user_resp = client.post(
        "/api/users",
        json={"name": "Luca Beispiel", "email": "luca@example.com", "phone": "+41 79 123 45 67"},
    )
    assert user_resp.status_code == 201
    user_id = user_resp.json()["id"]

    location_resp = client.post(
        "/api/locations",
        json={"name": "Marktplatz", "city": "Basel", "price": 95.0},
    )
    assert location_resp.status_code == 201
    location_id = location_resp.json()["id"]

    campaign_resp = client.post(
        "/api/campaigns",
        json={"name": "Sommer", "year": date.today().year, "budget": 900.0, "owner_id": user_id},
    )
    assert campaign_resp.status_code == 201
    campaign_id = campaign_resp.json()["id"]

    booking_resp = client.post(
        "/api/bookings",
        json={
            "event_date": (date.today() + timedelta(days=5)).isoformat(),
            "price": 95.0,
            "status": "open",
            "location_id": location_id,
            "campaign_id": campaign_id,
            "user_id": user_id,
        },
    )
    assert booking_resp.status_code == 201

    list_resp = client.get("/api/bookings")
    assert list_resp.status_code == 200
    payload = list_resp.json()
    assert len(payload) == 1
