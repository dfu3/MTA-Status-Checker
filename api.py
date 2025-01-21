# api.py 

from update_data import update, DELAYS
import time
from datetime import datetime
from pprint import pprint as pp
from flask import Flask, jsonify
import threading

app = Flask(__name__)

def background_task():
    while True:
        update()
        time.sleep(5)

@app.route("/delays")
def delays():
    return jsonify(DELAYS)

if __name__ == "__main__":
    thread = threading.Thread(target=background_task)
    thread.daemon = True
    thread.start()
    app.run(debug=True)
