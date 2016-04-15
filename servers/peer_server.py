# coding=utf-8
import socket, os, hashlib, select, sys, time

sys.path.insert(1, '/home/massa/Documenti/PycharmProjects/P2PKazaa')
from random import randint
import threading
from dbmodules.dbconnection import *
from commandFile import *

my_ipv4 = "172.030.008.002"
my_ipv6 = "fc00:0000:0000:0000:0000:0000:0008:0002"
my_port = "00080"
my_peer_port = "06000"
TTL = '04'


class Peer_Server(threading.Thread):
    """
        Gestisce le comunicazioni con i peer: LOGI, LOGO, ADDF, DELF, FIND
    """

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

        if cmd[:4] == 'LOGI':
            # “LOGI”[4B].IPP2P[55B].PP2P[5B]
            # “ALGI”[4B].SessionID[16B]
            ipv4 = cmd[4:19]
            ipv6 = cmd[20:59]
            port = cmd[59:64]
            output(self.output_lock, "\nMessagge received: ")
            output(self.output_lock, cmd[:4] + '\t' + ipv4 + '\t' + ipv6 + '\t' + port)

            sessionId = self.dbConnect.insert_session(ipv4, ipv6, port)

            msg = 'ALGI' + sessionId
            # funziona solo se il mantiene la connessione
            conn.send(msg)


        elif cmd[:4] == 'ADFF':
            # “ADFF”[4B].SessionID[16B].Filemd5[32B].Filename[100B]
            sessId = cmd[4:20]
            md5 = cmd[20:52]
            fname = cmd[52:152]
            output(self.output_lock, "\nMessagge received: " + cmd)
            output(self.output_lock, cmd[0:4] + "\t" + sessId + "\t" + md5 + "\t" + fname)

            self.dbConnect.share_file(sessId, md5, fname)

        elif cmd[:4] == 'DEFF':
            # “DEFF”[4B].SessionID[16B].Filemd5[32B]
            sessId = cmd[4:20]
            md5 = cmd[20:52]
            output(self.output_lock, "\nMessagge received: " + cmd)
            output(self.output_lock, cmd[0:4] + "\t" + sessId + "\t" + md5)

            self.dbConnect.remove_file(sessId, md5)

        elif cmd[:4] == 'LOGO':
            # “LOGO”[4B].SessionID[16B]
            # “ALGO”[4B].#delete[3B]
            sessId = cmd[4:20]
            output(self.output_lock, "\nMessagge received: " + cmd)
            output(self.output_lock, cmd[0:4] + "\t" + sessId)

            delete = self.dbConnect.remove_session(sessId)

            msg = 'ALGO' + str(delete).zfill(3)

            conn.send(msg)

        elif cmd[:4] == 'FIND':
            # “FIND”[4B].SessionID[16B].Ricerca[20B]                                         ricevo dai peer loggati
            # “AFIN”[4B].#idmd5[3B].{Filemd5_i[32B].Filename_i[100B].#copy_i[3B].
            # {IPP2P_i_j[55B].PP2P_i_j[5B]}(j=1..#copy_i)}(i=1..#idmd5)                       mando ai peer loggati

            sessId = cmd[4:20]
            searchStr = cmd[20:40]
            output(self.output_lock, "\nMessagge received: ")
            output(self.output_lock, cmd[0:4] + "\t" + sessId + "\t" + searchStr)

            if self.dbConnect.get_session(sessId) is not None:
                pktId = id_generator(16)
                self.dbConnect.insert_file_query(pktId, searchStr)
                supernodes = self.dbConnect.get_supernodes()

                if (len(supernodes) > 0):
                    # “QUER”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B].Ricerca[20B]          mando solo ai supernodi

                    msg = 'QUER' + pktId + my_ipv4 + '|' + my_ipv6 + my_port + TTL + searchStr
                    for supern in enumerate(supernodes):
                        sendTo(supern['ipv4'], supern['ipv6'], supern['port'], msg)

                    # aspetto per 20s le risposte dei supernodi
                    time.sleep(20)

                listResults = list(self.dbConnect.get_file_query(pktId)['results'])

                if listResults is not None:
                    numMd5 = str(len(listResults)).zfill(3)
                    msg = 'AFIN' + numMd5
                    for file in listResults:
                        msg += file['md5'] + file['name'].ljust(100) + str(len(file['peers'])).zfill(3)
                        for peer in file['peers']:
                            msg += peer['ipv4'] + '|' + peer['ipv6'] + peer['port']

                    conn.send(msg)

                else:
                    conn.send('AFIN000')