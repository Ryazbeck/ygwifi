from flask import Flask, request, Response
from datetime import datetime as dt
import datetime, logging, os, sys, json_logging
from subprocess import run, PIPE, STDOUT

app = Flask(__name__)

json_logging.init_flask(enable_json=True)
json_logging.init_request_instrument(app)
json_logging.config_root_logger()

# init the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
handler = logging.handlers.RotatingFileHandler(
    '/var/log/ygwifi.log',
    mode='a',
    maxBytes=5 * 1024 * 1024,
    backupCount=2,
    encoding=None,
    delay=0,
)
logger.addHandler(handler)


@app.after_request
def after_request(response):
    ' Logging after every request. '
    logger.info(
        '%s %s %s %s %s',
        request.method,
        request.path,
        request.scheme,
        response.status,
        response.content_length,
    )
    return response


def remove_file(file_path=None):
    if path.exists(file_path):
        logging.debug(f'{file_path} exists. removing')

        try:
            os.remove(file_path)
            return Response('Success', 200)
        except Exception as e:
            logging.info(f'failed to remove {file_path}: {e}')
            return Response('Failure', 500)
    else:
        logging.info(f'{file_path} does not exist.')
        return Response('Failure', 500)
    return Response('Success', 200)


@app.route('/apup')
def apup():
    logging.debug('turning up ap')
    remove_file('/var/run/hostapd/ap0')

    commands = [
        'iw phy phy0 interface add ap0 type __ap',
        'ifconfig ap0 up 192.168.100.1',
        'hostapd -B /etc/hostapd/hostapd.conf',
        'dnsmasq'
    ]

    for cmd in commands:
        try:
            run(cmd)
        except Exception as e:
            logging.info(f'{e}')
            return Response('Failure', 500)
    
    return Response('Success', 200)


@app.route('/apdown')
def apdown():
    logging.debug('turning down ap')

    commands = [
        'ifconfig ap0 down',
        'iw dev ap0 del',
        'killall hostapd dnsmasq'
    ]

    for cmd in commands:
        try:
            run(cmd)
        except Exceptions as e:
            logging.info(f'{e}')
            return Response(e, 500)

    return Response('Success', 200)


@app.route('/scan')
def scan():
    logging.debug('beginning scan for ssids')

    commands = [
        'wpa_cli scan_results | grep WPA | grep -v \\x | awk "{print $NF}" | grep -v ]$',
        'iw wlan0 scan | egrep "SSID: \w" | awk "{print $2}"',
    ]

    results = []

    for cmd in commands:
        try:
            results.append(run(cmd, capture_output=True).split('\n'))
        except Exception as e:
            logging.info(f'{e}')
            return Response(e, 500)

    logging.debug(f'scan results:{", ".join(results)}')

    return Response(str(set(results)), 200)


def edit_wpa_supplicant(ssid=None, key=None):
    if ssid and key:
        logging.debug('ssid and key submitted')

        wpa_supplicant_conf = f'''
            country=US
            ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
            update_config=1

            network={{
                ssid={ssid}
                psk={key}
            }}
            '''

        wpa_supplicant_path = os.environ('WPA_SUPPLICANT_PATH')

        try:
            logging.debug(f'opening {wpa_supplicant_path}')
            wpa_supplicant = open(wpa_supplicant_path)
        except:
            logging.info(f'failed opening {wpa_supplicant_path}')
            return 500

        try:
            logging.debug(f'writing {wpa_supplicant_path}')
            wpa_supplicant.write(wpa_supplicant_conf)
            return 200
        except:
            logging.info(f'{e}')
            return 500

    elif ssid and key is None:
        logging.info('ssid and key not submitted')
    elif ssid is None:
        logging.info('ssid not submitted')
    elif key is None:
        logging.info('key not submitted')

    return 500


def start_wpa_supplicant():
    # sometimes this file sticks around. this will remove if it exists
    remove_file('/var/run/wpa_supplicant/wlan0')
    try:
        logging.debug('starting wpa_supplicant')
        run('wpa_supplicant', 
            '-B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf')
        return 200
    except Exception as e:
        message = f'wpa_supplicant failed to start: {e}'
        logging.info()
        return 500


@app.route('/wlanup')
def wlanup():
    logging.debug('turning up wifi')
    commands = [
        'ifconfig wlan0 up',
        'dhclient wlan0'
    ]

    for cmd in commands:
        try:
            run(cmd)
            return Response('Success', 200)
        except Exception as e:
            logging.info(e)
            return Response(f'Failure {e}', 500)


@app.route('/wlandown')
def wlandown():
    logging.debug('turning down wifi')
    commands = [
        'ifconfig wlan0 down',
        'ip addr flush wlan0',
        'dhclient -r'
    ]

    for cmd in commands:
        try:
            run(cmd)
            return Response('Success', 200)
        except Exception as e:
            logging.info(e)
            return Response(f'Failure {e}', 500)
    

@app.route('/connect')
def connect():
    ssid = request.args.get('ssid', None)
    key = request.args.get('key', None)
    
    logging.debug('connecting to wifi')
    edit_wpa_supplicant(ssid, key)
    return v()


@app.route('/connected')
def connected():
    response = os.system('ping -c 1 google.com')
    if response == 0:
        return Response('Success', 200)
    return Response('Failure', 500)


if __name__ == '__main__':
    app.run()
