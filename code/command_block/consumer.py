# implements Kafka topic consumer functionality

import os
import threading
from confluent_kafka import Consumer, OFFSET_BEGINNING
import multiprocessing
import json
from producer import proceed_to_deliver

STORAGE_PATH = "command_block/data/commands.txt"
_responses_queue: multiprocessing.Queue = None


def commit_commands(details: dict) -> bool:
    stored = False
    # commands are dictionary where key is integer from 30 to 300
    # that's a lower bound and multiple of 20
    # value is a value of stimul
    commands = details['commands']
    try:
        with open(STORAGE_PATH, "w") as f:
            json.dump(commands, f)
        stored = True
    except Exception as e:
        print(f'[error] failed to store commands in {os.getcwd()}: {e}')
    return stored


def get_commands(details: dict):
    success = False
    commands: dict = None
    try:
        with open(STORAGE_PATH, "r") as f:
            commands = json.load(f)
        success = True
    except Exception as e:
        print(f"[error] failed to read commands {details}: {e}")
    return success, commands


def handle_event(id: str, details: dict):
    # print(f"[debug] handling event {id}, {details}")
    print(
        f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    try:
        required_delivery = False

        if details['operation'] == 'write_new_commands':
            # it's a request to store commands
            stored = commit_commands(details)
            if stored:
                details['deliver_to'] = 'query_processor'
                details['operation'] = 'commands_committed'
            else:
                details['operation'] = 'fail_commands_save'
                details['deliver_to'] = 'query_processor'
            # remove commands before sending further
            try:
                del details['commands']
            finally:
                required_delivery = True
        
        elif details['operation'] == 'high_bpm_alert' or\
                details['operation'] == 'return_historical_data':
            details['deliver_to'] = 'query_processor'
            required_delivery = True
        
        elif details['operation'] == 'apply_impuls':
            result, commands = get_commands(details)
            if result is True:
                try:
                    # search_key is impuls that round to multiple 20
                    search_key = int(max(30, details['impuls'] - details['impuls'] % 20))
                    details['response'] = [{
                        "operation": "discharge_impuls",
                        "result": "success",
                        "discharge value": commands.get(str(search_key))
                    }]
                    _responses_queue.put(details)
                except Exception as e:
                    print(f"[error] failed to get appropriate command: {e}")
            else:
                details['response'] = [{
                        "operation": "discharge_impuls",
                        "result": "fail. There are not any commands."
                }]
                _responses_queue.put(details)
            del details['impuls']
        
        if required_delivery:
            proceed_to_deliver(id, details)
                
    except Exception as e:
        print(f"[error] failed to handle request: {e}")


def consumer_job(args, config, responses_queue=None):
    global _responses_queue
    _responses_queue = responses_queue

    # Create Consumer instance
    command_block_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(command_block_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            command_block_consumer.assign(partitions)

    # Subscribe to topic
    topic = "command_block"
    command_block_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = command_block_consumer.poll(1.0)
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
                        f"[error] Malformed event received from topic {topic}: {msg.value()}. {e}")
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        command_block_consumer.close()


def start_consumer(args, config, responses_queue):
    threading.Thread(target=lambda: consumer_job(args, config, responses_queue)).start()


if __name__ == '__main__':
    start_consumer(None)
