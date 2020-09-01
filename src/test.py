import json
import os
import tempfile

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# def test_wpastatus(client):
#     wpastatus = client.get("wpastatus")
#     assert b"Failed to get wpa_status" in wpastatus.response


def test_connected_up(client):
    assert client.get("connected").status_code == 200


def test_wlandown(client):
    assert client.get("wlandown").status_code == 200


def test_connected_down(client):
    assert client.get("connected").status_code == 500


def test_wlanup(client):
    assert client.get("wlanup").status_code == 200


test_connected_up(client)
