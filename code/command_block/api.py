import multiprocessing
from flask import Flask, request, jsonify
from uuid import uuid4
import threading

host_name = "0.0.0.0"
port = 5007

app = Flask(__name__)             # create an app instance

APP_VERSION = "1.0.2"

_responses_queue: multiprocessing.Queue = None

@app.route("/heart", methods=['GET'])
def get_response():    
    responses = []
    while True:
        try:        
            resp = _responses_queue.get_nowait()
            for item in resp['response']:
                responses.append(item)
        except Exception as _:
            # no events
            break              
    return jsonify(responses)

def start_rest(responses_queue):
    global _responses_queue 
    _responses_queue = responses_queue
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()

# if __name__ == "__main__":        # on running python app.py
#     start_rest()