import base64
VERIFIER_SEAL = 'verifier_seal'


def check_operation(id, details):
    authorized = False
    # print(f"[debug] checking policies for event {id}, details: {details}")
    print(f"[info] checking policies for event {id},"
          f" {details['source']}->{details['deliver_to']}: {details['operation']}")
    src = details['source']
    dst = details['deliver_to']
    operation = details['operation']

    if src == 'commun_prog' and dst == 'query_processor' \
            and (operation == 'get_historical_data' or\
                operation == 'write_new_commands'):
        authorized = True

    if src == 'query_processor' and dst == 'commun_prog' \
            and (operation == 'return_historical_data' or\
                operation == 'process_event'):
        authorized = True

    if src == 'commun_user_interf' and dst == 'query_processor' \
            and operation == 'get_historical_data':
        authorized = True

    if src == 'query_processor' and dst == 'commun_user_interf' \
            and (operation == 'return_historical_data' or\
                 operation == 'high_bpm_alert'):
        authorized = True

    if src == 'battery_controller' and dst == 'query_processor' \
            and operation == 'return_battery_stat':
        authorized = True

    if src == 'query_processor' and dst == 'battery_controller' \
            and operation == 'check_battery':
        authorized = True

    if src == 'query_processor' and dst == 'data_processor' \
            and (operation == 'get_historical_data' or\
                operation == 'write_new_commands'):
        authorized = True

    if src == 'command_block' and dst == 'query_processor' \
            and operation == 'commands_committed' or\
                operation == 'fail_commands_save' or\
                operation == 'return_historical_data' or\
                operation == 'high_bpm_alert':
        authorized = True

    if src == 'data_processor' and dst == 'storage' \
            and (operation == 'get_historical_data' or\
                operation == 'write_new_data'):
        authorized = True

    if src == 'storage' and dst == 'data_processor' \
            and operation == 'return_historical_data':
        authorized = True

    if src == 'data_processor' and dst == 'command_block' \
            and (operation == 'return_historical_data' or\
                operation == 'write_new_commands' or\
                operation == 'high_bpm_alert' or\
                operation == 'apply_impuls'):
        authorized = True

    # there is a fictional module (priori doesn't include program code) 
    # due to the fact that 
    # in another case data_processor recieve impuls from data_processor 
    if src == 'sensor_switch' and dst == 'data_processor' \
            and operation == 'process_impuls':
        authorized = True
    
    # kea - Kafka events analyzer - an extra service for internal monitoring,
    # can only communicate with itself
    if src == 'kea' and dst == 'kea' \
            and (operation == 'self_test' or operation == 'test_param'):
        authorized = True

    return authorized


def check_payload_seal(payload):
    try:
        p = base64.b64decode(payload).decode()
        if p.endswith(VERIFIER_SEAL):
            print('[info] payload seal is valid')
            return True
    except Exception as e:
        print(f'[error] seal check error: {e}')
        return False
