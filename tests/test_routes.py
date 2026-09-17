from fastapi.testclient import TestClient

import models
from auth import get_current_user
from database import get_db
from main import app


client = TestClient(app)


def override_get_db():
    """
    Provide a mocked database dependency for functional tests.
    """
    yield None


def override_get_current_user():
    """
    Provide an authenticated test user.
    """
    return models.User(
        id=1,
        email="test@example.com",
        hashed_password="test_password"
    )


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_contacts(monkeypatch):
    """
    Test the GET /contacts route.
    """

    test_contacts = [
        models.Contact(
            id=1,
            user_id=1,
            name="Max",
            last_name="Test",
            email="max@example.com",
            phone="123456789"
        )
    ]

    def mock_get_contacts(db, user_id):
        return test_contacts

    monkeypatch.setattr(
        "main.repository_contacts.get_contacts",
        mock_get_contacts
    )

    response = client.get("/contacts")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Max"
    assert data[0]["last_name"] == "Test"
    assert data[0]["email"] == "max@example.com"