import sys
sys.path.append('..')
import socket
import threading
import time
from connection import Connection
from mutex import Mutex
from log import Logger
from database import Database
from handle import handle_receive
from subscriber import Subscriber
from constant import PUBLISH
from read_config import initial_config

log = Logger('SERVER').get_logger()

class Server:
    def __init__(self,host="127.0.0.1",port=3456):
        self.config = initial_config()
        self.host = self.config['host']
        self.port = self.config['port']
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.do_running = True
        self.BUFFER_SIZE = self.config['buff_size']
        self.connections = dict()
        self.server_mutex = Mutex()
        self.database = Database()
        self.subscriber = Subscriber()
        self.is_pub = False

        self.client_lock = threading.Lock()
        self.initial_lock()
        self.listen()
    
    def initial_lock(self):
        self.server_mutex.add_lock("connections")
        self.server_mutex.add_lock("clients")
        self.server_mutex.add_lock("database")
        self.server_mutex.add_lock("handle")
        self.server_mutex.add_lock("subscriber")
    
    def get_lock(self,id):
        return self.server_mutex.get_lock(id)
    
    def listen(self):
        try:
            self.sock.bind((self.host, self.port))
            self.sock.listen(self.config['connection'])
        except socket.error as e:
            log.error("Socket server error : {}".format(e))
    
    def add_connection(self,client,address):
        lock = self.get_lock("connections")
        with lock:
            if client.fileno() not in self.connections:
                connection = Connection(client,address)
                self.connections[connection.get_name()] = connection

    def sub_connection(self,client):
        lock = self.get_lock("connections")
        with lock:
            if client.fileno() in self.connections:
                log.warning("Disconnected : {}".format(self.connections[client.fileno()].get_address()))
                self.disconnect_subscriber(self.connections[client.fileno()])
                del self.connections[client.fileno()]
    
    def handle_accept(self):
        while self.do_running:
            client, address = self.sock.accept()
            try:
                if client:
                    self.add_connection(client,address)
                    log.info('Accepted : ' + address[0] + ':' + str(address[1]))
                    thread = threading.Thread(target=self.handle_receive,args=(client,))
                    thread.setDaemon(True)
                    thread.start()
                time.sleep(self.config['handle_accept_sleep'])
            except ConnectionResetError:
                
                self.sub_connection(client)
                client.close()

    def handle_receive(self,client):
        try:
            while self.do_running:
                data = client.recv(self.BUFFER_SIZE)
                if data:
                    lock_database = self.server_mutex.get_lock("database")
                    lock_subscriber = self.server_mutex.get_lock("subscriber")
                    lock_connection = self.server_mutex.get_lock("connections")
                    with lock_connection:
                        if client.fileno() in self.connections:
                            connection = self.connections[client.fileno()]
                            cmd = handle_receive(data,connection,self.database,lock_database,self.subscriber,lock_subscriber,None)
                else:
                    self.sub_connection(client)
                    client.close()

                time.sleep(self.config['handle_receive_sleep'])
            client.close()
        except OSError:
            self.sub_connection(client)
            client.close()
    
    def handle_callback(self,client):
        try:
            while self.do_running:
                if client:
                    print("Send to : {}".format(client))
                    client.sendall(b"Hello World")

                time.sleep(self.config['handle_callback'])
        except OSError:
            self.sub_connection(client)
            client.close()
    
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
    
    def disconnect_subscriber(self,connection = None):
        lock_subscriber = self.server_mutex.get_lock("subscriber")
        lock_subscriber.acquire()
        self.subscriber.disconnect(connection)
        lock_subscriber.release()

    def handle_broadcast(self):
        while self.do_running:
            lock = self.get_lock("connections")
            with lock:
                if not self.connections:
                    continue

                lock_database = self.server_mutex.get_lock("database")
                for con_id in self.connections:
                    connection = self.connections[con_id]
                    if connection:
                        self.subscriber_broadcast(connection,self.database,lock_database)
            self.subscriber_clear_cashed()
            time.sleep(self.config['handle_broadcast'])
    
    def run(self):
        log.info("Start server : {}:{}".format(self.host,self.port))
        thread = threading.Thread(target=self.handle_broadcast)
        thread.setDaemon(True)
        thread.start()
        self.handle_accept()

if __name__ == "__main__":
    try:
        server = Server()
        server.run()
    except KeyboardInterrupt:
        log.info("Stop server..")
        sys.exit()