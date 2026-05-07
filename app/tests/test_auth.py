"""
Tests for Authentication endpoints
"""


# =========================
# REGISTER TESTS
# =========================

def test_register_success(client):
    """Register a new user successfully"""
    res = client.post("/auth/register", json={
        "name": "John Doe",
        "email": "john@test.com",
        "password": "password123",
        "role": "patient"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "john@test.com"
    assert data["name"] == "John Doe"
    assert data["role"] == "patient"
    assert "id" in data


def test_register_admin(client):
    """Register an admin user"""
    res = client.post("/auth/register", json={
        "name": "Admin",
        "email": "admin@test.com",
        "password": "admin123",
        "role": "admin"
    })
    assert res.status_code == 200
    assert res.json()["role"] == "admin"


def test_register_duplicate_email(client):
    """Cannot register with same email twice"""
    client.post("/auth/register", json={
        "name": "John",
        "email": "john@test.com",
        "password": "password123",
        "role": "patient"
    })
    res = client.post("/auth/register", json={
        "name": "John 2",
        "email": "john@test.com",
        "password": "password456",
        "role": "patient"
    })
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"]


def test_register_missing_fields(client):
    """Register with missing required fields"""
    res = client.post("/auth/register", json={
        "email": "john@test.com"
    })
    assert res.status_code == 422


# =========================
# LOGIN TESTS
# =========================

def test_login_success(client):
    """Login with correct credentials"""
    client.post("/auth/register", json={
        "name": "John",
        "email": "john@test.com",
        "password": "password123",
        "role": "patient"
    })
    res = client.post("/auth/login", data={
        "username": "john@test.com",
        "password": "password123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """Login with wrong password"""
    client.post("/auth/register", json={
        "name": "John",
        "email": "john@test.com",
        "password": "password123",
        "role": "patient"
    })
    res = client.post("/auth/login", data={
        "username": "john@test.com",
        "password": "wrongpassword"
    })
    assert res.status_code == 401


def test_login_wrong_email(client):
    """Login with non-existent email"""
    res = client.post("/auth/login", data={
        "username": "notexist@test.com",
        "password": "password123"
    })
    assert res.status_code == 401


def test_login_returns_valid_token(client):
    """Token returned from login should work on protected routes"""
    client.post("/auth/register", json={
        "name": "John",
        "email": "john@test.com",
        "password": "password123",
        "role": "patient"
    })
    login_res = client.post("/auth/login", data={
        "username": "john@test.com",
        "password": "password123"
    })
    token = login_res.json()["access_token"]

    profile_res = client.get("/profile", headers={
        "Authorization": f"Bearer {token}"
    })
    assert profile_res.status_code == 200
    assert profile_res.json()["user"]["email"] == "john@test.com"


# =========================
# TOKEN VALIDATION TESTS
# =========================

def test_protected_route_without_token(client):
    """Cannot access protected route without token"""
    res = client.get("/profile")
    assert res.status_code == 401


def test_protected_route_with_invalid_token(client):
    """Cannot access protected route with invalid token"""
    res = client.get("/profile", headers={
        "Authorization": "Bearer invalidtoken123"
    })
    assert res.status_code == 401


def test_admin_route_with_user_token(client, user_headers):
    """Patient cannot access admin-only routes"""
    res = client.get("/patients/", headers=user_headers)
    assert res.status_code == 403