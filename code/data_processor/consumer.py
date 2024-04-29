# implements Kafka topic consumer functionality


import threading
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
from producer import proceed_to_deliver
import random
import time

TIME = time.time()
LOWER_THRESHOLD = 30 # bpm
ALERT_THRESHOLD = 200 # bpm
UPPER_THRESHOLD = 300 # bpm


def process_impuls(details: dict):
    global LOWER_THRESHOLD, UPPER_THRESHOLD
    # impuls is in range from 0.2 to 2 (300 bpm to 30 bpm)
    # there is a time from the last heartbeat value in seconds
    if details['impuls'] > 0:
        details['impuls'] = 60 // details['impuls']
    else:
        details['impuls'] = random.randint(40, 140)
    
    # fixing wrong heartbeat
    if details['impuls'] > UPPER_THRESHOLD or \
            details['impuls'] < LOWER_THRESHOLD: 
        details['impuls'] = random.randint(40, 140)
    
    # checking the exceeding of ALERT_THRESHOLD bpm
    if ALERT_THRESHOLD <= details['impuls']:
        details['operation'] = 'high_bpm_alert'
        details['high_bpm_value'] = (details['impuls'], ALERT_THRESHOLD)
        details['deliver_to'] = 'command_block'
        proceed_to_deliver(details.copy())


def handle_event(id: str, details: dict):
    # print(f"[debug] handling event {id}, {details}")
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    global TIME, ALERT_THRESHOLD
    try:
        if details['operation'] == 'process_impuls':
            process_impuls(details)
            details['operation'] = 'apply_impuls'
            details['deliver_to'] = 'command_block'
            proceed_to_deliver(details.copy())
            
            details['operation'] = 'write_new_data'
            TIME = time.time()
            details['update_record'] = (TIME, details['impuls'])
            details['deliver_to'] = 'storage'

        elif details['operation'] == 'get_historical_data':
            details['deliver_to'] = 'storage'
        
        elif details['operation'] == 'return_historical_data' or\
                details['operation'] == 'write_new_commands':
            details['deliver_to'] = 'command_block'
        
        proceed_to_deliver(details)
    except Exception as e:
        print(f"[error] failed to handle request: {e}")

def consumer_job(args, config):

    # Create Consumer instance
    data_processor_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(data_processor_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            data_processor_consumer.assign(partitions)

    # Subscribe to topic
    topic = "data_processor"
    data_processor_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = data_processor_consumer.poll(1.0)
            if msg is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                # print("Waiting...")
                pass
            elif msg.error():
                print(f"[error] {msg.error()}")
            else:
                try:
                    _id = msg.key().decode('utf-8')
                    details = json.loads(msg.value().decode('utf-8'))
                    handle_event(_id, details)
                except Exception as e:
                    print(
                        f"[error] malformed event received from topic {topic}: {msg.value()}. {e}")    
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        data_processor_consumer.close()

def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(args, config)).start()
    
if __name__ == '__main__':
    start_consumer(None)
