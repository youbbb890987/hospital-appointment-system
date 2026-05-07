"""
Tests for Doctors endpoints
"""


# =========================
# CREATE DOCTOR TESTS
# =========================

def test_create_doctor_as_admin(client, admin_headers):
    """Admin can create a doctor"""
    res = client.post("/doctors/", json={
        "name": "Dr. Ahmed",
        "specialization": "Cardiology",
        "email": "ahmed@hospital.com",
        "phone": "01012345678"
    }, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Dr. Ahmed"
    assert data["specialization"] == "Cardiology"
    assert "id" in data


def test_create_doctor_as_user(client, user_headers):
    """User cannot create a doctor"""
    res = client.post("/doctors/", json={
        "name": "Dr. Ahmed",
        "specialization": "Cardiology",
        "email": "ahmed@hospital.com",
        "phone": "01012345678"
    }, headers=user_headers)
    assert res.status_code == 403


def test_create_doctor_without_token(client):
    """Cannot create doctor without token"""
    res = client.post("/doctors/", json={
        "name": "Dr. Ahmed",
        "specialization": "Cardiology",
        "email": "ahmed@hospital.com",
        "phone": "01012345678"
    })
    assert res.status_code == 401


def test_create_doctor_duplicate_email(client, admin_headers):
    """Cannot create two doctors with same email"""
    client.post("/doctors/", json={
        "name": "Dr. Ahmed",
        "specialization": "Cardiology",
        "email": "ahmed@hospital.com",
        "phone": "01012345678"
    }, headers=admin_headers)
    res = client.post("/doctors/", json={
        "name": "Dr. Ali",
        "specialization": "Neurology",
        "email": "ahmed@hospital.com",
        "phone": "01087654321"
    }, headers=admin_headers)
    assert res.status_code == 400


# =========================
# GET DOCTORS TESTS
# =========================

def test_get_all_doctors(client, admin_headers):
    """Get all doctors - open endpoint"""
    client.post("/doctors/", json={
        "name": "Dr. Ahmed",
        "specialization": "Cardiology",
        "email": "ahmed@hospital.com",
        "phone": "01012345678"
    }, headers=admin_headers)
    res = client.get("/doctors/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) == 1


def test_get_doctor_by_id(client, admin_headers):
    """Get a specific doctor by ID"""
    create_res = client.post("/doctors/", json={
        "name": "Dr. Ahmed",
        "specialization": "Cardiology",
        "email": "ahmed@hospital.com",
        "phone": "01012345678"
    }, headers=admin_headers)
    doctor_id = create_res.json()["id"]

    res = client.get(f"/doctors/{doctor_id}")
    assert res.status_code == 200
    assert res.json()["id"] == doctor_id


def test_get_doctor_not_found(client):
    """Get non-existent doctor"""
    res = client.get("/doctors/9999")
    assert res.status_code == 404


# =========================
# UPDATE DOCTOR TESTS
# =========================

def test_update_doctor_as_admin(client, admin_headers):
    """Admin can update a doctor"""
    create_res = client.post("/doctors/", json={
        "name": "Dr. Ahmed",
        "specialization": "Cardiology",
        "email": "ahmed@hospital.com",
        "phone": "01012345678"
    }, headers=admin_headers)
    doctor_id = create_res.json()["id"]

    res = client.put(f"/doctors/{doctor_id}", json={
        "name": "Dr. Ahmed Updated",
        "specialization": "Neurology",
        "email": "ahmed@hospital.com",
        "phone": "01012345678"
    }, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Dr. Ahmed Updated"
    assert res.json()["specialization"] == "Neurology"


def test_update_doctor_as_user(client, admin_headers, user_headers):
    """User cannot update a doctor"""
    create_res = client.post("/doctors/", json={
        "name": "Dr. Ahmed",
        "specialization": "Cardiology",
        "email": "ahmed@hospital.com",
        "phone": "01012345678"
    }, headers=admin_headers)
    doctor_id = create_res.json()["id"]

    res = client.put(f"/doctors/{doctor_id}", json={
        "name": "Dr. Ahmed Updated",
        "specialization": "Neurology",
        "email": "ahmed@hospital.com",
        "phone": "01012345678"
    }, headers=user_headers)
    assert res.status_code == 403


# =========================
# DELETE DOCTOR TESTS
# =========================

def test_delete_doctor_as_admin(client, admin_headers):
    """Admin can delete a doctor"""
    create_res = client.post("/doctors/", json={
        "name": "Dr. Ahmed",
        "specialization": "Cardiology",
        "email": "ahmed@hospital.com",
        "phone": "01012345678"
    }, headers=admin_headers)
    doctor_id = create_res.json()["id"]

    res = client.delete(f"/doctors/{doctor_id}", headers=admin_headers)
    assert res.status_code == 200

    get_res = client.get(f"/doctors/{doctor_id}")
    assert get_res.status_code == 404


def test_delete_doctor_as_user(client, admin_headers, user_headers):
    """User cannot delete a doctor"""
    create_res = client.post("/doctors/", json={
        "name": "Dr. Ahmed",
        "specialization": "Cardiology",
        "email": "ahmed@hospital.com",
        "phone": "01012345678"
    }, headers=admin_headers)
    doctor_id = create_res.json()["id"]

    res = client.delete(f"/doctors/{doctor_id}", headers=user_headers)
    assert res.status_code == 403
