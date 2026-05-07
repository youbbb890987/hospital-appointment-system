"""
Tests for Appointments endpoints
"""


def create_doctor(client, headers):
    res = client.post("/doctors/", json={
        "name": "Dr. Ahmed",
        "specialization": "Cardiology",
        "email": "ahmed@hospital.com",
        "phone": "01012345678"
    }, headers=headers)
    return res.json()["id"]


# =========================
# CREATE APPOINTMENT TESTS
# =========================

def test_create_appointment_as_user(client, admin_headers, user_headers):
    """User can book an appointment"""
    doctor_id = create_doctor(client, admin_headers)
    res = client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:00"
    }, headers=user_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["doctor_id"] == doctor_id
    assert data["status"] == "Scheduled"


def test_create_appointment_without_token(client, admin_headers):
    """Cannot book appointment without token"""
    doctor_id = create_doctor(client, admin_headers)
    res = client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:00"
    })
    assert res.status_code == 401


def test_create_appointment_doctor_not_found(client, user_headers):
    """Cannot book appointment with non-existent doctor"""
    res = client.post("/appointments/", json={
        "doctor_id": 9999,
        "appointment_date": "2026-12-01T10:00"
    }, headers=user_headers)
    assert res.status_code == 404


def test_prevent_double_booking_same_time(client, admin_headers, user_headers):
    """Cannot book same doctor at same time"""
    doctor_id = create_doctor(client, admin_headers)
    client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:00"
    }, headers=user_headers)

    res = client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:00"
    }, headers=admin_headers)
    assert res.status_code == 400
    assert "already booked" in res.json()["detail"]


def test_prevent_booking_within_one_hour(client, admin_headers, user_headers):
    """Cannot book same doctor within 1 hour of existing appointment"""
    doctor_id = create_doctor(client, admin_headers)
    client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:00"
    }, headers=user_headers)

    res = client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:30"
    }, headers=admin_headers)
    assert res.status_code == 400


def test_allow_booking_after_one_hour(client, admin_headers, user_headers):
    """Can book same doctor after 1 hour gap"""
    doctor_id = create_doctor(client, admin_headers)
    client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:00"
    }, headers=user_headers)

    res = client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T11:01"
    }, headers=admin_headers)
    assert res.status_code == 200


# =========================
# GET APPOINTMENTS TESTS
# =========================

def test_get_my_appointments(client, admin_headers, user_headers):
    """User can get only their own appointments"""
    doctor_id = create_doctor(client, admin_headers)
    client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:00"
    }, headers=user_headers)
    client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T12:00"
    }, headers=admin_headers)

    res = client.get("/appointments/my", headers=user_headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_all_appointments_as_admin(client, admin_headers, user_headers):
    """Admin can get all appointments"""
    doctor_id = create_doctor(client, admin_headers)
    client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:00"
    }, headers=user_headers)
    client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T12:00"
    }, headers=admin_headers)

    res = client.get("/appointments/", headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_get_all_appointments_as_user(client, user_headers):
    """User cannot get all appointments"""
    res = client.get("/appointments/", headers=user_headers)
    assert res.status_code == 403


def test_get_appointment_by_id_as_owner(client, admin_headers, user_headers):
    """User can get their own appointment by ID"""
    doctor_id = create_doctor(client, admin_headers)
    create_res = client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:00"
    }, headers=user_headers)
    appt_id = create_res.json()["id"]

    res = client.get(f"/appointments/{appt_id}", headers=user_headers)
    assert res.status_code == 200


def test_get_appointment_by_id_not_owned(client, admin_headers, user_headers):
    """User cannot get another user's appointment"""
    doctor_id = create_doctor(client, admin_headers)
    create_res = client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:00"
    }, headers=admin_headers)
    appt_id = create_res.json()["id"]

    res = client.get(f"/appointments/{appt_id}", headers=user_headers)
    assert res.status_code == 403


# =========================
# UPDATE APPOINTMENT TESTS
# =========================

def test_update_appointment_as_owner(client, admin_headers, user_headers):
    """User can update their own appointment"""
    doctor_id = create_doctor(client, admin_headers)
    create_res = client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:00"
    }, headers=user_headers)
    appt_id = create_res.json()["id"]

    res = client.put(f"/appointments/{appt_id}", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-05T14:00"
    }, headers=user_headers)
    assert res.status_code == 200
    assert "2026-12-05" in res.json()["appointment_date"]


def test_update_appointment_not_owned(client, admin_headers, user_headers):
    """User cannot update another user's appointment"""
    doctor_id = create_doctor(client, admin_headers)
    create_res = client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:00"
    }, headers=admin_headers)
    appt_id = create_res.json()["id"]

    res = client.put(f"/appointments/{appt_id}", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-05T14:00"
    }, headers=user_headers)
    assert res.status_code == 403


# =========================
# DELETE APPOINTMENT TESTS
# =========================

def test_delete_appointment_as_owner(client, admin_headers, user_headers):
    """User can delete their own appointment"""
    doctor_id = create_doctor(client, admin_headers)
    create_res = client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:00"
    }, headers=user_headers)
    appt_id = create_res.json()["id"]

    res = client.delete(f"/appointments/{appt_id}", headers=user_headers)
    assert res.status_code == 200


def test_delete_appointment_as_admin(client, admin_headers, user_headers):
    """Admin can delete any appointment"""
    doctor_id = create_doctor(client, admin_headers)
    create_res = client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:00"
    }, headers=user_headers)
    appt_id = create_res.json()["id"]

    res = client.delete(f"/appointments/{appt_id}", headers=admin_headers)
    assert res.status_code == 200


def test_delete_appointment_not_owned(client, admin_headers, user_headers):
    """User cannot delete another user's appointment"""
    doctor_id = create_doctor(client, admin_headers)
    create_res = client.post("/appointments/", json={
        "doctor_id": doctor_id,
        "appointment_date": "2026-12-01T10:00"
    }, headers=admin_headers)
    appt_id = create_res.json()["id"]

    res = client.delete(f"/appointments/{appt_id}", headers=user_headers)
    assert res.status_code == 403