from tests.conftest import auth_header

async def test_login_success(client, seeded_users):
    response = await client.post(
        "/auth/token",
        data={"username": "test_admin", "password": "pw"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

async def test_login_fails_wrong_passord(client, seeded_users):
    response = await client.post(
        "/auth/token",
        data={"username": "test_admin", "password": "hello"},
    )
    assert response.status_code == 401

#RBAC test for the registration endpoint
async def test_register_requires_admin(client, seeded_users):
    payload = {"username": "new_user", "password": "something", "role": "Field Technician"}

    field_technician_response = await client.post(
        "/auth/register", json=payload, headers=auth_header(seeded_users["technician"])
    )
    assert field_technician_response.status_code == 403

    # assert admin will succeed
    admin_response = await client.post(
        "/auth/register", json=payload, headers=auth_header(seeded_users["admin"])
    )
    assert admin_response.status_code == 201

# test that registration username check is case-insensitive
async def test_register_case_insensitive(client, seeded_users):
    payload={"username": "TeSt_aDMin", "password": "password", "role": "Field Technician"}
    response = await client.post("/auth/register", json=payload, headers=auth_header(seeded_users["admin"]))
    assert response.status_code == 400