# implements Kafka topic consumer functionality

import threading
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
# from producer import proceed_to_deliver
import multiprocessing

_responses_queue: multiprocessing.Queue = None


def handle_event(id: str, details: dict):
    # print(f"[debug] handling event {id}, {details}")
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")

    if details['operation'] == 'return_historical_data' or \
            details['operation'] == 'process_event':
        _responses_queue.put(details)


def consumer_job(args, config, responses_queue=None):
    global _responses_queue
    _responses_queue = responses_queue

    # Create Consumer instance
    commun_prog_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(commun_prog_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            commun_prog_consumer.assign(partitions)

    # Subscribe to topic
    topic = "commun_prog"
    commun_prog_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = commun_prog_consumer.poll(1.0)
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
                    id = msg.key().decode('utf-8')
                    details = json.loads(msg.value().decode('utf-8'))
                    handle_event(id, details)
                except Exception as e:
                    print(
                        f"[error] malformed event received from topic {topic}: {msg.value()}. {e}")    
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        commun_prog_consumer.close()

def start_consumer(args, config, responses_queue):
    threading.Thread(target=lambda: consumer_job(args, config, responses_queue)).start()
    
if __name__ == '__main__':
    start_consumer(None)
