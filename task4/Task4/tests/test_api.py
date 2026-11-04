import os
import hmac
import hashlib
import json

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


# Test database
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=engine)

client = TestClient(app)

HEADERS = {
    "X-API-Key": "my-secret-api-key"
}


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


# 1. CREATE CUSTOMER
def test_create_customer():
    response = client.post(
        "/customers",
        headers=HEADERS,
        json={
            "name": "John",
            "email": "john@example.com"
        }
    )

    assert response.status_code == 200
    assert response.json()["name"] == "John"


# 2. MISSING API KEY
def test_missing_api_key():
    response = client.get("/customers")

    assert response.status_code == 401


# 3. WRONG API KEY
def test_wrong_api_key():
    response = client.get(
        "/customers",
        headers={"X-API-Key": "wrong"}
    )

    assert response.status_code == 403


# 4. GET CUSTOMER NOT FOUND
def test_customer_not_found():
    response = client.get(
        "/customers/999",
        headers=HEADERS
    )

    assert response.status_code == 404


# 5. DUPLICATE CUSTOMER
def test_duplicate_customer():
    data = {
        "name": "John",
        "email": "john@example.com"
    }

    client.post("/customers", headers=HEADERS, json=data)

    response = client.post(
        "/customers",
        headers=HEADERS,
        json=data
    )

    assert response.status_code == 409


# 6. INVALID CUSTOMER DATA
def test_invalid_customer():
    response = client.post(
        "/customers",
        headers=HEADERS,
        json={
            "name": "John",
            "email": "invalid-email"
        }
    )

    assert response.status_code == 422


# 7. VALID WEBHOOK
def test_valid_webhook():
    payload = {
        "order_id": 101,
        "status": "completed"
    }

    body = json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode()

    signature = hmac.new(
        b"my-webhook-secret",
        body,
        hashlib.sha256
    ).hexdigest()

    response = client.post(
        "/webhooks/order-events",
        json=payload,
        headers={"X-Signature": signature}
    )

    assert response.status_code == 200


# 8. TAMPERED WEBHOOK
def test_tampered_webhook():
    payload = {
        "order_id": 101,
        "status": "completed"
    }

    response = client.post(
        "/webhooks/order-events",
        json=payload,
        headers={"X-Signature": "invalid-signature"}
    )

    assert response.status_code == 401