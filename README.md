# Installation

## Installation rabbitmq operator

```bash
kubectl apply -f "https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml"
```

## Validate

### A new namespace rabbitmq-system. The Cluster Operator deployment is created in this namespace

```bash
kubectl get all -n rabbitmq-system

NAME                                             READY   STATUS    RESTARTS   AGE
pod/rabbitmq-cluster-operator-54f948d8b6-k79kd   1/1     Running   0          2m10s

NAME                                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/rabbitmq-cluster-operator   1/1     1            1           2m10s

NAME                                                   DESIRED   CURRENT   READY   AGE
replicaset.apps/rabbitmq-cluster-operator-54f948d8b6   1         1         1       2m10s
```

### A new custom resource rabbitmqclusters.rabbitmq.com. The custom resource allows us to define an API for the creation of RabbitMQ Clusters.

```cmd
kubectl get customresourcedefinitions.apiextensions.k8s.io

NAME                                             CREATED AT
...
rabbitmqclusters.rabbitmq.com                    2024-01-14T11:12:26Z
...
```

## Create a RabbitMQ cluster called hello-word in the current namespace

```bash
cd Infrastructure\ConfigManagement\Develop\rabitmq
kubectl apply -f cluster.yaml
```

You will also be able to see an instance of the rabbitmqclusters.rabbitmq.com custom resource created.

```bash
kubectl get all

NAME                       READY   STATUS    RESTARTS   AGE
pod/hello-word-server-0   1/1     Running   0          2m

NAME                 TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)              AGE
service/hello-word         ClusterIP   10.75.242.149   <none>        5672/TCP,15672/TCP   2m
service/hello-word-nodes   ClusterIP   None            <none>        4369/TCP,25672/TCP   2m
service/kubernetes   ClusterIP   10.75.240.1     <none>        443/TCP              4h1m

NAME                                  READY   AGE
statefulset.apps/hello-word-server   1/1     2m
```

You will also be able to see an instance of the rabbitmqclusters.rabbitmq.com custom resource created.

```bash
kubectl get rabbitmqclusters.rabbitmq.com

NAME          AGE    STATUS
hello-word          4m1s
```

## View RabbitMQ Logs

```bash
kubectl logs mide-server-0
...

  ##  ##      RabbitMQ 3.12.1
  ##  ##
  ##########  Copyright (c) 2005-2024 Broadcom. All Rights Reserved. The term "Broadcom" refers to Broadcom Inc. and/or its subsidiaries.
  ######  ##
  ##########  Licensed under the MPL 2.0. Website: https://rabbitmq.com

  Erlang:      26.0.1 [jit]
  TLS Library: OpenSSL - OpenSSL 1.1.1u  30 May 2023
  Release series support status: supported

  Doc guides: https://www.rabbitmq.com/documentation.html
  Support:    https://www.rabbitmq.com/contact.html
  Tutorials:  https://www.rabbitmq.com/tutorials.html
  Monitoring: https://www.rabbitmq.com/monitoring.html

...
```

## Access The Management UI

### Get user and password

```bash
...
decode base64
kubectl get secrets mide-default-user -o jsonpath='{.data.username}'
kubectl get secrets mide-default-user -o jsonpath='{.data.password}'
...

kubectl port-forward "service/hello-word" 15672
```

Now we can open localhost:15672 in the browser and see the Management UI. 

## Connect An Application To The Cluster

```bash
kubectl get service hello-word -o jsonpath='{.spec.clusterIP}'

kubectl run perf-test --image=pivotalrabbitmq/perf-test -- --uri amqp://{username}:{password}@{clusterIP}
```

We can now view the perf-test logs by running:

```bash
kubectl logs --follow perf-test
...
id: test-141948-895, time: 16.001s, sent: 25651 msg/s, received: 25733 msg/s, min/median/75th/95th/99th consumer latency: 1346110/1457130/1495463/1529703/1542172 µs
id: test-141948-895, time: 17.001s, sent: 26933 msg/s, received: 26310 msg/s, min/median/75th/95th/99th consumer latency: 1333807/1411182/1442417/1467869/1483273 µs
id: test-141948-895, time: 18.001s, sent: 26292 msg/s, received: 25505 msg/s, min/median/75th/95th/99th consumer latency: 1329488/1428657/1455482/1502191/1518218 µs
id: test-141948-895, time: 19.001s, sent: 23727 msg/s, received: 26055 msg/s, min/median/75th/95th/99th consumer latency: 1355788/1450757/1480030/1514469/1531624 µs
id: test-141948-895, time: 20.001s, sent: 25009 msg/s, received: 25202 msg/s, min/median/75th/95th/99th consumer latency: 1327462/1447157/1474394/1509857/1521303 µs
id: test-141948-895, time: 21.001s, sent: 28487 msg/s, received: 25942 msg/s, min/median/75th/95th/99th consumer latency: 1350527/1454599/1490094/1519461/1531042 µs
...
```

As can be seen, perf-test is able to produce and consume about 25,000 messages per second.

For more info, visit <https://www.rabbitmq.com/kubernetes/operator/quickstart-operator#install-the-rabbitmq-cluster-operator>

## Python - RabbitMQ Work Queues

### Install pika with pip or add it to requirements.txt file

With pip

```bash
python -m pip install pika --upgrade
```

Or add pika to file requirements.txt

```text
# requirements.txt

# RabbitMQ
pika
```

### Send message to RabbitMQ with Python

```Python
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
```

### Worker to consume messages of RabbitMQ with Python

```Python
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
```

For more info, visit <https://www.rabbitmq.com/tutorials/tutorial-two-python>
