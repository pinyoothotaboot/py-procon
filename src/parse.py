
from typing import List,Dict
from constant import *

def is_number(num_str = "") -> bool:
    try:
        num = int(num_str)
        return True
    except:
        return False

def packet(payload = {},message = "",status = SUCCESS) -> Dict:
    return {
        "status" : status,
        "message" : message,
        "payload" : payload
    }

def command(cmd = "",topic = "",data = {}) -> Dict:
    return {
        "command" : cmd,
        "topic" : topic,
        "data" : data
    }

def map_packet(data_list  = []) -> Dict:
    cmd = data_list[0]
    topic = data_list[1]

    if  (cmd == PUBLISH ) and len(data_list) > 2:
        return packet(
            command(cmd,topic,{"key" : "","value" : data_list[2]}),
            "Created publish packet"
        )
    elif (cmd == SUBSCRIBE):
        return packet(
            command(cmd,topic),
            "Created subscribe packet"
        )
    elif (cmd == UNSUBSCRIBE):
        return packet(
            command(cmd,topic),
            "Created unsubscribe packet"
        )
    elif (cmd == SET) and len(data_list) > 3:
        if ' ' in data_list[2]:
            return packet({},"Key has space character!.",ERROR)

        return packet(
            command(cmd,topic,{"key" : data_list[2],"value" : data_list[3]}),
            "Created set packet"
        )
    elif (cmd == GET) and len(data_list) > 2:
        if ' ' in data_list[2]:
            return packet({},"Key has space character!.",ERROR)

        return packet(
            command(cmd,topic,{"key" : data_list[2],"value" : ""}),
            "Created get packet"
        )
    elif (cmd == PUSH) and len(data_list) > 2:
        return packet(
            command(cmd,topic,{"key" : "","value" : data_list[2]}),
            "Created push packet"
        )
    elif (cmd == POP):
        return packet(
            command(cmd,topic),
            "Created pop packet"
        )
    elif (cmd == RANGE) and len(data_list) > 3:
        start = data_list[2]
        stop = data_list[3]
        if not is_number(start) or not is_number(stop):
            return packet({},"Range start or stop are not number!.",ERROR)
        
        return packet(
            command(cmd,topic,{"key": "","value" : "","start" : start,"stop" : stop}),
            "Created range packet"
        )
    else:
        return packet({},"Cannot create command packet!.",ERROR)

"""
    Function : parse_to_json
    @sync
    About : Convert string payload to json format
    Param :
        - String : data
    Pattern :
        - <PUBLISH<>topic<>hahahahahahaha>
        - <SUBSCRIBE<>["topic"]>
        - <UNSUBSCRIBE<>topic>
        - <SET<>topic<>key<>payload>
        - <GET<>topic<>key>
        - <PUSH<>topic<>payload>
        - <POP<>topic>
        - <RANGE<>topic<>start<>stop>
    Return :
        {
            command : PUSH,
            data : {
                key : ,
                value : 
            }
        }
"""
def parse_to_json(data ="") -> Dict:
    if not data:
        return packet({},"Data is empty!.",WARNING)

    # Check header (<) and tail (>)
    if  ((data[0] != '<') or (data[-1] != '>')):
        return packet({},"Data has not pattern format!.",ERROR)
    
    # Delete header (<) and tail (>)
    data = data[1:-1]
    if not data:
        return packet({},"Data is empty!.",WARNING)

    # Split '<>' from data
    data_list = data.split("<>")
    if len(data_list) < 2:
        return packet({},"Data out of pattern!.",ERROR)
    
    # Check command
    if data_list[0] not in commands:
        return packet({},"Command has not matched!.",ERROR)
    
    # Check space in topic
    if ' ' in data_list[1]:
        return packet({},"Topic has space character!.",WARNING)
        
    return map_packet(data_list)

def parse_to_string(topic = "",key ="",data ="") -> str:
    pass

