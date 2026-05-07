"""
Tests for Patients endpoints
"""


def create_patient_data(suffix=""):
    return {
        "name": f"Ahmed Mohamed{suffix}",
        "age": 30,
        "gender": "Male",
        "phone": "01012345678",
        "email": f"ahmed{suffix}@email.com"
    }


# =========================
# CREATE PATIENT TESTS
# =========================

def test_create_patient_as_user(client, user_headers):
    """User can create a patient"""
    res = client.post("/patients/", json=create_patient_data(), headers=user_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Ahmed Mohamed"
    assert data["age"] == 30


def test_create_patient_as_admin(client, admin_headers):
    """Admin can create a patient"""
    res = client.post("/patients/", json=create_patient_data(), headers=admin_headers)
    assert res.status_code == 200


def test_create_patient_without_token(client):
    """Cannot create patient without token"""
    res = client.post("/patients/", json=create_patient_data())
    assert res.status_code == 401


def test_create_patient_missing_fields(client, user_headers):
    """Cannot create patient with missing required fields"""
    res = client.post("/patients/", json={"name": "Ahmed"}, headers=user_headers)
    assert res.status_code == 422


# =========================
# GET PATIENTS TESTS
# =========================

def test_get_all_patients_as_admin(client, admin_headers, user_headers):
    """Admin can get all patients"""
    client.post("/patients/", json=create_patient_data("1"), headers=user_headers)
    client.post("/patients/", json=create_patient_data("2"), headers=admin_headers)

    res = client.get("/patients/", headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_get_all_patients_as_user(client, user_headers):
    """User cannot get all patients"""
    res = client.get("/patients/", headers=user_headers)
    assert res.status_code == 403


def test_get_my_patients(client, user_headers, admin_headers):
    """User can only see their own patients"""
    client.post("/patients/", json=create_patient_data("1"), headers=user_headers)
    client.post("/patients/", json=create_patient_data("2"), headers=admin_headers)

    res = client.get("/patients/my", headers=user_headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_patient_by_id_as_admin(client, admin_headers):
    """Admin can get any patient by ID"""
    create_res = client.post("/patients/", json=create_patient_data(), headers=admin_headers)
    patient_id = create_res.json()["id"]

    res = client.get(f"/patients/{patient_id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["id"] == patient_id


def test_get_patient_by_id_as_owner(client, user_headers):
    """User can get their own patient by ID"""
    create_res = client.post("/patients/", json=create_patient_data(), headers=user_headers)
    patient_id = create_res.json()["id"]

    res = client.get(f"/patients/{patient_id}", headers=user_headers)
    assert res.status_code == 200


def test_get_patient_not_owned(client, user_headers, admin_headers):
    """User cannot get another user's patient"""
    create_res = client.post("/patients/", json=create_patient_data(), headers=admin_headers)
    patient_id = create_res.json()["id"]

    res = client.get(f"/patients/{patient_id}", headers=user_headers)
    assert res.status_code == 403


def test_get_patient_not_found(client, admin_headers):
    """Get non-existent patient"""
    res = client.get("/patients/9999", headers=admin_headers)
    assert res.status_code == 404


# =========================
# UPDATE PATIENT TESTS
# =========================

def test_update_patient_as_owner(client, user_headers):
    """User can update their own patient"""
    create_res = client.post("/patients/", json=create_patient_data(), headers=user_headers)
    patient_id = create_res.json()["id"]

    res = client.put(f"/patients/{patient_id}", json={
        "name": "Ahmed Updated",
        "age": 35,
        "gender": "Male",
        "phone": "01012345678",
        "email": "ahmed@email.com"
    }, headers=user_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Ahmed Updated"
    assert res.json()["age"] == 35


def test_update_patient_not_owned(client, user_headers, admin_headers):
    """User cannot update another user's patient"""
    create_res = client.post("/patients/", json=create_patient_data(), headers=admin_headers)
    patient_id = create_res.json()["id"]

    res = client.put(f"/patients/{patient_id}", json={
        "name": "Hacked",
        "age": 25,
        "gender": "Male",
        "phone": "01012345678",
        "email": "hacked@email.com"
    }, headers=user_headers)
    assert res.status_code == 403


# =========================
# DELETE PATIENT TESTS
# =========================

def test_delete_patient_as_owner(client, user_headers):
    """User can delete their own patient"""
    create_res = client.post("/patients/", json=create_patient_data(), headers=user_headers)
    patient_id = create_res.json()["id"]

    res = client.delete(f"/patients/{patient_id}", headers=user_headers)
    assert res.status_code == 200


def test_delete_patient_as_admin(client, user_headers, admin_headers):
    """Admin can delete any patient"""
    create_res = client.post("/patients/", json=create_patient_data(), headers=user_headers)
    patient_id = create_res.json()["id"]

    res = client.delete(f"/patients/{patient_id}", headers=admin_headers)
    assert res.status_code == 200


def test_delete_patient_not_owned(client, user_headers, admin_headers):
    """User cannot delete another user's patient"""
    create_res = client.post("/patients/", json=create_patient_data(), headers=admin_headers)
    patient_id = create_res.json()["id"]

    res = client.delete(f"/patients/{patient_id}", headers=user_headers)
    assert res.status_code == 403
