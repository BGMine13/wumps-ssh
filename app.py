from flask import Flask, jsonify, render_template, request
from wakeonlan import send_magic_packet
from ping3 import ping
from configparser import ConfigParser
import paramiko

app = Flask(__name__)
config = ConfigParser()

# Index route


@app.route('/')
def index():
    config.read('config.ini')
    DEFAULT_HOST = config['DEFAULTS']['DEFAULT_HOST']
    DEFAULT_MAC = config['DEFAULTS']['DEFAULT_MAC']
    DEFAULT_DESTINATION = config['DEFAULTS']['DEFAULT_DESTINATION']
    return render_template('index.jinja',
                           app=app,
                           default_host=DEFAULT_HOST,
                           default_mac=DEFAULT_MAC,
                           default_destination=DEFAULT_DESTINATION)

# Saving route


@app.route('/save', methods=['POST'])
def save():
    DEFAULT_HOST = request.form['hostIP']
    DEFAULT_MAC = request.form['mac-address']
    DEFAULT_DESTINATION = request.form['destination']

    config['DEFAULTS'] = {
        'DEFAULT_HOST': DEFAULT_HOST,
        'DEFAULT_MAC': DEFAULT_MAC,
        'DEFAULT_DESTINATION': DEFAULT_DESTINATION
    }

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    # Note that flask will still have cached the .ini file,
    # so future gets to '/' will be reading from memory until the container restarts.

    # Return a simple JSON response with a 200 status code
    return jsonify({'message': 'Config saved successfully'}), 200

# API endpoints


@app.route('/api/wol/<mac>', methods=['GET'])
def wol(mac):
    try:
        send_magic_packet(mac)
        return jsonify({'result': True})
    except Exception as e:
        return jsonify({'result': False, 'error': str(e)})


@app.route('/api/off', methods=['GET'])
def sol(mac):
    try:
        ssh = paramiko.SSHClient()
        ssh.connect(192.168.1.107, username=media, password=media1)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(sudo shutdown now)
        return jsonify({'result': True})
    except Exception as e:
        return jsonify({'result': False, 'error': str(e)})


@app.route('/api/state/ip/<ip>', methods=['GET'])
def state(ip):
    try:
        response_time = ping(ip, timeout=2)
        if response_time is False:
            return jsonify({'status': 'unknown'})
        if response_time is not None:
            return jsonify({'status': 'awake'})
        else:
            return jsonify({'status': 'asleep'})
    except ping.PingError as e:
        return jsonify({'status': 'unknown', 'error': str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
