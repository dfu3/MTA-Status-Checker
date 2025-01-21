# api.py 

from update_data import update, DELAYS
import time
from datetime import datetime
from flask import Flask, jsonify
import threading

app = Flask(__name__)
service_start = datetime.now()

POLLING_RATE_SECONDS = 10

def background_task():
    """
    Call the update function to internal store to MTA live alert feed
    Runs continuously while flask app is live 
    """
    while True:
        update()
        time.sleep(POLLING_RATE_SECONDS)

def calculate_uptime(line_data, service_time):
    """
    Calculate the uptime percentage of a subway line.
    Uptime is calculated as the proportion of time the line was not delayed
    during the service period.

    Args:
        line_data (dict): A dictionary containing the delay information for the line.

    Returns:
        float: The uptime percentage of the line as a decimal (between 0 and 1).
    """
    total_delayed = line_data['total_delayed']
    if line_data['currently_delayed']:
        total_delayed += (datetime.now() - line_data['delay_start']).total_seconds()
    return 1 - (total_delayed / service_time)

@app.route("/uptime/<line>")
def uptime(line):
    """
    Get the uptime of a specific subway line.

    This endpoint calculates the uptime percentage of a subway line
    by comparing its delayed time to the total service time.

    Args:
        line (str): The subway line ID.

    Returns:
        dict: A JSON response containing the line ID and its uptime percentage.
        Example:
        {
            'Line': 'A',
            'Uptime': 0.95
        }
    """
    uptime = 1
    service_time = (datetime.now() - service_start).total_seconds()
    if line in DELAYS:
        uptime = calculate_uptime(DELAYS[line], service_time)
    return {
        'Line': line,
        'Uptime': uptime
    } 

@app.route("/status/<line>")
def status(line):
    """
    Get the delay status of a specific subway line.

    Args:
        line (str): The subway line ID.

    Returns:
        dict: A JSON response containing the line ID and its delay status.
        Example:
        {
            'Line': 'A',
            'Delayed': True
        }
    """
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
