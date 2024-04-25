import multiprocessing
from flask import Flask, request, jsonify
from uuid import uuid4
import threading

host_name = "0.0.0.0"
port = 5008

app = Flask(__name__)             # create an app instance

APP_VERSION = "1.0.2"

_requests_queue: multiprocessing.Queue = None

@app.route("/heart", methods=['POST'])
def heart():
    content = request.json
    
    req_id = uuid4().__str__()

    try:
        heart_details = {
            "id": req_id,
            "operation": "process_impuls",
            "impuls": content['impuls'],
            "source": "heart",
            "deliver_to": "data_processor"
            }
        _requests_queue.put(heart_details)
        print(f"update event: {heart_details}")
    except all:
        error_message = f"malformed request {request.data}"
        print(error_message)
        return error_message, 400
    return jsonify({"operation": "impuls requested", "id": req_id})

def start_rest(requests_queue):
    global _requests_queue 
    _requests_queue = requests_queue
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()

if __name__ == "__main__":        # on running python app.py
    start_rest()