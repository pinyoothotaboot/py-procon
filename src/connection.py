import uuid
from mutex import Mutex
from typing import Set

class Connection:
    def __init__(self,socket = None,addr = None,key_selector = None) -> None:
        self.id = uuid.uuid1()
        self.socket = socket
        self.name = self.socket.fileno()
        self.address = addr
        self.key_selector = key_selector

    """
        Function : get_name
        @sync
        About : Get connection name
        Return :
            - name
    """
    def get_name(self):
        return self.name
    
    def get_sock(self):
        return self.socket

    """
        Function : notify
        @sync
        About : Notify payload to client
        Param :
            - String : payload
    """
    def notify(self,payload = "",data = None):
        if not payload:
            return
        
        #self.socket.sendall(payload.encode())
        print("PAYLOAD",payload)
        sent = self.socket.send(payload.encode())
        print("BEFORE SENT",sent,"OUTB",data.outb)
        data.outb = data.outb[sent:]

    def publish(self,payload = ""):
        if not payload:
            return
        
        self.socket.sendall(payload.encode())