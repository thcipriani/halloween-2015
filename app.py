import os
import logging
import requests
import subprocess
import time

from flask import Flask
from flask import request
from flask import jsonify

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Directory this script and the skel directory are in
script_dir = os.path.dirname(os.path.realpath(__file__))

# An easy toggle for when little kids come to the door
dont_scare = os.path.join(script_dir, '.dontscare')

# Some basic setup before hand ensures I don't have to touch
# The button on the hue base station Every. Single. Time.
base_station_ip = '192.168.1.35'
base_station_username = 'newdeveloper'

base_url = 'http://{}/api/{}'.format(base_station_ip, base_station_username)

# Light show each time this application is triggered:
# 1. Flicker the lights
# 2. Kill the lights
# 3. Show intense red light
# 4. Transition back to normal light
light_show = [{
    # Turn the lights red
    'action': 'action',
    'data': [
        '"on": true',
        '"bri": 254',
        '"sat": 254',
        '"hue": 0',
        '"transitiontime": 0',
    ],
    }, {
    # Strobe the lights
    'action': 'transmitsymbol',
    'data': [
        '"symbolselection": '
        '"01010C010101020103010401050106010701080109010A010B010C",'
        '"duration": 1000'
    ],
    'delay': 10
    }, {
    # Make the lights normal again
    'action': 'action',
    'data': [
        '"on": true',
        '"bri": 254',
        '"hue": 11500',
        '"transitiontime": 20',
    ],
    }
]

# Effects for lights #2 and #3 only
lights = [2, 3]

scream_mp3 = os.path.join(script_dir, 'Scream.mp3')


def put(action, data, group=True):
    """Dumb wrapper for requests to the hue bulbs

    :param action: url or group action string
    :param data: json data AS A STRING
    :param group: treat ``action`` as a group action,
                  if False, treat ``action`` as a URL
    """
    if group:
        url = os.path.join(base_url, 'groups', '1', action)
        print url
        print data
    else:
        url = action
    r = requests.put(url, data)
    return r.status_code == requests.codes.ok


def setup_strobe():
    """Setting the pointsymbol for each hue bulb enables a strobe-type effect
    """
    strobe_data = '{"1":"040000FFFF00003333000033330000FFFFFFFFFF"}'

    def lights_path(light):
        return os.path.join(base_url, 'lights', str(light), 'pointsymbol')

    for light in lights:
        put(lights_path(light), data=strobe_data, group=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        with open(os.path.join(script_dir, 'index.html')) as f:
            return f.read()

    if os.path.isfile(dont_scare):
        return 'I don\'t like scaring kids for life'

    # Play scream noise over bluetooth
    subprocess.Popen('/usr/bin/mplayer "%s"' % scream_mp3,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,
                     shell=True)

    for effect in light_show:
        data = ', '.join(effect.get('data'))
        put(effect.get('action'), data='{' + data + '}')
        effect.setdefault('delay', 0)
        time.sleep(effect.get('delay'))
    return 'OK'


@app.route('/scare', methods=['GET', 'POST'])
@app.route('/scare/<int:do_scare>', methods=['POST'])
def scare(do_scare=None):
    """Check if don't scare is true or false or toggle dontscare"""
    scare_exists = os.path.isfile(dont_scare)

    if request.method == 'GET':
        return jsonify(exists=scare_exists)

    logging.info('FUCK {}'.format(do_scare))

    if do_scare is None and scare_exists:
        do_scare = 1
    elif do_scare is None and not scare_exists:
        do_scare = 0

    logging.info('FUCK {}'.format(do_scare))
    if int(do_scare) > 0:
        # Remove the scare file
        if os.path.isfile(dont_scare):
            os.unlink(dont_scare)
            return jsonify(exists=False)
        else:
            return jsonify(exists=True)

    # Touch the scare file
    with open(dont_scare, 'a'):
        os.utime(dont_scare, None)
        return jsonify(exists=True)



if __name__ == '__main__':
    setup_strobe()
    app.run(host='0.0.0.0', port=8000)
