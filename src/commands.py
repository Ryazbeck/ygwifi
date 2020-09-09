from subprocess import (
    run,
    check_call,
    check_output,
    CalledProcessError,
    Popen,
    PIPE,
    STDOUT,
)
from typing import List
import logging

logger = logging.getLogger()


def _check_output(command: List[str]):
    """generic handler for check_output"""

    logger.debug(f"check_output: '{' '.join(command)}'")

    try:
        check_output(command, stderr=STDOUT)
    except CalledProcessError as e:
        logger.warning(e.output)
        return False
    except Exception as e:
        logger.warning(e)
        return False
    else:
        return True


def start_wpa_supplicant():
    """
    Starting this service is already handled in interfaces for ifup and ifdown
    But scan still needs to be able to use wpa_supplicant for finding SSIDs
    """

    logger.debug("Starting wpa_supplicant")

    _check_output(["killall", "wpa_supplicant"])

    return _check_output(
        ["wpa_supplicant", "-B", "-i", "wlan1", "-c", "/cfg/wpa_supplicant.conf"]
    )


def wpa_status():
    """
    Checks that wpa_supplicant is running
    Retrieves `wpa_cli status` and returns it as a dict
    """

    logger.debug("Retrieving wpa_cli status")

    start_wpa_supplicant()

    try:
        wpa_status_out = Popen(
            ["wpa_cli", "-i", "wlan1", "status"], stdout=PIPE, universal_newlines=True,
        )
    except Exception as e:
        logger.info(f"failed to get wpa_cli status: {e}")
        return False

    whoami = run(["whoami"], capture_output=True, text=True)
    logger.debug(whoami.stdout)
    wpa_status = {}

    for fld in wpa_status_out.stdout.readlines():
        field = fld.split("=")
        wpa_status[field[0]] = field[1].strip()

    logger.debug(f"wpa_cli status: {wpa_status}")

    return wpa_status


def scan_for_ssids():
    """
    If wpa_status is true then wpa_supplicant is running
    Issue scan command and return SSIDs as an array
    """

    if not wpa_status():
        return False

    logger.debug("Scanning for SSIDs")

    try:
        scan_results = Popen(
            ["iw", "wlan1", "scan"], stdout=PIPE, universal_newlines=True
        )

        """pipes to clean the results"""
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
            return ssids
        else:
            return None

    except Exception as e:
        logger.warning(f"Scan failed: {e}")
        return False


def update_wpa_conf(ssid=None, key=None):
    """ 
    hashes the user's wifi key
    then adds network with ssid and psk to wpa_supplicant.conf 
    """

    logger.debug("Updating wpa_supplicant.conf")

    # hash the key
    try:
        wpa_passphrase = Popen(
            ["wpa_passphrase", f"{ssid}", f"{key}"],
            universal_newlines=True,
            stdout=PIPE,
        )
    except Exception as e:
        logger.info(e)
        return False

    # get hash from output
    for line in wpa_passphrase.stdout.readlines():
        if "psk" in line and "#" not in line:
            passphrase = line.strip().replace("psk=", "")
            break

    # this goes in the conf file so we can reuse it after boot
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
        logger.info(e)
        return False

    try:
        logger.debug(f"writing {wpa_supplicant_path}")
        wpa_supplicant.write(wpa_supplicant_conf)
        return True
    except Exception as e:
        logger.info(e)
        return False


def apup():
    logger.debug("Enabling ap0")
    return _check_output(["ifup", "ap0"])


def apdown():
    logger.debug("Disabling ap0")
    return _check_output(["ifdown", "ap0"])


def wlanup():
    logger.debug("Enabling wlan1")

    try:
        check_call(["grep", "ssid", "/cfg/wpa_supplicant.conf"])
    except Exception:
        logger.info("Cannot enable wlan1, wpa_supplicant.conf is not configured")

    if wpa_status()["wpa_state"] == "4WAY_HANDSHAKE":
        logger.info("Cannot enable wlan1: wifi authentication failure")
        return False

    if wpa_status()["wpa_state"] != "COMPLETED":
        logger.info("Wifi is not authenticated, attempting")
        try:
            check_call(["wpa_cli", "reconfigure"])
        except Exception:
            logger.debug("wpa_cli reconfigure timed out. checking wpa_state")
            if wpa_status()["wpa_state"] != "COMPLETED":
                return False

    return _check_output(["ifup", "wlan1"])


def wlandown():
    logger.debug("Disabling wlan1")
    return _check_output(["ifdown", "wlan1"])


def connected():
    logger.debug("Checking connectivity")
    return _check_output(["ping", "-I", "wlan1", "-c", "1", "-W", "1", "google.com"])
