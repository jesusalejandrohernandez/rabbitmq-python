#!/usr/bin/env python
import logging
import pika
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info('Init Worker')
logging.info('Config credentials to RabbitMQ')
credentials = pika.PlainCredentials('default_user_HyVrwYiHL_OO94aaM_X', 'nV0c9NekNaRY7SJ8R-q4Qr3rntx1FBW2')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='mide.default.svc.cluster.local', credentials=credentials))
channel = connection.channel()

logging.info('Queue declare')
channel.queue_declare(queue='task_queue', durable=True)
logging.info('[*] Waiting for messages.')

def callback(ch, method, properties, body):
    logging.info(f"[x] Received {body.decode()}")
    time.sleep(body.count(b'.'))
    logging.info("[x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', auto_ack=False, on_message_callback=callback)

logging.info('Start consuming')
channel.start_consuming()
