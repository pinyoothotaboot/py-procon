import json
from constant import *


def cmd_set(payload = {},connection = None , database = None , lock = None,data = None):
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
        connection.notify(f"{SET} Set data success",data)
    else:
        connection.notify(f"Cannot set data",data)

def cmd_get(payload = {},connection = None , database = None , lock = None,data = None):
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
        connection.notify(f"{GET} {resp}",data)
    else:
        connection.notify(f"Cannot get data",data)
    

def cmd_push(payload = {},connection = None , database = None , lock = None,data = None):
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
        connection.notify(f"{PUSH} Push data success",data)
    else:
        connection.notify(f"Cannot push data",data)

def cmd_pop(payload = {},connection = None , database = None , lock = None,data = None):
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
        connection.notify(f"{POP} {resp}",data)
    else:
        connection.notify(f"Cannot pop data",data)

def cmd_range(payload = {},connection = None , database = None , lock = None,data = None):
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
        connection.notify(f"{RANGE} {resp}",data)
    else:
        connection.notify(f"Cannot list range data",data)

def cmd_publish(payload = {},connection = None , database = None , lock = None,data=None):
    flag = False
    lock.acquire()
    try:
        topic = payload["topic"]
        value = payload["data"]["value"]
        database.publish(topic,value)
        flag = True
    except ValueError:
        pass
    
    
    if flag:
        connection.notify(f"{PUBLISH} Publish data success",data)
    else:
        connection.notify(f"Cannot publish data",data)
    
    lock.release()

def cmd_subscribe(payload = {},subscriber = None,lock_subscriber = None,connection = None,data=None):
    topics = []
    try:
        topics = json.loads(str(payload["topic"]))
    except Exception as ex:
        topics = []
        connection.notify(f"Cannot subscribe",data)

    if topics:
        lock_subscriber.acquire()
        subscriber.subscribe(topics,connection,data)
        lock_subscriber.release()

def cmd_unsubscribe(payload = {},subscriber = None,lock_subscriber = None,connection = None,data = None):
    topic = ""
    try:
        topic = payload["topic"]
    except Exception as ex:
        topic = ""
        connection.notify(f"Cannot unsubscribe",data)
    
    if topic:
        lock_subscriber.acquire()
        subscriber.unsubscribe(topic,connection,data)
        lock_subscriber.release()

    
    