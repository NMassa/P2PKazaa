import threading
import socket
import pymongo
import os
import string
import random
import select
from dbmodules import dbconnection
from helpers import helpers
from supernodoServer.snserver import output


class Server(threading.Thread):

    def __init__(self):
        super(Server, self).__init__()
        self.host = ''
        self.port = 3000
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []
        self.running = None
        self.output_lock = threading.Lock()
        self.dbConnect = dbconnection.MongoConnection()

    def run(self):
        self.open_socket()
        input = [self.server]
        self.running = 1
        try:
            while self.running:
                inputready, outputready, exceptready = select.select(input, [], [])

                for s in inputready:
                    if s == self.server:
                        try:
                            # handle the server socket
                            c = Client(self.server.accept(), self.dbConnect, self.output_lock)
                            c.start()
                            self.threads.append(c)
                        except Exception as e:
                            output(self.output_lock, "Server_run_socket: " + Exception + " / " + e.message)
        except Exception as e:
            output(self.output_lock, 'Server_run_socket: ' + e.message)

    def stop(self):
        self.running = 0
        for c in self.threads:
            c.join()
        self.server.close()

class Client(threading.Thread):
    cmd = None

    def __init__(self, (client, address), dbConnect, output_lock):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
        self.dbConnect = dbConnect
        self.output_lock = output_lock

    def run(self):
        conn = self.client
        cmd = conn.recv(self.size)

        #LOGI172.030.008.001|fc00:0000:0000:0000:0000:0000:0008:000106000
        if cmd == "LOGI":
            peer_ipv4 = cmd[4-19]
            peer_ipv6 = cmd[20:59]
            peer_port = cmd[59:64]
            result = dbconnection.insert_session(peer_ipv4, peer_ipv6, peer_port)
            if result is None:
                result = "0000000000000000"
            response = 'ALGI' + result
            conn.sendall(response)
            print "AlGI was send!"

        #"LOGOQGF0A8WPRA2XRFZ0"
        elif cmd == 'LOGO':
            session_id = cmd[4:20]
            result = dbconnection.remove_session(session_id)
            result.zfill(3)
            '''
            try:
                result = self.dbConnect.session.find( {"session_id": session_id} )
            except:
                print "error DB insert_one"
            if result:
                result = self.dbConnect.session.delete({"session_id": session_id})
            else:
                print "errore session id non esistente"
            '''

            response = 'ALGO' + result
            print response
            conn.send(response)

        elif cmd == "FIND":
            session_id = cmd[4:20]
            file_name = cmd[20:40].replace(" ", "")
            result = dbconnection.get_files(file_name)
            #md5 = cmd
            #dbconnection.get_file(md5)
            response = "AFIN" + result.lenght
            conn.send(response)

        #"ADFFQGF0A8WPRA2XRFZ0b4dd7f0b0ca6c25dd46cc096e45158ebciao.iso                                                                                            "
        elif cmd == "ADFF":
            session_id = cmd[4:20]
            md5 = cmd[20:52]
            file_name = cmd[52:152].replace(" ", "")
            dbconnection.share_file(session_id, md5, file_name)

        #DEFFQGF0A8WPRA2XRFZ0b4dd7f0b0ca6c25dd46cc096e45158eb
        elif cmd == "DEFF":
            session_id = cmd[4:20]
            md5 = cmd[20:52]
            dbconnection.remove_file(session_id, md5)


