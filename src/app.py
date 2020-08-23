from flask import Flask, request, Response, jsonify, make_response, abort
from subprocess import check_call, run, CalledProcessError, Popen, PIPE
from datetime import datetime as dt
from time import sleep
import datetime, logging, os, sys, json_logging
from helpers import (
    update_wpa_conf,
    start_wpa_supplicant,
    wpa_status,
    wlanup_cmd,
    wlanup_response,
)

FLASK_ENV = os.environ["FLASK_ENV"]

app = Flask(__name__)

json_logging.init_flask(enable_json=True)
json_logging.init_request_instrument(app)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
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


@app.route("/apup")
def apup():
    logger.debug("Enabling ap0")

    try:
        check_call(["ifup", "ap0"])
        return jsonify({"response": "ap0 enabled"})
    except Exception as e:
        response = f"Failed to enable ap0: {e}"
        logger.warning(response)
        return make_response(jsonify({"response": response}), 500)


@app.route("/apdown")
def apdown():
    logger.debug("Disabling ap0")

    try:
        check_call(["ifdown", "ap0"])
        return jsonify({"response": "ap0 disabled"})
    except Exception as e:
        response = f"Failed to disable ap0: {e}"
        logger.warning(response)
        return make_response(jsonify({"response": response}), 500)


@app.route("/scan")
def scan():
    logger.debug("Scanning for ssids")

    if not start_wpa_supplicant():
        abort(404)

    try:
        # subsequent Popens are pipes to clean the results
        scan_results = Popen(
            ["iw", "wlan1", "scan"], stdout=PIPE, universal_newlines=True
        )
        scan = Popen(
            ["egrep", r"SSID: \w"],
            stdin=scan_results.stdout,
            stdout=PIPE,
            universal_newlines=True,
        )
        scan = Popen(
            ["awk", "{print $2}"],
            stdin=scan.stdout,
            stdout=PIPE,
            universal_newlines=True,
        )
        ssids = list(set([ssid.strip() for ssid in scan.stdout.readlines()]))

        logger.debug(f"scan results:{', '.join(ssids)}")
        if ssids:
            return jsonify({"response": ssids})
        else:
            return make_response(jsonify({"response": "No SSIDs found"}), 404)

    except Exception as e:
        logger.warning(f"Scan failed: {e}")
        return make_response(jsonify({"response": "Scan failed"}), 500)


@app.route("/wlanup")
def wlanup():
    return wlanup_response()


@app.route("/wlandown")
def wlandown():
    logger.debug("Disabling wlan1")

    try:
        check_call(["ifdown", "wlan1"])
        return jsonify({"response": "wlan1 disabled"})
    except Exception as e:
        response = f"Failed to disable wlan1: {e}"
        logger.info(response)
        return make_response(jsonify({"response": response}), 500)


@app.route("/connect", methods=["POST"])
def connect():
    """
    takes ssid and key
    updates wpa_supplicant.conf
    turns up wlan1
    """

    if not request.json:
        abort(400)

    ssid = request.json["ssid"]
    key = request.json["key"]

    if ssid and key:
        logger.debug(f"connecting to {ssid}")

        if not update_wpa_conf(ssid, key):
            return make_response(
                jsonify({"response": "Failed to update wpa_supplicant.conf"}), 500
            )
        elif not wlanup_cmd():
            return make_response(
                jsonify({"response": "Failed to establish connection"}), 500
            )

        return wlanup_response()

    # missing parameters
    elif ssid and key is None:
        response = "ssid and key not submitted"
    elif ssid is None:
        response = "ssid not submitted"
    elif key is None:
        response = "key not submitted"

    logger.info(response)

    return make_response(jsonify({"response": response}), 500)


@app.route("/connected")
def connected():
    """ping test"""
    try:
        check_call(["ping", "-c", "1", "google.com"])
        return jsonify({"response": "Success"})
    except CalledProcessError as e:
        return make_response(jsonify({"response": f"Failure: {e}"}), 500)


if __name__ == "__main__":
    app.run(debug=FLASK_ENV == "development")
