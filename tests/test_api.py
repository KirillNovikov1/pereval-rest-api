from __future__ import annotations


def test_post_and_get_submit_data(client, valid_payload):
    response = client.post("/submitData", json=valid_payload)

    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data["status"] == 200
    assert "id" in response_data

    pereval_id = response_data["id"]
    get_response = client.get(f"/submitData/{pereval_id}")
    assert get_response.status_code == 200

    get_data = get_response.get_json()
    assert get_data["title"] == valid_payload["title"]
    assert get_data["status"] == "new"
    assert get_data["user"]["email"] == valid_payload["user"]["email"]


def test_get_submit_data_by_email(client, valid_payload):
    client.post("/submitData", json=valid_payload)

    response = client.get(f"/submitData?user__email={valid_payload['user']['email']}")

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["user"]["email"] == valid_payload["user"]["email"]


def test_patch_submit_data_success(client, valid_payload):
    create_response = client.post("/submitData", json=valid_payload)
    pereval_id = create_response.get_json()["id"]

    patch_payload = {
        "title": "Updated API title",
        "coords": {"height": 2222},
        "level": {"summer": "2А"},
        "user": valid_payload["user"],
        "images": [],
    }

    patch_response = client.patch(f"/submitData/{pereval_id}", json=patch_payload)
    patch_data = patch_response.get_json()

    assert patch_response.status_code == 200
    assert patch_data["state"] == 1

    get_response = client.get(f"/submitData/{pereval_id}")
    get_data = get_response.get_json()
    assert get_data["title"] == "Updated API title"
    assert get_data["coords"]["height"] == 2222
    assert get_data["images"] == []


def test_patch_submit_data_forbidden_when_user_changed(client, valid_payload):
    create_response = client.post("/submitData", json=valid_payload)
    pereval_id = create_response.get_json()["id"]

    patch_payload = {
        "user": {
            **valid_payload["user"],
            "email": "changed@example.com",
        }
    }

    patch_response = client.patch(f"/submitData/{pereval_id}", json=patch_payload)
    patch_data = patch_response.get_json()

    assert patch_response.status_code == 200
    assert patch_data["state"] == 0
    assert "Protected user field cannot be changed" in patch_data["message"]


def test_patch_submit_data_forbidden_when_status_is_not_new(client, database, valid_payload):
    create_response = client.post("/submitData", json=valid_payload)
    pereval_id = create_response.get_json()["id"]
    database.set_status(pereval_id, "pending")

    patch_response = client.patch(f"/submitData/{pereval_id}", json={"title": "Should fail"})
    patch_data = patch_response.get_json()

    assert patch_response.status_code == 200
    assert patch_data["state"] == 0
    assert "status 'new'" in patch_data["message"]


def test_get_nonexistent_pereval_returns_404(client):
    response = client.get("/submitData/99999")

    assert response.status_code == 404
    assert response.get_json()["message"] == "Pereval not found"
