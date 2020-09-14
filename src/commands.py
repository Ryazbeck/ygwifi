"""
This module handles the system commands used for manipulating
the wifi and ap hotspot
"""

from subprocess import (
    check_call,
    check_output,
    CalledProcessError,
    Popen,
    PIPE,
    STDOUT,
)
from typing import List
import logging
from time import sleep


WPA_SUPPLICANT_PATH = "/cfg/wpa_supplicant.conf"
WPA_SUPPLICANT_BASE = """
    country=US
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    p2p_disabled=1
    """

logger = logging.getLogger("ygwifi.commands")


def _check_output(command: List[str]):
    """Generic handler for check_output"""

    logger.debug("check_output: %i", " ".join(command))

    try:
        check_output(command, stderr=STDOUT)
    except CalledProcessError as error:
        logger.warning(error.output)
        return False
    else:
        return True


def start_wpa_supplicant():
    """
    Start wpa_supplicant so we can scan for SSIDs
    """

    logger.debug("Starting wpa_supplicant")

    try:
        check_call(["pgrep", "-f", "wpa_supplicant.conf"])
    except CalledProcessError as error:
        logger.debug(error)
        return _check_output(
            ["wpa_supplicant", "-B", "-i", "wlan1", "-c", "/cfg/wpa_supplicant.conf"]
        )
    else:
        return True


def get_wpa_status():
    """
    - Checks that wpa_supplicant is running
    - Retrieves `wpa_cli status`
    - Returns it as a dict
    """

    logger.debug("Retrieving wpa_cli status")

    start_wpa_supplicant()

    try:
        wpa_status_out = Popen(
            ["wpa_cli", "-i", "wlan1", "status"], stdout=PIPE, universal_newlines=True,
        )
        logger.debug("wpa_status_out: %i", wpa_status_out)
    except CalledProcessError as error:
        logger.info("failed to get wpa_cli status: %i", error)
        return False

    wpa_status_ret = {}

    for fld in wpa_status_out.stdout.readlines():
        field = fld.split("=")
        wpa_status_ret[field[0]] = field[1].strip()

    logger.debug("wpa_cli status: %i", wpa_status_ret)

    return wpa_status_ret


def scan_for_ssids():
    """
    - If get_wpa_status is true then wpa_supplicant is running
    - Issue scan command and return SSIDs as an array
    """

    if not get_wpa_status():
        return False

    logger.debug("Scanning for SSIDs")

    try:
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
        ssids = list({ssid.strip() for ssid in scan.stdout.readlines()})

        logger.debug("scan results: %i", ", ".join(ssids))

        if ssids:
            return ssids

        return None

    except CalledProcessError as error:
        logger.warning("Scan failed: %i", error)
        return False


def update_wpa_conf(ssid=None, key=None):
    """
    Updates wpa_supplicant.conf with the submitted ssid/key
    - Hashes the user's wifi key
    - Adds network with ssid and psk to wpa_supplicant.conf
    """

    logger.debug("Updating wpa_supplicant.conf")

    # hash the key
    try:
        wpa_passphrase = Popen(
            ["wpa_passphrase", f"{ssid}", f"{key}"],
            universal_newlines=True,
            stdout=PIPE,
        )
    except CalledProcessError as error:
        logger.info(error)
        return False

    # get hash from output
    for line in wpa_passphrase.stdout.readlines():
        if "psk" in line and "#" not in line:
            passphrase = line.strip().replace("psk=", "")
            break

    # this goes in the conf file so we can reuse it after boot
    wpa_supplicant_conf = f"""
        {WPA_SUPPLICANT_BASE}
        network={{
            ssid="{ssid}"
            psk={passphrase}
        }}
        """

    try:
        logger.debug("opening %i", WPA_SUPPLICANT_PATH)
        wpa_supplicant = open(WPA_SUPPLICANT_PATH, "w")
    except OSError as error:
        logger.info(error)
        return False

    try:
        logger.debug("writing %i", WPA_SUPPLICANT_PATH)
        wpa_supplicant.write(wpa_supplicant_conf)
        wpa_supplicant.close()
        return True
    except OSError as error:
        logger.info(error)
        return False


def wpa_default():
    """ Sets wpa_supplicant.conf to the base (no creds) """

    logger.debug("Setting wpa_supplicant.conf to default")

    try:
        logger.debug("opening %i", WPA_SUPPLICANT_PATH)
        wpa_supplicant = open(WPA_SUPPLICANT_PATH, "w")
    except OSError as error:
        logger.info(error)
        return False

    try:
        logger.debug("writing %i", WPA_SUPPLICANT_PATH)
        wpa_supplicant.write(WPA_SUPPLICANT_BASE)
        wpa_supplicant.close()
    except OSError as error:
        logger.info(error)
        return False

    try:
        check_call(["wpa_cli", "reconfigure"])
    except CalledProcessError as error:
        logger.debug("wpa_cli reconfigure timed out: %i", error)
    else:
        return True


def apup():
    """ Turns up ap0 using /etc/network/interfaces """
    logger.debug("Enabling ap0")
    return _check_output(["ifup", "ap0"])


def apdown():
    """ Turns down ap0 using /etc/network/interfaces """
    logger.debug("Disabling ap0")
    return _check_output(["ifdown", "ap0"])


def wlanup():
    """
    Handles turning up wlan1
    - Starts wpa_supplicant
    - Waits an extra 3 seconds x2 for wpa to be COMPLETED
    - Requests dhcp address
    """

    logger.debug("Enabling wlan1")

    try:
        check_call(["grep", "ssid", "/cfg/wpa_supplicant.conf"])
    except CalledProcessError as error:
        logger.info(
            "Cannot enable wlan1, wpa_supplicant.conf is not configured: %i", error
        )
        return False

    start_wpa_supplicant()

    attempt = 0
    while attempt < 2:
        if get_wpa_status()["wpa_state"] != "COMPLETED":
            logger.info("Wifi is not authenticated, attempting")
            try:
                check_call(["wpa_cli", "reconfigure"])
            except CalledProcessError as error:
                logger.debug(
                    "wpa_cli reconfigure timed out [%i]. checking wpa_state", error
                )
        else:
            logger.debug(
                "wpa_state is not completed, waiting 3 seconds and checking again"
            )
            attempt = attempt + 1
            sleep(3)

    if get_wpa_status()["wpa_state"] != "COMPLETED":
        return False

    return _check_output(["udhcpc", "-i", "wlan1"])


def wlandown():
    """
    Handles wlan1 down
    - Kills wpa_supplicant and dhcp
    - Flushes dhcp address
    """
    logger.debug("Disabling wlan1")
    _check_output(["killall", "wpa_supplicant", "udhcpc"])
    return _check_output(["ip", "addr", "flush", "wlan1"])


def connected():
    """ Checks connectivity to internet """
    logger.debug("Checking connectivity")
    return _check_output(["ping", "-I", "wlan1", "-c", "1", "-W", "1", "google.com"])
