# coding=utf-8
import hashlib
import os
import socket

import helpers
from Client import Download
from Owner import Owner
from SharedFile import SharedFile
from helpers import connection
from helpers.helpers import *


class Client(object):
    """
    Rappresenta il peer corrente

    Attributes:
        session_id: identificativo della sessione corrente fornito dalla directory
        my_ipv4: indirizzo ipv4 del peer corrente
        my_ipv6: indirizzo ipv6 del peer corrente
        my_port: porta del peer corrente
        dir_ipv4: indirizzo ipv4 della directory
        dir_ipv6: indirizzo ipv6 della directory
        dir_port: porta della directory
        files_list:
        directory: connessione alla directory
    """
    session_id = None
    files_list = []
    directory = None

    def __init__(self, my_ipv4, my_ipv6, my_port, dir_ipv4, dir_ipv6, dir_port, ttl, database):
        """
        Costruttore della classe Peer
        """
        self.my_ipv4 = my_ipv4
        self.my_ipv6 = my_ipv6
        self.my_port = my_port
        self.dir_ipv4 = dir_ipv4
        self.dir_ipv6 = dir_ipv6
        self.dir_port = dir_port
        self.ttl = ttl
        self.dbConnect = database

        # Searching for shareable files
        for root, dirs, files in os.walk("shareable"):
            for file in files:
                file_md5 = helpers.hashfile(open("shareable/" + file, 'rb'), hashlib.md5())
                new_file = SharedFile(file, file_md5)
                self.files_list.append(new_file)

    def login(self):
        """
        Esegue il login alla directory specificata
        """

        print 'Logging in...'
        msg = 'LOGI' + self.my_ipv4 + '|' + self.my_ipv6 + self.my_port
        print 'Login message: ' + msg

        response_message = None
        try:
            self.directory = None
            c = connection.Connection(self.dir_ipv4, self.dir_ipv6, self.dir_port)      # Creazione connessione con la directory
            c.connect()
            self.directory = c.socket

            self.directory.send(msg)                                                    # Richiesta di login
            print 'Message sent, waiting for response...'
            response_message = self.directory.recv(20)                                  # Risposta della directory, deve contenere ALGI e il session id
            print 'Directory responded: ' + response_message
        except socket.error, msg:
            print 'Socket Error: ' + str(msg)
        except Exception as e:
            print 'Error: ' + e.message
        else:
            if response_message is None:
                print 'No response from directory. Login failed'
            else:
                self.session_id = response_message[4:20]
                if self.session_id == '0000000000000000' or self.session_id == '':
                    print 'Troubles with the login procedure.\nPlease, try again.'
                else:
                    print 'Session ID assigned by the directory: ' + self.session_id
                    print 'Login completed'

    def logout(self):
        """
        Esegue il logout dalla directory a cui si è connessi
        """
        print 'Logging out...'
        msg = 'LOGO' + self.session_id
        print 'Logout message: ' + msg

        response_message = None
        try:
            self.directory.send(msg)                                                    # Richeista di logout
            print 'Message sent, waiting for response...'

            response_message = self.directory.recv(7)                                   # Risposta della directory, deve contenere ALGO e il numero di file che erano stati condivisi
            print 'Directory responded: ' + response_message
        except socket.error, msg:
            print 'Socket Error: ' + str(msg)
        except Exception as e:
            print 'Error: ' + e.message
        else:
            if response_message is None:
                print 'No response from directory. Login failed'
            elif response_message[0:4] == 'ALGO':
                self.session_id = None

                number_file = int(response_message[4:7])                                # Numero di file che erano stati condivisi
                print 'You\'d shared ' + str(number_file) + ' files'

                self.directory.close()                                                  # Chiusura della connessione
                print 'Logout completed'
            else:
                print 'Error: unknown response from directory.\n'

    def share(self):
        """
        Aggiunge un file alla directory rendendolo disponibile agli altri peer per il download
        """
        found = False
        while not found:
            print '\nSelect a file to share (\'c\' to cancel):'
            for idx, file in enumerate(self.files_list):
                print str(idx) + ": " + file.name

            try:
                option = raw_input()                                                    # Selezione del file da condividere tra quelli disponibili (nella cartella shareable)
            except SyntaxError:
                option = None

            if option is None:
                print 'Please select an option'
            elif option == "c":
                break
            else:
                try:
                    int_option = int(option)
                except ValueError:
                    print "A number is required"
                else:
                    for idx, file in enumerate(self.files_list):                        # Ricerca del file selezionato
                        if idx == int_option:
                            found = True

                            print "Adding file " + file.name
                            msg = 'ADDF' + self.session_id + file.md5 + file.name.ljust(100)
                            print 'Share message: ' + msg

                            response_message = None
                            try:
                                self.directory.send(msg)                                # Richeista di aggiunta del file alla directory, deve contenere session id, md5 e nome del file
                                print 'Message sent...'

                            except socket.error, msg:
                                print 'Socket Error: ' + str(msg)
                            except Exception as e:
                                print 'Error: ' + e.message

                    if not found:
                        print 'Option not available'

    def remove(self):
        """
        Rimuove un file condiviso nella directory
        """

        found = False
        while not found:
            print "\nSelect a file to remove ('c' to cancel):"
            for idx, file in enumerate(self.files_list):
                print str(idx) + ": " + file.name
            try:
                option = raw_input()                                                    # Selezione del file da rimuovere tra quelli disponibili (nella cartella shareable)
            except SyntaxError:
                option = None
            except Exception:
                option = None

            if option is None:
                print 'Please select an option'
            elif option == "c":
                break
            else:
                try:
                    int_option = int(option)
                except ValueError:
                    print "A number is required"
                else:
                    for idx, file in enumerate(self.files_list):                        # Ricerca del file selezionato
                        if idx == int_option:
                            found = True

                            print "Removing file " + file.name
                            msg = 'DELF' + self.session_id + file.md5
                            print 'Delete message: ' + msg

                            response_message = None
                            try:
                                self.directory.send(msg)                                # Richiesta di rimozione del file dalla directory, deve contenere session id e md5
                                print 'Message sent, waiting for response...'

                            except socket.error, msg:
                                print 'Socket Error: ' + str(msg)
                            except Exception as e:
                                print 'Error: ' + e.message

                    if not found:
                            print 'Option not available'

    def search_file(self):
        """
        Esegue la ricerca di una parola tra i file condivisi nella directory.
        Dai risultati della ricerca sarà possibile scaricare il file.
        Inserendo il termine '*' si richiedono tutti i file disponibili
        """
        print 'Insert search term:'
        try:
            term = raw_input()                                                          # Inserimento del parametro di ricerca
        except SyntaxError:
            term = None
        if term is None:
            print 'Please select an option'
        else:
            print "Searching files that match: " + term

            msg = 'FIND' + self.session_id + term.ljust(20)
            print 'Find message: ' + msg
            response_message = None
            try:
                self.directory.send(msg)                                                # Richeista di ricerca, deve contenere il session id ed il paramentro di ricerca (20 caratteri)
                print 'Message sent, waiting for response...'

                response_message = self.directory.recv(4)                               # Risposta della directory, deve contenere AFIN seguito dal numero di identificativi md5
                                                                                        # disponibili e dalla lista di file e peer che li hanno condivisi
                print 'Directory responded: ' + response_message
            except socket.error, msg:
                print 'Socket Error: ' + str(msg)
            except Exception as e:
                print 'Error: ' + e.message

            if not response_message == 'AFIN':
                print 'Error: unknown response from directory.\n'
            else:
                idmd5 = None
                try:
                    idmd5 = self.directory.recv(3)                                      # Numero di identificativi md5
                except socket.error as e:
                    print 'Socket Error: ' + e.message
                except Exception as e:
                    print 'Error: ' + e.message

                if idmd5 is None:
                    print 'Error: idmd5 is blank'
                else:
                    try:
                        idmd5 = int(idmd5)
                    except ValueError:
                        print "idmd5 is not a number"
                    else:
                        if idmd5 == 0:
                            print "No results found for search term: " + term
                        elif idmd5 > 0:  # At least one result
                            available_files = []

                            try:
                                for idx in range(0, idmd5):                             # Per ogni identificativo diverso si ricevono:
                                                                                        # md5, nome del file, numero di copie, elenco dei peer che l'hanno condiviso

                                    file_i_md5 = self.directory.recv(32)                # md5 dell'i-esimo file (32 caratteri)
                                    file_i_name = self.directory.recv(100).strip()      # nome dell'i-esimo file (100 caratteri compresi spazi)
                                    file_i_copies = self.directory.recv(3)              # numero di copie dell'i-esimo file (3 caratteri)
                                    file_owners = []
                                    for copy in range(0, int(file_i_copies)):                                   # dati del j-esimo peer che ha condiviso l'i-esimo file
                                        owner_j_ipv4 = self.directory.recv(16).replace("|", "")                 # indirizzo ipv4 del j-esimo peer
                                        owner_j_ipv6 = self.directory.recv(39)                                  # indirizzo ipv6 del j-esimo peer
                                        owner_j_port = self.directory.recv(5)                                   # porta del j-esimo peer

                                        file_owners.append(Owner(owner_j_ipv4, owner_j_ipv6, owner_j_port))

                                    available_files.append(SharedFile(file_i_name, file_i_md5, file_owners))

                            except socket.error, msg:
                                print 'Socket Error: ' + str(msg)
                            except Exception as e:
                                print 'Error: ' + e.message

                            if len(available_files) == 0:
                                print "No results found for search term: " + term
                            else:
                                print "Select a file to download ('c' to cancel): "
                                for idx, file in enumerate(available_files):            # visualizza i risultati della ricerca
                                    print str(idx) + ": " + file.name

                                selected_file = None
                                while selected_file is None:
                                    try:
                                        option = raw_input()                            # Selezione del file da scaricare
                                    except SyntaxError:
                                        option = None

                                    if option is None:
                                        print 'Please select an option'
                                    elif option == 'c':
                                        return
                                    else:
                                        try:
                                            selected_file = int(option)
                                        except ValueError:
                                            print "A number is required"

                                file_to_download = available_files[selected_file]       # Recupero del file selezionato dalla lista dei risultati

                                print "Select a peer ('c' to cancel): "
                                for idx, file in enumerate(available_files):            # Visualizzazione la lista dei peer da cui è possibile scaricarlo
                                    if selected_file == idx:
                                        for idx2, owner in enumerate(file.owners):
                                            print str(idx2) + ": " + owner.ipv4 + " | " + owner.ipv6 + " | " + owner.port

                                selected_peer = None
                                while selected_peer is None:
                                    try:
                                        option = raw_input()                            # Selezione di un peer da cui scaricare il file
                                    except SyntaxError:
                                        option = None

                                    if option is None:
                                        print 'Please select an option'
                                    elif option == 'c':
                                        return
                                    else:
                                        try:
                                            selected_peer = int(option)
                                        except ValueError:
                                            print "A number is required"

                                for idx2, owner in enumerate(file_to_download.owners):  # Download del file selezionato
                                    if selected_peer == idx2:
                                        print "Downloading file from: " + owner.ipv4 + " | " + owner.ipv6 + " " + owner.port
                                        self.get_file(self.session_id, owner.ipv4, owner.ipv6, owner.port, file_to_download)
                        else:
                            print "Unknown error, check your code!"

    def get_file(self, session_id, host_ipv4, host_ipv6, host_port, file):
        """
        Effettua il download di un file da un altro peer

        :param session_id: id sessione corrente assegnato dalla directory
        :type session_id: str
        :param host_ipv4: indirizzo ipv4 del peer da cui scaricare il file
        :type host_ipv4: str
        :param host_ipv6: indirizzo ipv6 del peer da cui scaricare il file
        :type host_ipv6: str
        :param host_port: porta del peer da cui scaricare il file
        :type host_port: str
        :param file: file da scaricare
        :type file: file
        :param directory: socket verso la directory (per la segnalazione del download)
        :type directory: object
        """

        c = connection.Connection(host_ipv4, host_ipv6, host_port)  # Inizializzazione della connessione verso il peer
        c.connect()
        download = c.socket

        msg = 'RETR' + file.md5
        print 'Download Message: ' + msg
        try:
            download.send(msg)  # Richiesta di download al peer
            print 'Message sent, waiting for response...'
            response_message = download.recv(
                10)  # Risposta del peer, deve contenere il codice ARET seguito dalle parti del file
        except socket.error as e:
            print 'Error: ' + e.message
        except Exception as e:
            print 'Error: ' + e.message
        else:
            if response_message[:4] == 'ARET':
                n_chunks = response_message[4:10]  # Numero di parti del file da scaricare
                # tmp = 0

                filename = file.name
                fout = open('received/' + filename,
                            "wb")  # Apertura di un nuovo file in write byte mode (sovrascrive se già esistente)

                n_chunks = int(str(n_chunks).lstrip('0'))  # Rimozione gli 0 dal numero di parti e converte in intero

                for i in range(0, n_chunks):
                    if i == 0:
                        print 'Download started...'

                    helpers.update_progress(i, n_chunks,
                                            'Downloading ' + fout.name)  # Stampa a video del progresso del download

                    try:
                        chunk_length = recvall(download, 5)  # Ricezione dal peer la lunghezza della parte di file
                        data = recvall(download, int(chunk_length))  # Ricezione dal peer la parte del file
                        fout.write(data)  # Scrittura della parte su file
                    except socket.error as e:
                        print 'Socket Error: ' + e.message
                        break
                    except IOError as e:
                        print 'IOError: ' + e.message
                        break
                    except Exception as e:
                        print 'Error: ' + e.message
                        break
                fout.close()  # Chiusura file a scrittura ultimata
                print "\n"
                print 'Download completed'
                print 'Checking file integrity...'
                downloaded_md5 = helpers.hashfile(open(fout.name, 'rb'),
                                                  hashlib.md5())  # Controllo dell'integrità del file appena scarcato tramite md5
                if file.md5 == downloaded_md5:
                    print 'The downloaded file is intact'
                else:
                    print 'Something is wrong. Check the downloaded file'
            else:
                print 'Error: unknown response from directory.\n'

    def search_supe(self):
        pktId = id_generator(16)
        msg = "SUPE" + str(pktId) + self.my_ipv4 + "|" + self.my_ipv6 + self.my_port + self.ttl

        print 'Search supernode message: ' + msg

        # Propago a TUTTI i vicini
        if ttl > 1 and visited:
            ttl -= 1
            neighbors = self.dbConnect.get_neighbors()

            if (len(neighbors) > 0):
                # “SUPE”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B]

                for neighbor in enumerate(neighbors):
                    sendTo(neighbor['ipv4'], neighbor['ipv6'], neighbor['port'], msg)





