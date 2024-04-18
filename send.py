#!/usr/bin/env python
import logging
import pika
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info('Init Sender')
logging.info('Sleep 3s')
time.sleep(3)
logging.info('Config credentials to RabbitMQ')
credentials = pika.PlainCredentials('default_user_HyVrwYiHL_OO94aaM_X', 'nV0c9NekNaRY7SJ8R-q4Qr3rntx1FBW2')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='mide.default.svc.cluster.local', credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

message = ' '.join(sys.argv[1:]) or "La tuya!"
channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent
    ))
logging.info(f"[x] Sent {message}")
connection.close()