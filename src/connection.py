import uuid
from mutex import Mutex
from typing import Set

class Connection:
    def __init__(self,socket = None,addr = None) -> None:
        self.id = uuid.uuid1()
        self.socket = socket
        self.name = self.socket.fileno()
        self.address = addr

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
    
    def get_address(self):
        return "{}:{}".format(self.address[0],self.address[1])

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
        
        self.socket.sendall(payload.encode())

    def publish(self,payload = ""):
        if not payload:
            return
        
        self.socket.sendall(payload.encode())