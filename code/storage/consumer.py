# implements Kafka topic consumer functionality

import os
import threading
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
from producer import proceed_to_deliver
from time import ctime

STORAGE_PATH = "storage/data/anamnesis.txt"


def write_new_data(details):
    stored = False
    # update_record is tuple like (time, value_of_impuls)
    update_record = "(" + ctime(details['update_record'][0])\
        + ", " + str(details['update_record'][1]) + ")\n"
    try:
        with open(STORAGE_PATH, "a") as f:
            f.write(update_record)
        stored = True
    except Exception as e:
        print(f'[error] failed to store impuls {id} in {os.getcwd()}: {e}')
    return stored


def get_anamnesis(details):
    success = False
    data = []
    try:
        with open(STORAGE_PATH, "r") as f:
            for record in f.readlines():
                data.append(record)
        success = True
    except Exception as e:
        print(f"[error] failed to read anamnesis {details}: {e}")
    return success, data


def handle_event(id: str, details: dict):
    # print(f"[debug] handling event {id}, {details}")
    print(
        f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    try:
        if details['operation'] == 'write_new_data':
            # it's a request to store the impuls
            stored = write_new_data(details)
            if not stored:
                # try to resave 3 times
                for _ in range(3):
                    stored = write_new_data(details)
                    if stored:
                        break
            del details['update_record']
        
        elif details['operation'] == 'get_historical_data':
            # someone requested the anamnesis, get it and send it to the requester
            result, data = get_anamnesis(details)
            if result is True:
                details['operation'] = 'return_historical_data'
                details['historical_data'] = data
            else:
                # try to get 3 times
                for _ in range(3):
                    result, data = get_anamnesis(details)
                    if result is True:
                        details['historical_data'] = data
                        break
                if result is False:
                    details['historical_data'] = []
            details['deliver_to'] = 'data_processor'
            proceed_to_deliver(id, details)
        
    except Exception as e:
        print(f"[error] failed to handle request: {e}")


def consumer_job(args, config):
    # Create Consumer instance
    verifier_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(verifier_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            verifier_consumer.assign(partitions)

    # Subscribe to topic
    topic = "storage"
    verifier_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = verifier_consumer.poll(1.0)
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
                    id = msg.key().decode('utf-8')
                    details = json.loads(msg.value().decode('utf-8'))
                    # print(
                    #     f"[debug] consumed event from topic {topic}: key = {id} value = {details}")
                    handle_event(id, details)
                except Exception as e:
                    print(
                        f"[error] Malformed event received from topic {topic}: {msg.value()}. error: {e}")
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        verifier_consumer.close()


def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(args, config)).start()


if __name__ == '__main__':
    start_consumer(None)
