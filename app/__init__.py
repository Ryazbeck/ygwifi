from flask import Flask, request, Response
from datetime import datetime as dt
import datetime, logging, os, sys, json_logging
from subprocess import check_call, run, CalledProcessError

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


# helper funcs
def run_commands(commands, success_message='Success'):
    for cmd in commands:
        try:
            check_call(cmd)
        except CalledProcessError as e:
            logger.info(e)
            return False

    return True


def remove_file(file_path=None):
    if path.exists(file_path):
        logger.debug(f'{file_path} exists. removing')
        try:
            os.remove(file_path)
        except Exception as e:
            logger.info(f'failed to remove {file_path}: {e}')
            return False
    else:
        logger.info(f'{file_path} does not exist.')

    return True


def update_wpa_conf(ssid=None, key=None):
    logger.debug('Updating wpa_supplicant.conf')

    # hash the key
    wpa_passphrase = Popen(
        ['wpa_passphrase', f'"{ssid}"', f'"{key}"'], 
        universal_newlines=True, stdout=PIPE
    ).stdout.readlines()

    # get hash from output
    for line in wpa_passphrase:
        if 'psk' in line and '#' not in line:
            passphrase = line.strip().replace('psk=','')
            break

    # this goes in the conf file so we can reuse it
    wpa_supplicant_conf = f'''
        country=US
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1
        p2p_disabled=1

        network={{
            ssid="{ssid}"
            psk={passphrase}
        }}
        '''

    wpa_supplicant_path = '/cfg/wpa_supplicant.conf'

    try:
        logger.debug(f'opening {wpa_supplicant_path}')
        wpa_supplicant = open(wpa_supplicant_path, 'w')
    except Exception as e:
        logger.info(f'failed opening: {e}')
        return False

    try:
        logger.debug(f'writing {wpa_supplicant_path}')
        wpa_supplicant.write(wpa_supplicant_conf)
        return True
    except Exception as e:
        logger.info(f'failed writing: {e}')
        return False


def wpa_status();
    logger.debug('Retrieving wpa_cli status')

    try:
        wpa_status_out = Popen(['wpa_cli', 'status'], 
        stdout=PIPE, universal_newlines=True)
    except Exception as e:
        logger.info(f'failed to get wpa_cli status: {e}')
        return False

    wpa_status = {}
    
    for fld in wpa_status_out.stdout.readlines()[1::]:
        field = fld.split('=')
        wpa_status[field[0]] = field[1].strip()

    logger.debug(f'wpa_cli status: {wpa_status}')
        
    return wpa_status


def start_wpa():
    '''
    Enables scan for ssids
    If wpa_supplicant is configured station will connect to wifi
    '''

    logger.debug('Starting wpa_supplicant')

    try:
        check_call(['killall', 'wpa_supplicant'])
        check_call([
            'wpa_supplicant',
            '-B',
            '-i', 'wlan1',
            '-c', '/cfg/wpa_supplicant.conf'
        ])
        return True
    except Exception as e:
        logger.warning(f'wpa_supplicant failed to start: {e}')
        return False


def get_ip():
    logger.debug('Requesting IP address')

    try:
        check_call(['killall', 'dhclient'])
        check_call(['dhclient', '-v', 'wlan1'])
        return True
    except Exception as e:
        debug.info(f'dhclient failed to get IP: {e}')
        return False


def _connected()
    connected = os.system('ping -c 1 google.com')
    if connected == 0:
        return True
    return False


def _connect(initialize=False):
    # initialize will return True even if wpa_state isn't COMPLETED
    logger.debug('Connect to wifi')

    if start_wpa():
        if wpa_status()['wpa_state'] != 'COMPLETED':
            # there are no creds or they are wrong
            logger.info(f'wifi is not authenticated')
        
            if initialize:
                # we can end initialization here and wait for user to update
                return True
            return False

        elif not get_ip():
            logger.critical(f'failed to get IP address')
            return False

    return True


def _scan():
    logger.debug('Scanning for ssids')

    try:
        # the subsequent Popens are pipes to clean the results
        scan_results = Popen(['iw', 'wlan0', 'scan'], 
            stdout=PIPE, universal_newlines=True)
        scan_ssids = Popen(['egrep', 'SSID: \w'], 
            stdin=scan_results.stdout, stdout=PIPE, universal_newlines=True)
        scan_ssids = Popen(['awk', '{print $2}'], 
            stdin=scan_ssids.stdout, stdout=PIPE, universal_newlines=True)
        ssids = list(set([ssid.strip() for ssid in scan_ssids.stdout.readlines()]))
        ssids = ", ".join(ssids)

        logger.debug(f'scan results:{ssids}')
    except Exception as e:
        logger.warning(f'Failed to get scan results: {e}')
        return False
    
    return set(ssids)


def initialize():
    logger.debug('Initializing ygwifi')
    _connect(initialize=True)


# endpoints
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


@app.route('/apup')
def apup():
    logger.debug('Enabling AP')

    commands = [
        ['iw', 'phy', 'phy0', 'interface', 'add', 'ap0', 'type', '__ap'],
        ['ifconfig', 'ap0', 'up', '192.168.100.1'],
        ['hostapd', '-B', '/etc/hostapd/hostapd.conf'],
        ['dnsmasq']
    ]
    
    if run_commands(commands):
        return Response('AP enabled', 200)

    return Response('Failed to enable AP:', 500)


@app.route('/apdown')
def apdown():
    logger.debug('Disabling AP')

    commands = [
        ['ifconfig', 'ap0', 'down'],
        ['killall', 'hostapd', 'dnsmasq']
    ]
    
    if run_commands(commands):
        return Response('AP disabled', 200)

    return Response('Failed to disable AP', 500)


@app.route('/scan')
def scan():
    if wpa_status():
        ssids = _scan()
        if ssids:
            return Response(str(ssids), 200)

    return Response('Scan failed', 500)


@app.route('/wlandown')
def wlandown():
    logger.debug('turning down wifi')
    commands = [
        ['ifconfig', 'wlan1', 'down'],
        ['killall', 'wpa_supplicant', 'dhclient'],
        ['ip', 'addr', 'flush', 'wlan1'],
    ]
    
    if run_commands(commands):
        return Response('wlan1 disabled', 200)

    return Response('Failed to disable wlan1', 500)
    

@app.route('/connect')
def connect():
    ssid = request.args.get('ssid', None)
    key = request.args.get('key', None)

    if ssid and key:
        logger.debug(f'connecting to {ssid}')
        
        if not update_wpa_conf(ssid, key):
            return Response('Failed to update wpa_supplicant.conf', 500)
        elif not _connect():
            return Response('Failed to establish connection', 500)
        else:
            return Response('connection established', 200)

    # missing parameters
    elif ssid and key is None:
        response = 'ssid and key not submitted'
    elif ssid is None:
        response = 'ssid not submitted'
    elif key is None:
        response = 'key not submitted'

    logger.info(response)
    return Response(response, 500)


@app.route('/connected')
def connected():
    if _connected():
        return Response('Success', 200)

    return Response('Failure', 500)


if __name__ == '__main__':
    if initialize():
        app.run()
    else:
        logged.critical('Failed to initialize app')
        exit()