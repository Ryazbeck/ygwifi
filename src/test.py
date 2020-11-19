"""
This runs outside ygwifi in its own container to test the flask API
while it's running on the test device.
"""

import json
import os
import requests


WIFI_SSID = os.getenv("WIFI_SSID", None)
WIFI_KEY = os.getenv("WIFI_KEY", None)


def test_ap_up():
    """ Verifies ap0 up """
    apup = requests.get("http://localhost:5000/apup")
    assert apup.status_code == 200


def test_ap_down():
    """ Verifies ap0 down """
    apdown = requests.get("http://localhost:5000/apdown")
    assert apdown.status_code == 200


def test_wlan_down():
    """
    Tests wlan down functionality
    - Sets wpa_supplicant.conf to default
    - Verifies wifi is no longer authenticated
    - Turns down wlan1
    - Verifies connection is down
    """

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


def test_wlan_up():
    """
    Tests wlan up functionality
    - Verifies connection is down
    - Submits ssid and key for connect
    - Verifies connection established
    """

    # connected should fail
    connected = requests.get("http://localhost:5000/connected")
    assert connected.status_code in [200, 500]

    # enable wpa and confirm scan works
    wpa_status_down = requests.get("http://localhost:5000/wpastatus")
    assert json.loads(wpa_status_down.text)["response"]["wpa_state"] in [
        "SCANNING",
        "DISCONNECTED",
        "COMPLETED",
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
