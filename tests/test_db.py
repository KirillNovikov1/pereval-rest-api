from __future__ import annotations


def test_database_add_and_get_pereval(database, valid_payload):
    pereval_id, error = database.add_pereval(valid_payload)

    assert error is None
    assert isinstance(pereval_id, int)

    pereval = database.get_pereval(pereval_id)
    assert pereval is not None
    assert pereval["title"] == valid_payload["title"]
    assert pereval["status"] == "new"
    assert pereval["user"]["email"] == valid_payload["user"]["email"]
    assert len(pereval["images"]) == 1


def test_database_get_perevals_by_email(database, valid_payload):
    first_id, _ = database.add_pereval(valid_payload)

    second_payload = valid_payload.copy()
    second_payload["title"] = "Второй перевал"
    second_id, _ = database.add_pereval(second_payload)

    result = database.get_perevals_by_email(valid_payload["user"]["email"])

    assert len(result) == 2
    ids = [item["id"] for item in result]
    assert first_id in ids
    assert second_id in ids


def test_database_update_pereval_success(database, valid_payload):
    pereval_id, _ = database.add_pereval(valid_payload)

    patch_payload = {
        "title": "Обновлённый перевал",
        "coords": {"height": 1400},
        "level": {"summer": "1Б"},
        "user": valid_payload["user"],
        "images": [],
    }

    success, message = database.update_pereval(pereval_id, patch_payload)
    updated = database.get_pereval(pereval_id)

    assert success is True
    assert message == "The record was updated successfully"
    assert updated["title"] == "Обновлённый перевал"
    assert updated["coords"]["height"] == 1400
    assert updated["level"]["summer"] == "1Б"
    assert updated["images"] == []


def test_database_update_forbidden_when_user_changed(database, valid_payload):
    pereval_id, _ = database.add_pereval(valid_payload)

    patch_payload = {
        "title": "Обновлённый перевал",
        "user": {
            **valid_payload["user"],
            "phone": "+70000000000",
        },
    }

    success, message = database.update_pereval(pereval_id, patch_payload)

    assert success is False
    assert "Protected user field cannot be changed" in message


def test_database_update_forbidden_when_status_is_not_new(database, valid_payload):
    pereval_id, _ = database.add_pereval(valid_payload)
    database.set_status(pereval_id, "pending")

    success, message = database.update_pereval(pereval_id, {"title": "Нельзя обновить"})

    assert success is False
    assert "status 'new'" in message
