from mutex import Mutex

class Subscriber:

    def __init__(self):
        self.subscribers = dict()
        self.casheds = dict()
        self.lock = Mutex()
        self.subscriber_id = "subscribers"
        self.cashed_id  = "casheds"
        self.initial_lock()
    
    def get_subscriber_id(self):
        return self.subscriber_id
    
    def get_cashed_id(self):
        return self.cashed_id

    def initial_lock(self):
        self.lock.add_lock(self.get_subscriber_id())
        self.lock.add_lock(self.get_cashed_id())
    
    def subscribe(self,topics = [],connection = None,data = None):
        if not topics or connection is None:
            connection.notify(f"Data has none!.")
            return 

        lock = self.lock.get_lock(self.get_subscriber_id())
        flag = False
        lock.acquire()
        for topic in topics:
            if not topic:
                continue
            if topic not in self.subscribers:
                subscriber = set()
                subscriber.add(connection.get_name())
                self.subscribers[topic] = subscriber
                flag = True
            else:
                self.subscribers[topic].add(connection.get_name())
                flag = True
        lock.release()
        if flag:
            connection.notify(f"Subscribe successed",data)
        else:
            connection.notify(f"Cannot subscribe!.",data)

    def unsubscribe(self,topic="",connection = None,data = None):
        if not topic or connection is None:
            return
        
        lock = self.lock.get_lock(self.get_subscriber_id())
        flag = False
        lock.acquire()

        if topic in self.subscribers:
            if connection.get_name() in self.subscribers[topic]:
                self.subscribers[topic].remove(connection.get_name())
                flag = True
        
        lock.release()

        if flag:
            connection.notify(f"Unsubscribe successed",data)
        else:
            connection.notify(f"Cannot unsubscribe",data)

    def broadcast(self,connection : None , database : None , lock_database : None):
        if connection is None or database is None or lock_database is None:
            return
        
        lock_subscriber = self.lock.get_lock(self.get_subscriber_id())
        lock_cashed = self.lock.get_lock(self.get_cashed_id())

        lock_subscriber.acquire()
        for topic in self.subscribers:
            if connection.get_name() not in self.subscribers[topic]:
                continue

            resp = ""

            lock_cashed.acquire()
            if topic not in self.casheds:
                lock_database.acquire()
                resp = database.subscribe(topic)
                lock_database.release()

                if not resp:
                    continue

                self.casheds[topic] = resp
            else:
                resp = self.casheds[topic]

            lock_cashed.release()

            connection.publish(resp)
        
        lock_subscriber.release()
    
    def clear_cashed(self):
        lock_cashed = self.lock.get_lock(self.get_cashed_id())
        lock_cashed.acquire()
        self.casheds = None
        self.casheds = dict()
        lock_cashed.release()

    def disconnect(self,connection = None):
        if connection is None:
            return
        
        lock = self.lock.get_lock(self.get_subscriber_id())
        lock.acquire()

        for topic in self.subscribers:
            if connection.get_name() in self.subscribers[topic]:
                self.subscribers[topic].remove(connection.get_name())

        lock.release()