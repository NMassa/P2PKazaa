# coding=utf-8
import socket, os, hashlib, select, sys, time

sys.path.insert(1, '/home/massa/Documenti/PycharmProjects/P2PKazaa')
from peer_server import *
from directory_server import *
import config

class Server(threading.Thread):
    def __init__(self, is_supernode):
        threading.Thread.__init__(self)
        self.host = ''
        self.port_peer = 6000
        self.port_dir = 80
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.sock_lst = []
        self.threads = []
        self.running = None
        self.output_lock = threading.Lock()
        self.dbConnect = MongoConnection()
        self.is_supernode = is_supernode

    def run(self):

        try:
            for item in self.port_dir, self.port_peer:
                self.sock_lst.append(socket.socket(socket.AF_INET6, socket.SOCK_STREAM))
                self.sock_lst[-1].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock_lst[-1].bind((self.host, item))
                self.sock_lst[-1].listen(self.backlog)
                print "Listening on " + str(item)
        except socket.error, (value, message):
            if self.sock_lst[-1]:
                self.sock_lst[-1].close()
                self.sock_lst = self.sock_lst[:-1]
            print 'Could not open socket: ' + message
            sys.exit(1)

        self.running = 1
        while self.running:
            inputready, outputready, exceptready = select.select(self.sock_lst, [], [])

            for s in inputready:
                for item in self.sock_lst:
                    if s == item:
                        port = s.getsockname()[1]

                        if port == self.port_dir:

                            try:
                                # handle the server socket
                                c = Directory_Server(item.accept(), self.dbConnect, self.output_lock, config.my_ipv4,
                                                     config.my_ipv6, config.my_port, config.ttl, self.is_supernode)
                                c.start()
                                self.threads.append(c)
                            except Exception as e:
                                output(self.output_lock, "Server_run_socket: " + Exception + " / " + e.message)

                        elif port == self.port_peer:

                            try:
                                # handle the server socket
                                c = Peer_Server(item.accept(), self.dbConnect, self.output_lock, config.my_ipv4,
                                                config.my_ipv6, config.my_port, config.ttl, self.is_supernode)
                                c.start()
                                self.threads.append(c)
                            except Exception as e:
                                output(self.output_lock, "Server_run_socket: " + Exception + " / " + e.message)

    def stop(self):
        # close all threads

        self.running = 0

        for item in self.sock_lst:
            item.close()

        for c in self.threads:
            c.join()