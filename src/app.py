"""Flask API for manipulating wifi and ap hotspot"""

import logging
import os
import sys
import json
from flask import Flask, request, jsonify, make_response
from flask.logging import create_logger
import commands

log_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
LOG_LEVEL = log_levels[os.getenv("LOG_LEVEL", "INFO")]

app = Flask("ygwifi")
logger = create_logger(app)

handler = logging.StreamHandler(sys.stdout)

logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)


@app.route("/wpastatus")
def wpastatus():
    """
    wpa_status contains wpa_state so we can see if wpa auth'd successfully
    front end can poll this endpoint and provide feedback (ie auth fail)

    Returns:
        response: {wpa_status}
    """

    wpa_status_out = commands.get_wpa_status()
    logger.debug("wpa_status: %i", wpa_status_out)

    if isinstance(wpa_status_out, dict):
        return jsonify({"response": wpa_status_out})

    return make_response(jsonify({"response": "Failed to get wpa_status"}), 500)


@app.route("/scan")
def scan():
    """Enables wlan1
    Scans for ssids
    Returns results as array of strings

    Returns:
        response: [SSIDs]
    """

    if not commands.start_wpa_supplicant():
        return make_response(
            jsonify({"response": "Failed to start wpa_supplicant"}), 404
        )

    ssids = commands.scan_for_ssids()

    if ssids:
        return jsonify({"response": ssids})

    if ssids is None:
        return make_response(jsonify({"response": "No SSIDs found"}), 404)

    return make_response(jsonify({"response": "Scan failed"}), 500)


@app.route("/connect", methods=["POST"])
def connect():
    """Takes ssid and key
    Updates wpa_supplicant.conf
    Turns up wlan1

    Returns:
        response: success or failure
    """

    req_json = json.loads(request.data.decode("utf-8"))

    if not req_json:
        return make_response(jsonify({"response": "wifi ssid and key required"}), 500)

    ssid = req_json["ssid"]
    key = req_json["key"]

    if ssid and key:
        logger.debug("SSID:%i selected", ssid)

        if not commands.update_wpa_conf(ssid, key):
            return make_response(
                jsonify({"response": "Failed to update wpa_supplicant.conf"}), 500
            )

        if not commands.wlanup():
            return make_response(jsonify({"response": "Failed to enable wlan1"}), 500)

        if commands.connected():
            return jsonify({"response": "Connected"})

        response = "Failed to connect"

    # check for missing parameters
    elif ssid is None and key is None:
        response = "ssid and key not submitted"
    elif ssid is None:
        response = "ssid not submitted"
    elif key is None:
        response = "key not submitted"

    logger.info(response)

    return make_response(jsonify({"response": response}), 500)


@app.route("/wpadefault")
def wpadefault():
    """sets wpa_supplicant.conf to default

    Returns:
        response: success or failure
    """

    wpa_default = commands.wpa_default()
    if wpa_default:
        return jsonify({"response": "wpa_supplicant.conf set to default"})

    return make_response(
        jsonify({"response": "failed to set wpa_supplicant.conf to default"}), 500
    )


@app.route("/apup")
def apup():
    """Creates ap0 with 192.168.100.1
    Starts hostapd and dnsmasq

    Returns:
        response: success or failure
    """

    apup_out = commands.apup()
    if apup_out:
        return jsonify({"response": "ap0 enabled"})

    return make_response(jsonify({"response": "failed to enable ap0"}), 500)


@app.route("/apdown")
def apdown():
    """Deletes ap0
    Kills hostapd and dnsmasq
    Flushes ip

    Returns:
        response: success or failure
    """

    apdown_out = commands.apdown()
    if apdown_out:
        return jsonify({"response": "ap0 disabled"})

    return make_response(jsonify({"response": "failed to disable ap0"}), 500)


@app.route("/wlanup")
def wlanup():
    """Turns up wlan and returns a response

    Returns:
        response: success or failure
    """

    wlanup_out = commands.wlanup()

    if wlanup_out:
        return jsonify({"response": "wlan1 enabled"})

    return make_response(jsonify({"response": "Failed to enable wlan1"}), 500)


@app.route("/wlandown")
def wlandown():
    """Disables wlan1

    Returns:
        response: success or failure
    """

    wlandown_out = commands.wlandown()

    if wlandown_out:
        return jsonify({"response": "wlan1 disabled"})

    return make_response(jsonify({"response": "Failed to disable wlan1"}), 500)


@app.route("/connected")
def connected():
    """Ping test

    Returns:
        response: success or failure
    """

    if commands.connected():
        return jsonify({"response": "Success"})

    return make_response(jsonify({"response": "Failure"}), 500)


if __name__ == "__main__":
    app.run()
