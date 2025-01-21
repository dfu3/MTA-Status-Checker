# api.py 

from update_data import update, DELAYS
import time
from datetime import datetime
from pprint import pprint as pp
from flask import Flask, jsonify
import threading

app = Flask(__name__)
service_start = datetime.now()

def background_task():
    while True:
        update()
        time.sleep(10)

def calculate_uptime(line_data, service_time):
    total_delayed = line_data['total_delayed']
    if line_data['currently_delayed']:
        total_delayed += (datetime.now() - line_data['delay_start']).total_seconds()
    return 1 - (total_delayed - service_time)

@app.route("/delays")
def delays():
    return jsonify(DELAYS)

@app.route("/uptime/<line>")
def uptime(line):
    uptime = 0
    service_time = (datetime.now() - service_start).total_seconds()
    if line in DELAYS:
        uptime = calculate_uptime(DELAYS[line], service_time)
    else:
        uptime = service_time
    return {
        'Line': line,
        'Uptime': uptime
    } 

@app.route("/status/<line>")
def status(line):
    delayed = False
    if line in DELAYS:
        delayed = DELAYS[line]['currently_delayed']
    return {
        'Line': line,
        'Delayed': delayed
    }

if __name__ == "__main__":
    thread = threading.Thread(target=background_task)
    thread.daemon = True
    thread.start()
    app.run(debug=False)
