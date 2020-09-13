import json
import requests
import os
import tempfile

import pytest


WIFI_SSID = os.getenv("WIFI_SSID", None)
WIFI_KEY = os.getenv("WIFI_KEY", None)


def test_ap():
    apup = requests.get("http://localhost:5000/apup")
    assert apup.status_code == 200

    apdown = requests.get("http://localhost:5000/apdown")
    assert apdown.status_code == 200


def test_wlan():
    # connected should fail
    connected = requests.get("http://localhost:5000/connected")
    assert connected.status_code == 500

    # enable wpa and confirm scan works
    wpa_status_down = requests.get("http://localhost:5000/wpastatus")
    print(wpa_status_down.text)
    assert json.loads(wpa_status_down.text)["response"]["wpa_state"] in [
        "SCANNING",
        "DISCONNECTED",
    ]

    scan = requests.get("http://localhost:5000/scan")
    assert isinstance(json.loads(scan.text)["response"], list)

    # connect. ssid and key are stored in env file on dev station
    connect = requests.post(
        "http://localhost:5000/connect", json={"ssid": WIFI_SSID, "key": WIFI_KEY}
    )
    assert connect.status_code == 200

    # wpa_state should now be COMPLETED
    wpa_status_up = requests.get("http://localhost:5000/wpastatus")
    assert json.loads(wpa_status_up.text)["response"]["wpa_state"] == "COMPLETED"

    # station should be connected
    connected = requests.get("http://localhost:5000/connected")
    assert connected.status_code == 200

    # set wpa_supplicant.conf to default
    wpadefault = requests.get("http://localhost:5000/wpadefault")
    assert wpadefault.status_code == 200

    # wpa_state should no longer be COMPLETED
    wpa_status_up = requests.get("http://localhost:5000/wpastatus")
    assert json.loads(wpa_status_up.text)["response"]["wpa_state"] != "COMPLETED"

    # turn down wlan1
    connected = requests.get("http://localhost:5000/wlandown")
    assert connected.status_code == 200

    # station should not be connected
    connected = requests.get("http://localhost:5000/connected")
    assert connected.status_code == 500
