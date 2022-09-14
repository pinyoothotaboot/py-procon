from parse import parse_to_json
from constant import *
from command import *

def case_command(payload = {},sock = None,database = None,lock_database = None):
    cmd = payload["command"]
    sent = 0
    if cmd == SET:
        sent = cmd_set(payload,sock,database,lock_database)
    elif cmd == GET:
        sent = cmd_get(payload,sock,database,lock_database)
    elif cmd == PUSH:
        sent = cmd_push(payload,sock,database,lock_database)
    elif cmd == POP:
        sent = cmd_pop(payload,sock,database,lock_database)
    elif cmd == RANGE:
        sent = cmd_range(payload,sock,database,lock_database)
    elif cmd == PUBLISH:
        sent = cmd_publish(payload,sock,database,lock_database)

    return sent

def handle_receive(message = "",connection = None, database = None,lock_database = None):
    packet = parse_to_json(message.decode())
    sock = connection.get_sock()
    print("PACKET",packet)
    sent = 0
    if packet["status"] != SUCCESS:
        sent = sock.send(packet["message"].encode())
        return sent
    
    payload = packet["payload"]
    if not payload:
        sent = sock.send(f"Not found payload!.".encode())
        return sent
    
    cmd = payload["command"]
    if cmd == SUBSCRIBE:
        sent = cmd_subscribe(payload,sock,connection)
    elif cmd == UNSUBSCRIBE:
        sent = cmd_unsubscribe(payload,sock,connection)
    else:
        sent = case_command(payload,sock,database,lock_database)

    return sent
    
