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


def run_commands(commands, success_message='Success'):
    for cmd in commands:
        try:
            check_call(cmd)
        except CalledProcessError as e:
            logger.info(e)
            return Response(f'Failure: {e}', 500)

    return Response(f'Success: {success_message}', 200)


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


def start_wpa():
    '''
    always start wpa
    if wpa_supplicant is configured then station will connect to wifi
    else it will allow us to scan for ssids to connect to
    '''

    logger.debug('Starting wpa')

    # sometimes this file hangs. remove it
    remove_file('/var/run/wpa_supplicant/wlan0')

    try:
        check_call(['wpa_cli', 'status'])
        logger.debug('wpa already started')
    except:
        try:
            check_call(
                'wpa_supplicant', 
                '-B', # background
                '-i', 'wlan0',
                '-c', '/etc/wpa_supplicant/wpa_supplicant.conf'
            )
        except Exception as e:
            logger.info(f'wpa_supplicant failed to start: {e}')
            return False

    return True


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
    logger.debug('turning up ap')

    # sometimes this file sticks around. this will remove if it exists
    remove_file('/var/run/hostapd/ap0')

    commands = [
        ['iw', 'phy', 'phy0', 'interface', 'add', 'ap0', 'type', '__ap'],
        ['ifconfig', 'ap0', 'up', '192.168.100.1'],
        ['hostapd', '-B', '/etc/hostapd/hostapd.conf'],
        ['dnsmasq']
    ]
    
    return run_commands(
        commands,
        success_message='AP enabled'
    )


@app.route('/apdown')
def apdown():
    logger.debug('turning down ap')

    commands = [
        ['ifconfig', 'ap0', 'down'],
        ['iw', 'dev', 'ap0', 'del'],
        ['killall', 'hostapd', 'dnsmasq']
    ]
    
    return run_commands(
        commands,
        success_message='AP disabled'
    )


@app.route('/scan')
def scan():
    logger.debug('beginning scan for ssids')

    try:
        check_call(['wpa_cli', 'status'])
    except CalledProcessError as e:
        logger.info(f'wpa_cli not started: {e}')
        start_wpa()

    try:
        # the subsequent Popens are pipes to clean the results
        scan_results = Popen(['iw', 'wlan0', 'scan'], 
            stdout=PIPE, universal_newlines=True)
        scan_ssids = Popen(['egrep', 'SSID: \w'], 
            stdin=scan_results.stdout, stdout=PIPE, universal_newlines=True)
        scan_ssids = Popen(['awk', '{print $2}'], 
            stdin=scan_ssids.stdout, stdout=PIPE, universal_newlines=True)
        ssids = list(set([ssid.strip() for ssid in scan_ssids.stdout.readlines()]))

        logger.debug(f'scan results:{", ".join(ssids)}')

        return Response(str(set(ssids)), 200)
    except Exceptions as e:
        logger.info(f'scanning failed: {e}')

        return Response(e, 500)



@app.route('/wlanup')
def wlanup():
    logger.debug('turning up wifi')

    commands = [
        ['ifconfig', 'wlan0', 'up'],
        ['dhclient', 'wlan0']
    ]
    
    return run_commands(
        commands,
        'wlan0 enabled'
    )


@app.route('/wlandown')
def wlandown():
    logger.debug('turning down wifi')
    commands = [
        ['ifconfig', 'wlan0', 'down'],
        ['wpa_cli', 'terminate'],
        ['dhclient', '-r'],
        ['ip', 'addr', 'flush', 'wlan0'],
    ]
    
    return run_commands(
        commands,
        'wlan0 disabled'
    )
    

@app.route('/connect')
def connect():
    ssid = request.args.get('ssid', None)
    key = request.args.get('key', None)

    logger.debug(f'connecting to {ssid}')
    
    if ssid and key:
        logger.debug('ssid and key submitted')

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

        # probably unnecessary
        wpa_supplicant_path = os.environ('WPA_SUPPLICANT_PATH')

        try:
            logger.debug(f'opening {wpa_supplicant_path}')
            wpa_supplicant = open(wpa_supplicant_path, 'w')
        except Exception as e:
            logger.info(f'failed opening: {e}')
            return Response(e, 500)

        try:
            logger.debug(f'writing {wpa_supplicant_path}')
            wpa_supplicant.write(wpa_supplicant_conf)
            return Response('Success', 200)
        except Exception as e:
            logger.info(f'failed writing: {e}')

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
    response = os.system('ping -c 1 google.com')
    if response == 0:
        return Response('Success', 200)
    return Response('Failure', 500)


if __name__ == '__main__':
    start_wpa()
    app.run()
