import json
from constant import *


def cmd_set(payload = {},sock = None , database = None , lock = None):
    sent = 0
    flag = False

    lock.acquire()
    try:
        key = payload["data"]["key"]
        value = payload["data"]["value"]
        topic = payload["topic"]
        database.set(topic,key,value)
        flag = True
    except ValueError:
        pass
    lock.release()

    if flag:
        sent = sock.send(f"{SET} Set data success".encode())
    else:
        sent = sock.send(f"Cannot set data".encode())

    return sent

def cmd_get(payload = {},sock = None , database = None , lock = None):
    sent = 0
    flag = False
    resp = ""

    lock.acquire()
    try:
        key = payload["data"]["key"]
        topic = payload["topic"]
        resp = database.get(topic,key)
        flag = True
    except ValueError:
        pass

    lock.release()

    if flag:
        sent = sock.send(f"{GET} {resp}".encode())
    else:
        sent = sock.send(f"Cannot get data".encode())
    
    return sent

def cmd_push(payload = {},sock = None , database = None , lock = None):
    sent = 0
    flag = False

    lock.acquire()
    try:
        value = payload["data"]["value"]
        topic = payload["topic"]
        database.push(topic,value)
        flag = True
    except ValueError:
        pass

    lock.release()

    if flag:
        sent = sock.send(f"{PUSH} Push data success".encode())
    else:
        sent = sock.send(f"Cannot push data".encode())

    return sent

def cmd_pop(payload = {},sock = None , database = None , lock = None):
    sent = 0
    flag = False
    resp = ""
    lock.acquire()
    try:
        topic = payload["topic"]
        resp = database.pop(topic)
        flag = True
    except ValueError:
        pass

    lock.release()

    if flag:
        sent = sock.send(f"{POP} {resp}".encode())
    else:
        sent = sock.send(f"Cannot pop data".encode())

    return sent

def cmd_range(payload = {},sock = None , database = None , lock = None):
    sent = 0
    flag = False
    resp = []

    lock.acquire()
    try:
        topic = payload["topic"]
        start = payload["data"]["start"]
        stop = payload["data"]["stop"]
        resp = database.list(topic,start,stop)
        flag = True
    except ValueError:
        pass

    lock.release()

    if flag:
        sent = sock.send(f"{RANGE} {resp}".encode())
    else:
        sent = sock.send(f"Cannot list range data".encode())

    return sent


def cmd_publish(payload = {},sock = None , database = None , lock = None):
    sent = 0
    flag = False

    lock.acquire()
    try:
        topic = payload["topic"]
        value = payload["data"]["value"]
        database.publish(topic,value)
        flag = True
    except ValueError:
        pass

    lock.release()

    if flag:
        sent = sock.send(f"{PUBLISH} Publish data success".encode())
    else:
        sent = sock.send(f"Cannot publish data".encode())

    return sent

def cmd_subscribe(payload = {},sock = None ,connection = None):
    sent = 0
    flag = False

    try:
        topics = json.load(payload["topic"])
        connection.subscribe(topics)
        flag = True
    except ValueError:
        pass

    if flag:
        sent = sock.send(f"{SUBSCRIBE} Subscribe topic success".encode())
    else:
        sent = sock.send(f"Cannot subscribe topic ".encode())
    
    return sent

def cmd_unsubscribe(payload = {},sock = None ,connection = None):
    sent = 0
    flag = False

    try:
        topic = payload["topic"]
        connection.unsubscribe(topic)
        flag = True
    except ValueError:
        pass

    if flag:
        sent = sock.send(f"{UNSUBSCRIBE} Unsubscribe topic success".encode())
    else:
        sent = sock.send(f"Cannot unsubscribe topic ".encode())
    
    return sent