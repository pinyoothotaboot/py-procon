import sys
sys.path.append('..')
import selectors
import socket
import threading
import time
import types
from connection import Connection
from mutex import Mutex
from log import Logger
from database import Database
from handle import handle_receive
from subscriber import Subscriber

log = Logger('SERVER').get_logger()

class Server:
    def __init__(self,host = "127.0.0.1",port = 3456) -> None:
        self.host = host
        self.port = port
        self.socket_server = socket.socket()
        self.selector = selectors.DefaultSelector()
        self.DO_BLOCKING = False
        self.server_mutex = Mutex()
        self.connections = dict()
        self.clients = list()
        self.database = Database()
        self.subscriber = Subscriber()
        self.BUFFER_SIZE = 2048

        self.initial_socket_server()
        self.initial_selector()
        self.initial_lock()
    
    def initial_socket_server(self):
        try:
            self.socket_server.bind((self.host,self.port))
            self.socket_server.listen()
            self.socket_server.setblocking(self.DO_BLOCKING)
        except Exception as ex:
            log.error("[initial_socket_server()] - Cannot initial socket server {}".format(ex))
            sys.exit(1)
    
    def initial_selector(self):
        try:
            self.selector.register(
                fileobj=self.socket_server,
                events=selectors.EVENT_READ,
                data=None
            )
        except Exception as ex:
            log.error("[initial_selector()] - Cannot register selector {}".format(ex))
            sys.exit(1)
    
    def initial_lock(self):
        self.server_mutex.add_lock("connections")
        self.server_mutex.add_lock("clients")
        self.server_mutex.add_lock("database")
        self.server_mutex.add_lock("handle")
        self.server_mutex.add_lock("subscriber")
    
    def add_connection(self,conn = None,addr = None,key_selector = None):
        if conn is None:
            log.warn("[add_connection()] - Not found connection")
            return
        
        lock = self.server_mutex.get_lock("connections")
        if lock is None:
            log.warn("[add_connection()] - Not found lock")
            return
        
        
        lock.acquire()

        connection = Connection(socket=conn,addr=addr,key_selector=key_selector)
        if connection.get_name() not in self.connections:
            self.connections[connection.get_name()] = connection
        
        lock.release()

    def disconnect_subscriber(self,connection = None):
        lock_subscriber = self.server_mutex.get_lock("subscriber")
        lock_subscriber.acquire()
        self.subscriber.disconnect(connection)
        lock_subscriber.release()

    def delete_connection(self,conn = None):
        if conn is None:
            log.warn("[delete_connection()] - Not found connection")
            return
        
        lock = self.server_mutex.get_lock("connections")
        if lock is None:
            log.warn("[delete_connection()] - Not found lock")
            return

        lock.acquire()
        if conn.fileno() in self.connections:
            connection = self.connections[conn.fileno()]
            self.disconnect_subscriber(connection)
            del self.connections[conn.fileno()]
        
        lock.release()
    
    def add_client(self,data = None):
        if data is None:
            log.warn("[add_client()] - Not found data")
            return

        lock = self.server_mutex.get_lock("clients")
        if lock is None:
            log.warn("[add_client()] - Not found lock")
            return
        lock.acquire()
        self.clients.append(data)
        lock.release()
    
    def on_accept(self,sock = None) -> None:
        if sock is None:
            log.warn("[on_accept()] - Not found socket")
            return

        try:
            conn,addr = sock.accept()
            conn.setblocking(self.DO_BLOCKING)
            log.info("[on_accept()] - Accepted connection : {}".format(conn.getpeername()))
            data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
            self.add_client(data=data)
            self.selector.register(
                fileobj=conn, 
                events=selectors.EVENT_READ | selectors.EVENT_WRITE,
                data=data
            )
            self.add_connection(conn=conn,addr=addr,key_selector = self.selector.select())
        except Exception as ex:
            log.error("[on_accept()] - Cannot accept connection : {}".format(ex))
    
    def on_close(self,conn = None):
        if conn is None:
            log.warn("[on_close()] - Not found connection")
            return

        try:
            log.info("[on_close()] - Disconnect : {}".format(conn.getpeername()))
            self.delete_connection(conn=conn)
            self.selector.unregister(conn)
            conn.close()
        except Exception as ex:
            log.error("[on_close()] - Cannot close connection : {}".format(ex))
    
    def handle_receive(self,sock = None,message = "",data = None):
        lock = self.server_mutex.get_lock("connections")
        if lock is None:
            log.warn("[handle()] - Not found lock")
            return

        lock_database = self.server_mutex.get_lock("database")
        lock_subscriber = self.server_mutex.get_lock("subscriber")

        lock.acquire()
        if sock.fileno() in self.connections:
            connection = self.connections[sock.fileno()]
            handle_receive(message,connection,self.database,lock_database,self.subscriber,lock_subscriber,data)

        #data.outb = data.outb[sent:]
        lock.release()

    def subscriber_broadcast(self,connection,database,lock_database):
        lock_subscriber = self.server_mutex.get_lock("subscriber")
        lock_subscriber.acquire()
        self.subscriber.broadcast(connection,database,lock_database)
        lock_subscriber.release()
    
    def subscriber_clear_cashed(self):
        lock_subscriber = self.server_mutex.get_lock("subscriber")
        lock_subscriber.acquire()
        self.subscriber.clear_cashed()
        lock_subscriber.release()

    def handle_subscriber(self):
        log.info("[handle_subscriber()] - Start handle subscriber..")

        lock_connection = self.server_mutex.get_lock("connections")
        lock_database = self.server_mutex.get_lock("database")
        
        while True:
            lock_connection.acquire()
            for conn_name in self.connections:
                connection = self.connections[conn_name]
                self.subscriber_broadcast(connection,self.database,lock_database)
            lock_connection.release()
            self.subscriber_clear_cashed()
            time.sleep(0.2)

    def on_read(self,key = None,mask = None):
        if (key is None) or (mask is None):
            log.warn("[on_read()] - Not found key or mask")
            return

        try:
            sock = key.fileobj
            data = key.data

            if mask & selectors.EVENT_READ:
                recv_data = sock.recv(self.BUFFER_SIZE)
                if recv_data:
                    data.outb += recv_data
                else:
                    self.on_close(sock)
            
            if mask & selectors.EVENT_WRITE:
                if data.outb:
                    message = data.outb
                    self.handle_receive(sock,message,data)
                    #sent = sock.send(f"Get data successed".encode())
                    #data.outb = data.outb[sent:]

        except ConnectionResetError:
            self.on_close(key.fileobj)
    
    def run(self):
        log.info("[run()] - Start server : {}:{}".format(self.host,self.port))

        thread = threading.Thread(target=self.handle_subscriber)
        thread.setDaemon(True)
        thread.start()

        while True:
            events = self.selector.select(timeout=0.2)
            for key,mask in events:
                if key.data is None:
                    self.on_accept(key.fileobj)
                else:
                    self.on_read(key,mask)

if __name__ == "__main__":
    try:
        server = Server()
        server.run()
    except KeyboardInterrupt:
        log.info("Stoped server..")
        sys.exit()