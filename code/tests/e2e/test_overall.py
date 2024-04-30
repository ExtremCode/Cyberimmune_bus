from time import sleep
import pytest
import json
from urllib.request import urlopen, Request

COMMANDS: dict = {
    "cardiologist_sign": "digital_cardiologists_signature",
    "operation": "write_new_commands",
    "commands": {
        "30": 5,
        "40": 4,
        "60": 3,
        "80": 2,
        "100": 1,
        "120": 0,
        "140": 0,
        "160": 0,
        "180": 0,
        "200": 0,
        "220": 0,
        "240": 0,
        "260": 0,
        "280": 0,
        "300": 0
        }
}
IMPULS: int = 2
COMMUN_PROG_POST_URL = "http://localhost:5004/programming"
COMMUN_PROG_GET_URL = "http://localhost:5004/clinic_response"
COMMUN_USER_INTERF_URL = "http://localhost:5005/user_get"
COMMAND_BLOCK_URL = "http://localhost:5007/command_block"
SENSOR_SWITCH_URL = "http://localhost:5008/sensor_switch"


def get_commun_prog_data() -> dict:
    req = Request(COMMUN_PROG_GET_URL,
                  method='GET')
    response = urlopen(req)
    data = json.loads(response.read().decode())
    return data[0]


def post_write_commands() -> dict:
    # send impuls to sensor_switch
    command_request_body = COMMANDS
    headers = {'content-type': 'application/json'}
    req = Request(COMMUN_PROG_POST_URL, 
                  data=json.dumps(command_request_body).encode(),
                headers=headers,
                method='POST')
    resp = urlopen(req)
    return json.loads(resp.read().decode())


def test_post_write_commands():
    resp = post_write_commands()
    assert "operation" in resp
    assert resp["operation"] == "write_new_commands requested"


def test_get_resp_from_write_comm():
    post_write_commands()
    sleep(10)
    data = get_commun_prog_data()
    assert "operation" in data
    assert "result" in data
    assert data["result"] in ["commands_committed", "fail_save_commands"]


@pytest.fixture
def set_commands() -> bool:
    post_write_commands()
    sleep(5)
    resp = get_commun_prog_data()
    if resp != {}:
        return resp["result"] == "commands_committed"
    return False


def send_impuls(impuls=IMPULS):
    impuls_request_body = {
        "impuls": impuls
    }
    headers = {'content-type': 'application/json'}
    req = Request(SENSOR_SWITCH_URL, 
                data=json.dumps(impuls_request_body).encode(),
                headers=headers,
                method='POST')
    resp = urlopen(req)
    return resp


def get_discharge() -> dict:
    req = Request(COMMAND_BLOCK_URL, 
                  method='GET')
    resp = urlopen(req)
    if resp.getcode() == 200:
        resp = resp.read().decode()
        resp = json.loads(resp)
        if resp != []:
            return resp[-1]
    return {
            "result": "fail",
            "value_of_discharge": -1
        }


def test_send_apply_impuls(set_commands):
    if set_commands:
        resp = send_impuls()
        assert resp.getcode() == 200
        sleep(2)
        # try to get value of discharge
        max_retries = 10
        discharge = -1
        while max_retries > 0:
            sleep(1) 
            max_retries -= 1
            res = get_discharge()
            if res["result"] == "success":
                discharge = res["value_of_discharge"]
                break
        assert discharge == COMMANDS["commands"][str(60//IMPULS)]


def get_user_data() -> dict:
    req = Request(COMMUN_USER_INTERF_URL,
                  method='GET')
    response = urlopen(req)
    data = json.loads(response.read().decode())
    if data == []:
        return {}
    return data[0]


def test_get_high_bpm_alerts(set_commands):
    if set_commands:
        resp = send_impuls(0.3)
        assert resp.getcode() == 200
        sleep(2)
        # try to get value of discharge
        max_retries = 10
        res = None
        while max_retries > 0:
            sleep(1)
            max_retries -= 1
            res = get_user_data()
            if res != {}:
                break
        assert "operation" in res and \
                "value" in res and \
                "threshold" in res
        assert res["value"] == 200 and \
                res["threshold"] == 200
