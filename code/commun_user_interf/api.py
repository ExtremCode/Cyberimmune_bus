import multiprocessing
from flask import Flask, request, jsonify
from uuid import uuid4
import threading

host_name = "0.0.0.0"
port = 5005

app = Flask(__name__)             # create an app instance

APP_VERSION = "1.0.2"

_requests_queue: multiprocessing.Queue = None
_responses_queue: multiprocessing.Queue = None

@app.route("/user_post", methods=['POST'])
def update():
    content = request.json
    if 'user_sign' not in content:
        return "unauthorized", 401

    req_id = uuid4().__str__()

    try:
        update_details = {
            "id": req_id, # may be worse to remove this key
            "operation": "get_historical_data",
            "user_sign": content['user_sign'],
            "deliver_to": "query_processor"
            }
        _requests_queue.put(update_details)
        print(f"update event: {update_details}")
    except all:
        error_message = f"malformed request {request.data}."
        print(error_message)
        return error_message, 400
    return jsonify({"operation": "update requested", "id": req_id})

@app.route("/user_get", methods=['GET'])
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

def start_rest(requests_queue, responses_queue):
    global _requests_queue, _responses_queue
    _requests_queue = requests_queue
    _responses_queue = responses_queue
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()

if __name__ == "__main__":        # on running python app.py
    start_rest()