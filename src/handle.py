from parse import parse_to_json
from constant import *
from command import *

def case_command(payload = {},connection = None,database = None,lock_database = None):
    cmd = payload["command"]
    sent = 0
    if cmd == SET:
        sent = cmd_set(payload,connection,database,lock_database)
    elif cmd == GET:
        sent = cmd_get(payload,connection,database,lock_database)
    elif cmd == PUSH:
        sent = cmd_push(payload,connection,database,lock_database)
    elif cmd == POP:
        sent = cmd_pop(payload,connection,database,lock_database)
    elif cmd == RANGE:
        sent = cmd_range(payload,connection,database,lock_database)
    elif cmd == PUBLISH:
        sent = cmd_publish(payload,connection,database,lock_database)

    return sent

def handle_receive(message = "",connection = None, database = None,lock_database = None):
    packet = parse_to_json(message.decode())
    sock = connection.get_sock()
    print("PACKET",packet)
    sent = 0
    if packet["status"] != SUCCESS:
        sent = connection.notify(packet["message"])
        return sent
    
    payload = packet["payload"]
    if not payload:
        sent = connection.notify(f"Not found payload!.")
        return sent
    
    cmd = payload["command"]
    if cmd == SUBSCRIBE:
        sent = cmd_subscribe(payload,connection)
    elif cmd == UNSUBSCRIBE:
        sent = cmd_unsubscribe(payload,connection)
    else:
        sent = case_command(payload,connection,database,lock_database)

    return sent
    
