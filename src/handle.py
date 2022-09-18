from parse import parse_to_json
from constant import *
from command import *

def case_command(payload = {},connection = None,database = None,lock_database = None,data = None):
    cmd = payload["command"]
    if cmd == SET:
        cmd_set(payload,connection,database,lock_database,data)
    elif cmd == GET:
        cmd_get(payload,connection,database,lock_database,data)
    elif cmd == PUSH:
        cmd_push(payload,connection,database,lock_database,data)
    elif cmd == POP:
        cmd_pop(payload,connection,database,lock_database,data)
    elif cmd == RANGE:
        cmd_range(payload,connection,database,lock_database,data)
    elif cmd == PUBLISH:
        cmd_publish(payload,connection,database,lock_database,data)

def handle_receive(message = "",connection = None, database = None,lock_database = None,subscriber = None , lock_subscriber = None,data = None):
    
    packet = parse_to_json(message.decode())
    if packet["status"] != SUCCESS:
        connection.notify(packet["message"],data)
        return ""

    payload = packet["payload"]
    if not payload:
        connection.notify(f"Not found payload!.",data)
        return ""
    
    cmd = payload["command"]
    if cmd == SUBSCRIBE:
        cmd_subscribe(payload,subscriber,lock_subscriber,connection,data)
        return ""
    elif cmd == UNSUBSCRIBE:
        cmd_unsubscribe(payload,subscriber,lock_subscriber,connection,data)
    else:
        case_command(payload,connection,database,lock_database,data)
    
    return cmd
    
