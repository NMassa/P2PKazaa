# coding=utf-8
import socket, os, hashlib, select, sys, time

#sys.path.insert(1, '/home/massa/Documenti/PycharmProjects/P2PKazaa')
from random import randint
import threading
from dbmodules.dbconnection import *
from helpers import *


class Peer_Server(threading.Thread):
    """
        Ascolta sulla porta 6000
        Supernodo: Gestisce le comunicazioni con gli altri i supernodi e l'invio dei file: SUPE, ASUP, QUER, AQUE, RETR
        Peer: Gestisce la propagazione dei pacchetti SUPE a tutti i vicini e l'invio dei file
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
            # TODO: Stampare su GUI

            # “SUPE”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B]
            # “ASUP”[4B].Pktid[16B].IPP2P[55B].PP2P[5B]
            pktId = cmd[4:20]
            ipv4 = cmd[20:35]
            ipv6 = cmd[36:75]
            port = cmd[75:80]
            ttl = int(cmd[80:82])
            output(self.output_lock, "\nMessagge received: ")
            output(self.output_lock, cmd[0:4] + "\t" + pktId + "\t" + ipv4 + "\t" + ipv6 + "\t" +
                   port + "\t" + str(ttl))

            visited = self.dbConnect.insert_packet(pktId)

            # Propago a TUTTI i vicini
            if ttl > 1 and not visited:
                ttl -= 1
                neighbors = self.dbConnect.get_neighbors()

                if (len(neighbors) > 0):
                    # “SUPE”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B]

                    msg = 'SUPE' + pktId + ipv4 + '|' + ipv6 + port + str(ttl).zfill(2)
                    for neighbor in neighbors:
                        sendTo(self.output_lock, neighbor['ipv4'], neighbor['ipv6'], neighbor['port'], msg)

            # Se sono supernodo rispondo
            if self.is_supernode:
                msg = "ASUP" + pktId + self.my_ipv4 + "|" + self.my_ipv6 + str(self.my_port).zfill(5)
                sendTo(self.output_lock, ipv4, ipv6, port, msg)

        elif cmd[:4] == 'ASUP':
            # TODO: Stampare su GUI

            # “ASUP”[4B].Pktid[16B].IPP2P[55B].PP2P[5B]
            pktId = cmd[4:20]
            ipv4 = cmd[20:35]
            ipv6 = cmd[36:75]
            port = cmd[75:80]

            # inserisco il supernodo se non lo conosco altrimenti aggiorno
            self.dbConnect.insert_neighbor(ipv4, ipv6, port, "true")

        elif cmd[:4] == 'QUER':
            # TODO: Stampare su GUI

            # “QUER”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B].Ricerca[20B]            ricevo solo dai supernodi
            pktId = cmd[4:20]
            ipv4 = cmd[20:35]
            ipv6 = cmd[36:75]
            port = cmd[75:80]
            ttl = int(cmd[80:82])
            searchStr = cmd[82:102]
            output(self.output_lock, "\nMessagge received: ")
            output(self.output_lock, cmd[0:4] + "\t" + pktId + "\t" + ipv4 + "\t" + ipv6 + "\t" +
                   port + "\t" + str(ttl) + "\t" + searchStr)

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
                                sendTo(self.output_lock, ipv4, ipv6, port, msgComplete)

            if ttl > 1 and not visited:
                ttl -= 1
                supernodes = self.dbConnect.get_supernodes()

                if (len(supernodes) > 0):
                    # “QUER”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B].Ricerca[20B]          mando solo ai supernodi

                    msg = 'QUER' + pktId + ipv4 + '|' + ipv6 + port + str(ttl).zfill(2) + searchStr
                    for supern in supernodes:
                        sendTo(self.output_lock, supern['ipv4'], supern['ipv6'], supern['port'], msg)

        elif cmd[:4] == 'AQUE':
            # TODO: Stampare su GUI

            # “AQUE”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].Filemd5[32B].Filename[100B]     ricevo solo dai supernodi
            pktId = cmd[4:20]
            ipv4 = cmd[20:35]
            ipv6 = cmd[36:75]
            port = cmd[75:80]
            md5 = cmd[80:112]
            fname = cmd[112:212]
            output(self.output_lock, "\nMessagge received: ")
            output(self.output_lock, cmd[0:4] + "\t" + pktId + "\t" + ipv4 + "\t" + ipv6 + "\t" +
                   port + "\t" + md5 + "\t" + fname)

            self.dbConnect.update_file_query(pktId, md5, fname, ipv4, ipv6, port)
        elif cmd[:4] == 'RETR':
            # TODO: Stampare su GUI

            output(self.output_lock, "\nMessagge received: " + cmd)

            md5Remoto = cmd[4:36]
            file = self.dbConnect.get_file(md5Remoto)
            fileFd = None
            try:
                fileFd = open("fileCondivisi/" + file['name'], "rb")
            except Exception, e:
                output(self.output_lock, 'Error: ' + e.message + "\n")
            else:
                tot_dim = os.stat("fileCondivisi/" + file['name']).st_size  # Calcolo delle dimesioni del file
                n_chunks = int(tot_dim // 1024)  # Calcolo del numero di parti
                resto = tot_dim % 1024  # Eventuale resto
                if resto != 0.0:
                    n_chunks += 1

                fileFd.seek(0, 0)  # Spostamento all'inizio del file

                try:

                    chunks_sent = 0
                    chunk_size = 1024

                    buff = fileFd.read(chunk_size)  # Lettura del primo chunk

                    msg = 'ARET' + str(n_chunks).zfill(
                        6)  # Risposta alla richiesta di download, deve contenere ARET ed il numero di chunks che saranno inviati

                    conn.sendall(msg)

                    output(self.output_lock, '\nUpload Message: ' + msg[0:4] + "\t" + msg[4:10])

                    while len(buff) == chunk_size:  # Invio dei chunks
                        try:
                            msg = str(len(buff)).zfill(5) + buff
                            conn.sendall(msg)  # Invio di
                            chunks_sent += 1

                            update_progress(self.output_lock, chunks_sent, n_chunks,
                                            'Uploading ' + fileFd.name)  # Stampa a video del progresso dell'upload

                            buff = fileFd.read(chunk_size)  # Lettura chunk successivo
                        except IOError:
                            output(self.output_lock,
                                   "Client_run-Error: Connection error due to the death of the peer!!!\n")
                    if len(buff) != 0:  # Invio dell'eventuale resto, se più piccolo di chunk_size

                        msg = str(len(buff)).zfill(5) + buff
                        conn.sendall(msg)

                    output(self.output_lock, "\r\nUpload Completed")

                    fileFd.close()  # Chiusura del file
                except EOFError:
                    output(self.output_lock, "Client_run-Error: You have read a EOF char")