from flask import Flask, request, Response
from datetime import datetime as dt
import datetime, logging, os, sys, json_logging
from subprocess import check_call, run, CalledProcessError, Popen, PIPE

app = Flask(__name__)

json_logging.init_flask(enable_json=True)
json_logging.init_request_instrument(app)

# init the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
handler = logging.handlers.RotatingFileHandler(
    "/var/log/ygwifi.log",
    mode="a",
    maxBytes=5 * 1024 * 1024,
    backupCount=2,
    encoding=None,
    delay=0,
)
logger.addHandler(handler)


def update_wpa_conf(ssid=None, key=None):
    logger.debug("Updating wpa_supplicant.conf")

    # hash the key
    wpa_passphrase = Popen(
        ["wpa_passphrase", f'"{ssid}"', f'"{key}"'],
        universal_newlines=True,
        stdout=PIPE,
    ).stdout.readlines()

    # get hash from output
    for line in wpa_passphrase:
        if "psk" in line and "#" not in line:
            passphrase = line.strip().replace("psk=", "")
            break

    # this goes in the conf file so we can reuse it
    wpa_supplicant_conf = f"""
        country=US
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1
        p2p_disabled=1

        network={{
            ssid="{ssid}"
            psk={passphrase}
        }}
        """

    wpa_supplicant_path = "/cfg/wpa_supplicant.conf"

    try:
        logger.debug(f"opening {wpa_supplicant_path}")
        wpa_supplicant = open(wpa_supplicant_path, "w")
    except Exception as e:
        logger.info(f"failed opening: {e}")
        return False

    try:
        logger.debug(f"writing {wpa_supplicant_path}")
        wpa_supplicant.write(wpa_supplicant_conf)
        return True
    except Exception as e:
        logger.info(f"failed writing: {e}")
        return False


def start_wpa_supplicant():
    """
    Enables scan for ssids
    If wpa_supplicant is configured station will connect to wifi
    """

    logger.debug("Starting wpa_supplicant")

    try:
        check_call(["killall", "wpa_supplicant"])
        check_call(
            ["wpa_supplicant", "-B", "-i", "wlan1", "-c", "/cfg/wpa_supplicant.conf"]
        )
        return True
    except Exception as e:
        logger.warning(f"wpa_supplicant failed to start: {e}")
        return False


def wpa_status():
    logger.debug("Retrieving wpa_cli status")

    try:
        wpa_status_out = Popen(
            ["wpa_cli", "status"], stdout=PIPE, universal_newlines=True
        )
    except Exception as e:
        logger.info(f"failed to get wpa_cli status: {e}")
        return False

    wpa_status = {}

    for fld in wpa_status_out.stdout.readlines()[1::]:
        field = fld.split("=")
        wpa_status[field[0]] = field[1].strip()

    logger.debug(f"wpa_cli status: {wpa_status}")

    return wpa_status


def wlanup_cmd():
    logger.debug("Enabling wlan1")

    try:
        check_call(["ifup", "wlan1"])
        return True
    except Exception as e:
        logger.info(f"Failed to enable wlan1: {e}")
        return False


def wlanup_response():
    if wlanup_cmd():
        return Response("wlan1 enabled", 200)
    return Response(f"Failed to enable wlan1", 500)


def initialize():
    logger.debug("Initializing ygwifi")

    start_wpa_supplicant()

    if wpa_status()["wpa_state"] == "COMPLETED":
        return wlanup_cmd()
    return True


# endpoints
@app.after_request
def after_request(response):
    " Logging after every request. "
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
        return Response("ap0 enabled", 200)
    except Exception as e:
        response = f"Failed to enable ap0: {e}"
        logger.warning(response)
        return Response(response, 500)


@app.route("/apdown")
def apdown():
    logger.debug("Disabling ap0")

    try:
        check_call(["ifdown", "ap0"])
        return Response("ap0 disabled", 200)
    except Exception as e:
        response = f"Failed to disable ap0: {e}"
        logger.warning(response)
        return Response(response, 500)


@app.route("/scan")
def scan():
    logger.debug("Scanning for ssids")

    try:
        # subsequent Popens are pipes to clean the results
        scan_results = Popen(
            ["iw", "wlan0", "scan"], stdout=PIPE, universal_newlines=True
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
        ssids = ", ".join(ssids)

        logger.debug(f"scan results:{ssids}")
        if ssids:
            return Response(str(ssids), 200)

    except Exception as e:
        logger.warning(f"Scan failed: {e}")
        return Response("Scan failed", 500)


@app.route("/wlanup")
def wlanup():
    return wlanup_response()


@app.route("/wlandown")
def wlandown():
    logger.debug("Disabling wlan1")

    try:
        check_call(["ifdown", "wlan1"])
        return Response("wlan1 disabled", 200)
    except Exception as e:
        response = f"Failed to disable wlan1: {e}"
        logger.info(response)
        return Response(response, 500)


@app.route("/connect")
def connect():
    ssid = request.args.get("ssid", None)
    key = request.args.get("key", None)

    if ssid and key:
        logger.debug(f"connecting to {ssid}")

        if not update_wpa_conf(ssid, key):
            return Response("Failed to update wpa_supplicant.conf", 500)
        elif not wlanup_cmd():
            return Response("Failed to establish connection", 500)
        return wlanup_response()

    # missing parameters
    elif ssid and key is None:
        response = "ssid and key not submitted"
    elif ssid is None:
        response = "ssid not submitted"
    elif key is None:
        response = "key not submitted"

    logger.info(response)
    return Response(response, 500)


@app.route("/connected")
def connected():
    connected = os.system("ping -c 1 google.com")
    if connected == 0:
        return Response("Success", 200)
    return Response("Failure", 500)


if __name__ == "__main__":
    if initialize():
        app.run()
    else:
        logger.critical("Failed to initialize app")
        exit()
