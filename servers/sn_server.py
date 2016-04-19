# coding=utf-8
import socket, os, hashlib, select, sys, time

sys.path.insert(1, '/home/massa/Documenti/PycharmProjects/P2PKazaa')
from random import randint
import threading
from dbmodules.dbconnection import *
from commandFile import *


class SN_Server(threading.Thread):
    """
        Gestisce le comunicazioni con i supernodi: SUPER, QUER, AQUE
    """

    def __init__(self, (client, address), dbConnect, output_lock, my_ipv4, my_ipv6, my_port, ttl, is_supernode):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
        self.dbConnect = dbConnect
        self.output_lock = output_lock
        self.my_ipv4 = my_ipv4
        self.my_ipv6 = my_ipv6
        self.my_port = my_port
        self.ttl = ttl
        self.is_supernode = is_supernode

    def run(self):
        conn = self.client
        cmd = conn.recv(self.size)

        if cmd[:4] == 'SUPE':
            # “SUPE”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B]
            # “ASUP”[4B].Pktid[16B].IPP2P[55B].PP2P[5B]
            pktId = cmd[4:20]
            ipv4 = cmd[20:35]
            ipv6 = cmd[36:75]
            port = cmd[75:80]
            ttl = cmd[80:82]
            output(self.output_lock, "\nMessagge received: ")
            output(self.output_lock, cmd[0:4] + "\t" + pktId + "\t" + ipv4 + "\t" + ipv6 + "\t" +
                   port + "\t" + ttl)
            visited = self.dbConnect.insert_packet(pktId)

            # Propago a TUTTI i vicini
            if ttl > 1 and visited:
                ttl -= 1
                neighbors = self.dbConnect.get_neighbors()

                if (len(neighbors) > 0):
                    # “SUPE”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B]

                    msg = 'SUPE' + pktId + ipv4 + '|' + ipv6 + port + ttl
                    for neighbor in enumerate(neighbors):
                        sendTo(neighbor['ipv4'], neighbor['ipv6'], neighbor['port'], msg)

            # Se sono supernodo rispondo
            if self.is_supernode:
                msg = "ASUP" + pktId + self.my_ipv4 + "|" + self.my_ipv6 + self.my_port
                sendTo(ipv4, ipv6, port, msg)

        elif cmd[:4] == 'ASUP':
            # “ASUP”[4B].Pktid[16B].IPP2P[55B].PP2P[5B]
            pktId = cmd[4:20]
            ipv4 = cmd[20:35]
            ipv6 = cmd[36:75]
            port = cmd[75:80]
            visited = self.dbConnect.insert_packet(pktId)

            if not visited:
                # inserisco il supernodo se non lo conosco altrimenti aggiorno
                self.dbConnect.insert_neighbor(ipv4, ipv6, port, "true")

        elif cmd[:4] == 'QUER':
            # “QUER”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B].Ricerca[20B]            ricevo solo dai supernodi
            pktId = cmd[4:20]
            ipv4 = cmd[20:35]
            ipv6 = cmd[36:75]
            port = cmd[75:80]
            ttl = cmd[80:82]
            searchStr = cmd[82:102]
            output(self.output_lock, "\nMessagge received: ")
            output(self.output_lock, cmd[0:4] + "\t" + pktId + "\t" + ipv4 + "\t" + ipv6 + "\t" +
                   port + "\t" + ttl + "\t" + searchStr)

            visited = self.dbConnect.insert_packet(pktId)
            if ttl >= 1 and not visited:
                files = self.dbConnect.get_files(searchStr)
                if files is not None:
                    msg = 'AQUE' + pktId
                    for file in files:
                        if len(file['peers']) > 0:
                            for peer in file['peers']:
                                msgComplete = msg + peer['ipv4'] + '|' + peer['ipv6'] + peer['port'] + file['md5'] + \
                                              file['name']
                                sendTo(ipv4, ipv6, port, msgComplete)

            if ttl > 1 and not visited:
                ttl -= 1
                supernodes = self.dbConnect.get_supernodes()

                if (len(supernodes) > 0):
                    # “QUER”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B].Ricerca[20B]          mando solo ai supernodi

                    msg = 'QUER' + pktId + ipv4 + '|' + ipv6 + port + ttl + searchStr
                    for supern in enumerate(supernodes):
                        sendTo(supern['ipv4'], supern['ipv6'], supern['port'], msg)

        elif cmd[:4] == 'AQUE':
            # “AQUE”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].Filemd5[32B].Filename[100B]     ricevo solo dai supernodi
            pktId = cmd[4:20]
            ipv4 = cmd[20:35]
            ipv6 = cmd[36:75]
            port = cmd[75:80]
            md5 = cmd[80:102]
            fname = cmd[102:202]
            output(self.output_lock, "\nMessagge received: ")
            output(self.output_lock, cmd[0:4] + "\t" + pktId + "\t" + ipv4 + "\t" + ipv6 + "\t" +
                   port + "\t" + md5 + "\t" + fname)

            self.dbConnect.update_file_query(pktId, md5, fname, ipv4, ipv6, port)
