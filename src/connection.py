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
        self.has_subscriber = False
        self.subscribes = set()
        self.lock = Mutex()

        self.subscribe_id = "subscribes-{}".format(self.id)

        self.initial_lock()
    
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
        Function : initial_lock
        @sync
        About : Initial mutex locking
    """
    def initial_lock(self):
        self.lock.add_lock(self.subscribe_id)
    
    """
        Function : get_lock
        @sync
        About : Get mutex lock by id
        Param :
            - String : id
        Return :
            - lock
    """
    def get_lock(self,id = ""):
        return self.lock.get_lock(id)
    
    """
        Function : subscribe
        @sync
        About : Subscribe topic
        Param :
            - Array : topics
    """
    def subscribe(self,topics = []):
        if not topics:
            return
        
        lock = self.get_lock(self.subscribe_id)
        lock.acquire()
        for topic in topics:
            if topic not in self.subscribes:
                self.subscribes.add(topic)
        lock.release()

    """
        Function : has_subscribe
        @sync
        About : Check subscribe by topic
        Param : 
            - String : topic
        Return :
            - True/False
    """
    def has_subscribe(self,topic = "") -> bool:
        if not topic:
            return False
        
        status = False
        lock = self.get_lock(self.subscribe_id)
        lock.acquire()
        if topic in self.subscribes:
            status = True
        lock.release()

        return status
    
    """
        Function : unsubscribe
        @sync
        About : Unsubscribe topic
        Param :
            - String : topic
    """
    def unsubscribe(self,topic = ""):
        if not topic:
            return
        
        lock = self.get_lock(self.subscribe_id)
        lock.acquire()
        if topic in self.subscribes:
            self.subscribes.remove(topic)
        lock.release()
    
    """
        Function : notify
        @sync
        About : Notify payload to client
        Param :
            - String : payload
    """
    def notify(self,payload = ""):
        if not payload:
            return
        
        self.socket.send(payload.encode())