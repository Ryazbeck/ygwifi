from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
from time import sleep
from os import path, getcwd
import subprocess

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

'''
This enables interacting with the Pi directly so we can 
- Enable and disable hotspot
- Configure wpa_supplicant.conf for user's wi-fi
- Confirm connection is established
- toggle ap0
- toggle wlan0
'''

def hotspot(status):
  command = f'echo "bash networkHandler.sh -h {status}" > networkHandlerPipe'
  if status == 'start' or status == 'stop':
    return subprocess.run(command, shell=True)
  return jsonify('Status must equal either "start" or "stop"')


def restart_wlan0():
  command = 'echo "bash networkHandler.sh -r 1" > networkHandlerPipe'
  return subprocess.run(command, shell=True)


def check_ping():
  response = os.system("ping -c 1 8.8.8.8")
  if response == 0:
      return True
  return False


@app.route('/wifi_creds')
def wifi_creds():
  ssid = request.args.get('ssid', None)
  key = request.args.get('key', None)

  # open wpa_supplicant.conf and write creds to it
  if ssid and key:
    connected = False
    try:
      subprocess.run(f'echo "bash networkHandler.sh -s {ssid} -k {key}" > networkHandlerPipe',
        shell=True,
        capture_output=True)

      restart_wlan0()

      for i in range(10):
        if check_ping():
          message = ['Success: Connection established.']
          message.append('Hotspot will be disabled in 10 seconds.')
          hotspot('stop')
          return jsonify(message=' '.join(message))
        sleep(3)

      return jsonify(message='Failure: unable to establish connection.')

    except:
      return jsonify(message='Unknown error, unable to establish connection.')
  else:
    return jsonify(message='Failure: Wi-fi SSID and Key were not provided')
  

if __name__ == '__main__':
  hotspot('start')
  app.run(debug=True, host='0.0.0.0', port=5001)