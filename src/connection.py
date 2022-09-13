import uuid

class Connection:
    def __init__(self,connection = None,addr = None,key_selector = None) -> None:
        self.id = uuid.uuid1()
        self.connection = connection
        self.name = self.connection.fileno()
        self.address = addr
        self.key_selector = key_selector
        self.has_subscriber = False
    
    def get_name(self):
        return self.name