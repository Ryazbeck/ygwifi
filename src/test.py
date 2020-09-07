import json
import requests
import os
import tempfile

import pytest


WIFI_SSID = os.getenv("WIFI_SSID", None)
WIFI_KEY = os.getenv("WIFI_KEY", None)


def test_ap():
    apup = requests.get("http://localhost:5000/apup")
    assert json.loads(apup.text)["response"] == "ap0 enabled"

    apdown = requests.get("http://localhost:5000/apdown")
    assert json.loads(apdown.text)["response"] == "ap0 disabled"


def test_wlan():
    # connected should fail
    connected = requests.get("http://localhost:5000/connected")
    assert json.loads(connected.text)["response"] == "Failure"

    # enable wpa and confirm scan workls
    wpa_status_down = requests.get("http://localhost:5000/wpastatus")
    assert json.loads(wpa_status_down.text)["response"]["wpa_state"] == "DISCONNECTED"

    scan = requests.get("http://localhost:5000/scan")
    assert isinstance(json.loads(scan.text)["response"], list)

    connect = requests.get(
        "http://localhost:5000/connect", params={"ssid": WIFI_SSID, "key": WIFI_KEY}
    )
    assert json.loads(connect.text)["response"] == "Success"

    wpa_status_up = requests.get("http://localhost:5000/wpastatus")
    assert json.loads(wpa_status_up.text)["response"]["wpa_state"] == "COMPLETED"

    connected = requests.get("http://localhost:5000/connected")
    assert json.loads(connected.text)["response"] == "Success"

