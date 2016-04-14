# coding=utf-8
import socket, json, os, hashlib, select, sys, time
sys.path.insert(1,'/home/andrei/PycharmProjects/P2PKazaa')
from random import randint
import threading
from dbmodules.dbconnection import *
from commandFile import *


#my_ipv4 = "172.030.008.004"
#my_ipv6 = "fc00:0000:0000:0000:0000:0000:0008:0004"
#my_port = "00080"

my_ipv4 = "127.000.000.001"
my_ipv6 = "::1"
my_port = "03000"

def output(lock, message):
    lock.acquire()
    print message
    lock.release()

class Client(threading.Thread):
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

        if cmd[:4] == 'SUPE':
            #“SUPE”[4B].Pktid[16B].IPP2P[39B].PP2P[5B].TTL[2B]
            #“ASUP”[4B].Pktid[16B].IPP2P[39B].PP2P[5B]
            pass
            """
            output(self.output_lock, "\nMessagge received: ")
            output(self.output_lock,
                   cmd[0:4] + "\t" + cmd[4:20] + "\t" + cmd[20:35] + "\t" + cmd[36:75] + "\t" + cmd[76:80] + "\t" +
                                                                                    cmd[80:82])
            msg = 'ASUP' + cmd[4:20] + my_ipv4 + '|' + my_ipv6 + my_port

            sendAckSuper(msg)
            """

        elif cmd[:4] == 'LOGI':
            #“LOGI”[4B].IPP2P[39B].PP2P[5B]
            #“ALGI”[4B].SessionID[16B]
            output(self.output_lock, "\nMessagge received: ")
            output(self.output_lock,
                   cmd[0:4] + "\t" + cmd[4:20] + "\t" + cmd[20:35] + "\t" + cmd[36:75] + "\t" + cmd[75:80])

            sessionId = logon(cmd)

            msg = 'ALGI' + sessionId

            sendAckLogon(msg)


        elif cmd[:4] == 'ADFF':
            #“ADFF”[4B].SessionID[16B].Filemd5[16B].Filename[100B]
            output(self.output_lock, "\nMessagge received: " + cmd)
            output(self.output_lock, cmd[0:4] + "\t" + cmd[4:20] + "\t" + cmd[20:52] + "\t" + cmd[52:102])

            addFile(cmd)

        elif cmd[:4] == 'DEFF':
            #“DEFF”[4B].SessionID[16B].Filemd5[16B]
            output(self.output_lock, "\nMessagge received: " + cmd)
            output(self.output_lock, cmd[0:4] + "\t" + cmd[4:20] + "\t" + cmd[20:52])

            removeFile(cmd)

        elif cmd[:4] == 'LOGO':
            #“LOGO”[4B].SessionID[16B]
            #“ALGO”[4B].#delete[3B]
            output(self.output_lock, "\nMessagge received: " + cmd)
            output(self.output_lock, cmd[0:4] + "\t" + cmd[4:20])

            delete = logout(cmd)

            msg = 'ALGO' + delete

            sendAckLogout(msg)

        elif cmd[:4] == 'QUER':
            #“QUER”[4B].Pktid[16B].IPP2P[39B].PP2P[5B].TTL[2B].Ricerca[20B]            ricevo solo dai supernodi
            output(self.output_lock, "\nMessagge received: ")
            output(self.output_lock, cmd[0:4] + "\t" + cmd[4:20] + "\t" + cmd[20:35] + "\t" + cmd[36:75] + "\t" +
                                                                   cmd[76:80] + "\t" + cmd[80:82] + "\t" + cmd[82:102])

            ttl = cmd[80]
            # recupero tutti i file che corrispondono al termine di ricerca e li mando al supernodo che ha fatto la query
            files = retrieveFiles(cmd[82:102])

            sendAckQuery(cmd, files)

        elif cmd[:4] == 'AQUE':
            #“AQUE”[4B].Pktid[16B].IPP2P[39B].PP2P[5B].Filemd5[16B].Filename[100B]     ricevo solo dai supernodi
            output(self.output_lock, "\nMessagge received: ")
            output(self.output_lock, cmd[0:4] + "\t" + cmd[4:20] + "\t" + cmd[20:35] + "\t" + cmd[36:75] + "\t" +
                                                                   cmd[76:80] + "\t" + cmd[80:102] + "\t" + cmd[102:202])

            insertAckQuery(cmd)

        elif cmd[:4] == 'FIND':
            #“FIND”[4B].SessionID[16B].Ricerca[20B]                                    ricevo dai peer loggati
            #“AFIN”[4B].#idmd5[3B].{Filemd5_i[16B].Filename_i[100B].#copy_i[3B].
            #{IPP2P_i_j[39B].PP2P_i_j[5B]}(j=1..#copy_i)}(i=1..#idmd5)                 mando ai peer loggati
            output(self.output_lock, "\nMessagge received: ")
            output(self.output_lock, cmd[0:4] + "\t" + cmd[4:20] + "\t" + cmd[20:40])

            if loggedIn(cmd[4:20]):
                sendQuery(cmd[20:40])

            # aspetto 20s che IL SUPERNODO interrogato
            time.sleep(20)

            # se c'è ancora la connessione col peer che ha fatto la ricerca
            sendAckFind(cmd)



class Server(threading.Thread):
    def __init__(self):
        super(Server, self).__init__()
        self.host = ''
        self.port = 6000
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []
        self.running = None
        self.output_lock = threading.Lock()
        self.dbConnect = MongoConnection()

    def open_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            output(self.output_lock, 'Listening on ' + str(self.port))
        except socket.error, (value, message):
            if self.server:
                self.server.close()
            output(self.output_lock, "Server_open_socket: Could not open socket: " + message)
            sys.exit(1)
        except socket.error, (value, message):
            if self.server:
                self.server.close()
                output(self.output_lock, "Server_open_socket-Error: Could not open socket: " + message)
            sys.exit(1)

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
        # close all threads

        self.running = 0

        for c in self.threads:
            c.join()

        self.server.close()


s = Server()
s.start()