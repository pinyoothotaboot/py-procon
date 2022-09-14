import sys
import os
sys.path.append(os.getcwd())
from queue import Queue
from src.mutex import Mutex
import uuid

class DbQueue:
    def __init__(self,name = uuid.uuid1()):
        self.name = name
        self.lock = Mutex()
        self.queue = Queue()
        self.lock.add_lock("queue-{}".format(self.name))
    
    """
        Function : get_name
        @sync
        About : Get name of queue
        Return :
            - name
    """
    def get_name(self) -> str:
        return self.name
    
    """
        Function : get_lock
        @sync
        About : Get mutex lock
        Return :
            - lock
    """
    def get_lock(self):
        return self.lock.get_lock("queue-{}".format(self.name))
    
    """
        Function : is_empty
        @sync
        About : Check empty queue
        Return :
            - True/False
    """
    def is_empty(self) -> bool:
        status = False
        lock = self.get_lock()
        lock.acquire()
        status = self.queue.empty()
        lock.release()
        return status
    
    """
        Function : add
        @sync
        About : Add data to queue
        Param :
            - String : data
        Return : 
            - True/False
    """
    def add(self,data="") -> bool:
        if not data:
            return False
        
        if not isinstance(data,str):
            return False

        status = False
        lock = self.get_lock()
        lock.acquire()
        self.queue.put(data)
        status = True
        lock.release()
        return status
    
    """
        Function : get
        @sync
        About : Get data from queue and pop
        Return :
            - data
    """
    def get(self) -> str:
        data = ""
        lock = self.get_lock()
        lock.acquire()
        data = self.queue.get()
        lock.release()
        return data
    
    """
        Function : clear
        @sync
        About : Clear data in queue
    """
    def clear(self):
        lock = self.get_lock()
        lock.acquire()
        self.queue = None
        self.queue = Queue()
        lock.release()
