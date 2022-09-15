import json
from constant import *


def cmd_set(payload = {},connection = None , database = None , lock = None):
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
        sent = connection.notify(f"{SET} Set data success")
    else:
        sent = connection.notify(f"Cannot set data")

    return sent

def cmd_get(payload = {},connection = None , database = None , lock = None):
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
        sent = connection.notify(f"{GET} {resp}")
    else:
        sent = connection.notify(f"Cannot get data")
    
    return sent

def cmd_push(payload = {},connection = None , database = None , lock = None):
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
        sent = connection.notify(f"{PUSH} Push data success")
    else:
        sent = connection.notify(f"Cannot push data")

    return sent

def cmd_pop(payload = {},connection = None , database = None , lock = None):
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
        sent = connection.notify(f"{POP} {resp}")
    else:
        sent = connection.notify(f"Cannot pop data")

    return sent

def cmd_range(payload = {},connection = None , database = None , lock = None):
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
        sent = connection.notify(f"{RANGE} {resp}")
    else:
        sent = connection.notify(f"Cannot list range data")

    return sent


def cmd_publish(payload = {},connection = None , database = None , lock = None):
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
        sent = connection.notify(f"{PUBLISH} Publish data success")
    else:
        sent = connection.notify(f"Cannot publish data")

    return sent

def cmd_subscribe(payload = {},connection = None):
    sent = 0
    flag = False

    try:
        topics = json.load(payload["topic"])
        connection.subscribe(topics)
        flag = True
    except ValueError:
        pass

    if flag:
        sent = connection.notify(f"{SUBSCRIBE} Subscribe topic success")
    else:
        sent = connection.notify(f"Cannot subscribe topic ")
    
    return sent

def cmd_unsubscribe(payload = {},connection = None):
    sent = 0
    flag = False

    try:
        topic = payload["topic"]
        connection.unsubscribe(topic)
        flag = True
    except ValueError:
        pass

    if flag:
        sent = connection.notify(f"{UNSUBSCRIBE} Unsubscribe topic success")
    else:
        sent = connection.notify(f"Cannot unsubscribe topic ")
    
    return sent