from flask import Flask, request, Response, jsonify, make_response, abort
import logging, os, sys, json_logging, json
import commands

log_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

LOG_LEVEL = log_levels[os.getenv("LOG_LEVEL", "INFO")]

app = Flask(__name__)

json_logging.init_flask(enable_json=True)
json_logging.init_request_instrument(app)

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)
logger.addHandler(logging.StreamHandler(sys.stdout))
# handler = logging.handlers.RotatingFileHandler(
# filename="/var/log/ygwifi.log",
#     mode="a",
#     maxBytes=5 * 1024 * 1024,
#     backupCount=2,
#     encoding=None,
#     delay=0,
# )
# logger.addHandler(handler)


# endpoints
@app.after_request
def after_request(response):
    logger.info(
        "%s %s %s %s %s",
        request.method,
        request.path,
        request.scheme,
        response.status,
        response.content_length,
    )

    return response


@app.route("/wpastatus")
def wpastatus():
    """
    wpa_status contains wpa_state so we can see if wpa auth'd successfully
    front end can poll this endpoint and provide feedback (ie auth fail)

    wpa_status = { 
        'bssid': "a8:9a:93:a4:00:e7"
        'freq': "5180"
        'ssid': "wifiname"
        'id': "0"
        'mode': "station"
        'wifi_generation': "5"
        'pairwise_cipher': "CCMP"
        'group_cipher': "CCMP"
        'key_mgmt': "WPA2-PSK"
        'wpa_state': "COMPLETED"
        'ip_address': "192.168.1.45"
        'address': "1c:bf:ce:36:00:e0"
        'uuid': "bf26e924-aeed-59ea-ad0f-6c12b316062d"
        'ieee80211ac': "1"
    }

    possible wpa_states:
        DISCONNECTED
        INACTIVE
        INTERFACE_DISABLED
        SCANNING
        AUTHENTICATING
        ASSOCIATING
        ASSOCIATED
        4WAY_HANDSHAKE (auth failure)
        GROUP_HANDSHAKE
        COMPLETED
        UNKNOWN
    """

    wpa_status_out = commands.wpa_status()

    if wpa_status_out:
        return jsonify({"response": wpa_status_out})
    else:
        return make_response(jsonify({"response": "Failed to get wpa_status"}), 500)


@app.route("/scan")
def scan():
    """
    Enables wlan1
    Scans for ssids
    Returns results as array of strings
    """

    if not commands.start_wpa_supplicant():
        return make_response(
            jsonify({"response": "Failed to start wpa_supplicant"}), 404
        )

    ssids = commands.scan_for_ssids()

    if ssids:
        return jsonify({"response": ssids})
    elif ssids is None:
        return make_response(jsonify({"response": "No SSIDs found"}), 404)
    else:
        return make_response(jsonify({"response": "Scan failed"}), 500)


@app.route("/connect", methods=["POST"])
def connect():
    """
    Takes ssid and key
    Updates wpa_supplicant.conf
    Turns up wlan1
    """

    req_json = json.loads(request.data.decode("utf-8"))

    if not req_json:
        return make_response(jsonify({"response": "wifi ssid and key required"}), 500)

    ssid = req_json["ssid"]
    key = req_json["key"]

    if ssid and key:
        logger.debug(f"SSID:{ssid} selected")

        if not commands.update_wpa_conf(ssid, key):
            return make_response(
                jsonify({"response": "Failed to update wpa_supplicant.conf"}), 500
            )
        elif not commands.wlanup():
            return make_response(jsonify({"response": "Failed to enable wlan1"}), 500)
        else:
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


@app.route("/apup")
def apup():
    """
    Creates ap0 with 192.168.100.1
    Starts hostapd and dnsmasq 
    """

    apup_out = commands.apup()
    if apup_out:
        return jsonify({"response": "ap0 enabled"})
    else:
        return make_response(jsonify({"response": "failed to enable ap0"}), 500)


@app.route("/apdown")
def apdown():
    """
    Deletes ap0
    Kills hostapd and dnsmasq
    Flushes ip
    """

    apdown_out = commands.apdown()
    if apdown_out:
        return jsonify({"response": "ap0 disabled"})
    else:
        return make_response(jsonify({"response": "failed to disable ap0"}), 500)


@app.route("/wlanup")
def wlanup():
    """Turns up wlan and returns a response"""

    wlanup_out = commands.wlanup()

    if wlanup_out:
        return jsonify({"response": "wlan1 enabled"})
    else:
        return make_response(jsonify({"response": "Failed to enable wlan1"}), 500)


@app.route("/wlandown")
def wlandown():
    """Disables wlan1"""

    wlandown_out = commands.wlandown()

    if wlandown_out:
        return jsonify({"response": "wlan1 disabled"})
    else:
        return make_response(jsonify({"response": "Failed to disable wlan1"}), 500)


@app.route("/connected")
def connected():
    """Ping test"""

    if commands.connected():
        return jsonify({"response": "Success"})
    else:
        return make_response(jsonify({"response": "Failure"}), 500)


if __name__ == "__main__":
    app.run()
