import sys
import selectors
import socket
import threading
import time
import types
from datetime import datetime
from connection import Connection
from mutex import Mutex
from log import Logger

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
        self.BUFFER_SIZE = 1024

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
    

    def add_connection(self,conn = None,addr = None,key_selector = None):
        if conn is None:
            log.warn("[add_connection()] - Not found connection")
            return
        
        lock = self.server_mutex.get_lock("connections")
        if lock is None:
            log.warn("[add_connection()] - Not found lock")
            return
        
        connection = Connection(connection=conn,addr=addr,key_selector=key_selector)
        lock.acquire()

        if connection.get_name() not in self.connections:
            self.connections[connection.get_name()] = connection
        lock.release()
    
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
                    sent = sock.send(f"You say : {message.decode()}".encode())
                    data.outb = data.outb[sent:]

        except ConnectionResetError:
            self.on_close(key.fileobj)
    
    def run(self):
        log.info("[run()] - Start server : {}:{}".format(self.host,self.port))

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