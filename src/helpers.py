from flask import Flask, request, Response, jsonify, make_response, abort
from subprocess import check_call, run, CalledProcessError, Popen, PIPE
import logging, sys, json_logging
from time import sleep

logger = logging.getLogger()


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
        sleep(1)
        check_call(
            ["wpa_supplicant", "-B", "-i", "wlan1", "-c", "/cfg/wpa_supplicant.conf"]
        )
        return True
    except CalledProcessError as e:
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
    except CalledProcessError as e:
        logger.info(f"Failed to enable wlan1: {e}")
        return False


def wlanup_response():
    """Turns up wlan and returns a response"""
    if wlanup_cmd():
        return jsonify({"wlan1 enabled"})
    return make_response(jsonify({"response": "Failed to enable wlan1"}), 500)
