# implements Kafka topic consumer functionality

import threading
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
from producer import proceed_to_deliver

CHARGE_LEVEL = 100


def handle_event(id: str, details: dict):    
    # print(f"[debug] handling event {id}, {details}")
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    try:
        global CHARGE_LEVEL
        required_delivery = False

        if details['operation'] == 'return_battery_stat':
            CHARGE_LEVEL = details['charge_level']
            del details['charge_level']
        
        elif details['operation'] == 'high_bpm_alert':
            details['response'] = [{
                "operation": "high_bpm_alert",
                "value": details['high_bpm_value'][0],
                "threshold": details['high_bpm_value'][1]
                }]
            details['deliver_to'] = 'commun_user_interf'
            try:
                del details['high_bpm_value']
            finally:
                required_delivery = True
        
        elif details['operation'] == 'return_historical_data':
            if 'cardiologist_sign' in details:
                details['deliver_to'] = 'commun_prog'
                details['operation'] = 'return_historical_data'
                details['response'] = [{
                    "operation": "return_historical_data",
                    "result": 
                        "success" if details['historical_data'] != []\
                        else "fail",
                    "data": details['historical_data'],
                    "charge_level": CHARGE_LEVEL
                }]
                try:
                    del details['cardiologist_sign']
                    del details['historical_data']
                finally:
                    proceed_to_deliver(details.copy())
            
            if 'user_sign' in details:
                details['deliver_to'] = 'commun_user_interf'
                details['operation'] = 'return_historical_data'
                details['response'] = [{
                    "operation": "return_historical_data",
                    "result": 
                        "success" if details['historical_data'] != []\
                        else "fail",
                    "data": details['historical_data'],
                    "charge_level": CHARGE_LEVEL
                }]
                try:
                    del details['user_sign']
                    if 'historical_data' in details:
                        del details['historical_data']
                finally:
                    required_delivery = True

        elif details['operation'] == 'commands_committed' or\
                details['operation'] == 'fail_commands_save':
            details['response'] = [{
                'operation': 'write_new_commands',
                'result': details['operation']
            }]
            details['operation'] = 'process_event'
            details['deliver_to'] = 'commun_prog'
            required_delivery = True

        # only reliable cardiologist and user can get historical data
        elif details['operation'] == 'get_historical_data':
            # firstly check that sign is in details
            if 'cardiologist_sign' in details:
                if details['cardiologist_sign'] == 'digital_cardiologists_signature':
                    details['deliver_to'] = 'data_processor'
                    proceed_to_deliver(details.copy())
            elif 'user_sign' in details:
                if details['user_sign'] == 'digital_users_signature':
                    details['deliver_to'] = 'data_processor'
                    proceed_to_deliver(details.copy())
            details['operation'] = 'check_battery'
            details['deliver_to'] = 'battery_controller'
            required_delivery = True

        # only a reliable cardiologist can write new commands
        elif details['operation'] == 'write_new_commands':
            if 'cardiologist_sign' in details:
                if details['cardiologist_sign'] == 'digital_cardiologists_signature':
                    details['deliver_to'] = 'data_processor'
                    del details['cardiologist_sign']
                    required_delivery = True
                    
        if required_delivery:
            proceed_to_deliver(details)
    except Exception as e:
        print(f"[error] failed to handle request: {e}")

def consumer_job(args, config):
    # Create Consumer instance
    query_processor_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(query_processor_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            query_processor_consumer.assign(partitions)

    # Subscribe to topic
    topic = "query_processor"
    query_processor_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = query_processor_consumer.poll(1.0)
            if msg is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                # print("Waiting...")
                pass
            elif msg.error():
                print(f"[error] {msg.error()}")
            else:
                # Extract the (optional) key and value, and print.
                try:
                    _id = msg.key().decode('utf-8')
                    details_str = msg.value().decode('utf-8')
                    # print("[debug] consumed event from topic {topic}: key = {key:12} value = {value:12}".format(
                        # topic=msg.topic(), key=id, value=details_str))
                    handle_event(_id, json.loads(details_str))
                except Exception as e:
                    print(
                        f"Malformed event received from topic {topic}: {msg.value()}. {e}")
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        query_processor_consumer.close()


def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(args, config)).start()


if __name__ == '__main__':
    start_consumer(None)
