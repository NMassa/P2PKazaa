# coding=utf-8
from pymongo import MongoClient
from helpers.helpers import *
from helpers.ipaddr import *
from Client import Peer
import re


class MongoConnection():
    def __init__(self, host="localhost", port=27017, db_name='kazaa', conn_type="local", username='', password=''):
        self.host = host
        self.port = port
        try:
            self.conn = MongoClient()
            self.db = self.conn[db_name]

        except Exception as e:
            print "Could not connect to server: " + e.message

        # se sono un peer
        if True:
            # Database initialization
            self.initialize_files()

    def initialize_files(self):
        """
            Inserisce nel database i file dalla cartella fileCondivisi
        """
        files = get_shareable_files()
        for file in files:
            try:
                found = self.db.files.find_one({"md5": file['md5']})
                if found is None:
                    self.db.files.insert_one({
                        "name": file['name'].strip(" "),
                        "md5": file['md5'],
                        "peers": []
                    })
            except Exception, e:
                print "initialize_files: " + e.message

    def get_file(self, md5):
        """
            Restituisce un file in base all'md5
        """
        cursor = self.db.files.find_one({"md5": md5})
        if cursor is None:
            # TODO: modificare print
            print "error"
        else:
            return cursor

    def get_files(self):
        """
            Restituisce tutti i file
        """
        files = self.db.files.find()
        return list(files)

    def get_files(self, query_str):
        """
            Restituisce i file il cui nome comprende la stringa query_str
        """
        regexp = re.compile(query_str, re.IGNORECASE)
        files = self.db.files.find({"name": {"$regex": regexp}})

        return list(files)

    def share_file(self, session_id, md5, name):
        """
            Aggiugne alla directory un file condiviso da un peer
        """
        file = self.db.files.find_one({"md5": md5, "peers": {"$elemMatch": {"session_id": session_id}}})

        if file is not None:
            print "already shared this file"
            #TODO: return error
        else:
            file = self.db.files.find_one({"md5": md5})

            if file is None:
                # prima volte che qualcuno condivide il file
                self.db.files.insert_one({"md5": md5,
                                          "name": name.strip(" "),
                                          "peers": [
                                              {
                                                  "session_id": session_id
                                              }
                                          ]})
            else:
                # aggiorno il file esistente
                self.db.files.update({"md5": md5},
                                     {"$push":
                                         {
                                             "peers" : {"session_id": session_id}
                                         }
                                     })

    def remove_file(self, session_id, md5):
        """
            Rimuove dalla directory un file condiviso da un peer
        """
        file = self.db.files.find_one({"md5": md5, "peers": {"$elemMatch": {"session_id": session_id}}})

        if file is None:
            print "file doesn't exist"
            # TODO: return error
        else:
            # rimuovo il session_id dalla lista dei peer
            peers = list(file['peers'])
            result = []

            for peer in peers:
                if peer['session_id'] != session_id:  # se il session id è diverso lo mantengo nella lista
                    result.append(peer)

            if not result:
                # era l'ultimo a condividerlo quindi lo elimino
                self.db.files.remove({"md5": md5})
            else:
                file['peers'] = result
                self.db.files.update(
                    {"md5": file['md5']},
                    {
                        "$set": {"peers": file['peers']}
                    })

    def get_neighbors(self):
        """
            Restituisce tutti i vicini
        """
        cursor = self.db.neighbors.find()
        return list(cursor)

    def get_neighbors(self, my_ipv4, my_ipv6):
        """
            Restituisce un vicino
        """
        cursor = self.db.neighbors.find({"ipv4": {"$ne": my_ipv4},
                                         "ipv6": {"$ne": my_ipv6}
                                         })
        neighbors = []
        for document in cursor:
            neighbors.append({
                "ipv4": document['ipv4'],
                "ipv6": document['ipv6'],
                "port": document['port']
            })

        return neighbors

    def insert_neighbor(self, ipv4, ipv6, port):
        """
            Inserisce un vicino
        """
        cursor = self.db.neighbors.find({"ipv4": IPv4Address(ipv4).exploded,
                                         "ipv6": IPv6Address(ipv6).exploded,
                                         "port": str(port).zfill(5)
                                         })

        if cursor is None:
            self.db.neighbors.insert_one({"ipv4": IPv4Address(ipv4).exploded,
                                          "ipv6": IPv6Address(ipv6).exploded,
                                          "port": str(port).zfill(5),
                                          "is_supernode": "true"
                                          })

    def remove_neighbor(self, ipv4, ipv6, port):
        """
            Rimuove un vicino
        """
        cursor = self.db.neighbors.find({"ipv4": IPv4Address(ipv4).exploded,
                                         "ipv6": IPv6Address(ipv6).exploded,
                                         "port": str(port).zfill(5)
                                         })

        if cursor is not None:
            self.db.neighbors.remove({"$or": [{"ipv4": IPv4Address(ipv4).exploded},
                                              {"ipv6": IPv6Address(ipv6).exploded}]
                                      })

    def get_packets(self):
        """
            Restituisce tutti i pacchetti transitati
        """
        cursor = self.db.packets.find()
        return list(cursor)

    def insert_packet(self, pktId):
        """
            Inserisce un pacchetto transitato
        """
        cursor = self.db.packets.find_one({"pktId": pktId})
        if cursor is not None:
            # TODO: modificare print
            print "already visited"
        else:
            try:
                self.db.packets.insert_one({"pktId": pktId})
            except Exception as e:
                print "insert_packet: " + e.message

    def get_sessions(self):
        """
            Restituisce tutte le sessioni aperte
        """
        cursor = self.db.sessions.find()
        return list(cursor)

    def get_session(self, session_id):
        session = self.db.sessions.find_one({"session_id": session_id})
        return session

    def insert_session(self, ipv4, ipv6, port):
        """
            Inserisce una nuova sessione, o restitusce il session_id in caso esista già
        """
        cursor = self.db.sessions.find({"ipv4": ipv4,
                                        "ipv6": ipv6,
                                        "port": port
                                        })
        if cursor.count() is not None:
            # TODO: modificare print
            print "already logged in"
            # Restituisco il session id esistente come da specifiche
            return cursor['session_id']
        else:
            try:
                session_id = id_generator(16)
                self.db.sessions.insert_one({"session_id": session_id,
                                       "ipv4": ipv4,
                                       "ipv6": ipv6,
                                       "port": port
                                       })
                return session_id
            except Exception as e:
                print "insert_session: " + e.message
                return "0000000000000000"

    def remove_session(self, session_id):
        """
            Esegue il logout di un utente eliminando i file da lui condivisi e restituendone il numero
        """
        try:
            # TODO: restituire il numero di file condivisi
            cursor = self.db.sessions.find_one({"session_id": session_id})

            if cursor is not None:
                removed_files = 0
                # recupero i file in cui compare l'id associato alla sessione dell'utente che ha richiesto il logout
                shared_files = list(self.db.files.find({"peers": {"$elemMatch": {"session_id": cursor['session_id']}}}))

                # per ogni file cerco il session_id corrispondente all'utente che ha richiesto il logout e lo elimino dalla lista
                for file in shared_files:
                    peers = list(file['peers'])
                    result = []

                    for peer in peers:
                        if peer['session_id'] != session_id: # se il session id è diverso lo mantengo nella lista
                            result.append(peer)

                    file['peers'] = result

                    self.db.files.update(
                        {"md5": file['md5']},
                        {
                            "$set": {"peers": file['peers']}
                        })

                    removed_files += 1

            self.db.sessions.remove({"session_id": session_id})

            return removed_files
        except Exception as e:
            print "remove_session: " + e.message

    def get_file_queries(self):
        """
            Restituisce tutte le ricerche di file
        """
        cursor = self.db.file_queries.find()
        return list(cursor)

    def insert_file_query(self, pktId, query_str):

        self.db.file_queries.insert_one({"pktId": pktId,
                                         "term": query_str,
                                         })

        # recupero i file disponibili dal database che soddisfano la ricerca
        files = self.get_files(query_str)

        if files is not None:
            results = []
            for file in files:
                has_peers = file['peers']
                if has_peers:
                    peers = []
                    for peer in file['peers']:
                        session = self.get_session(peer['session_id'])
                        if session:
                            peers.append({"ipv4": session['ipv4'],
                                          "ipv6": session['ipv6'],
                                          "port": session['port']})

                    file['peers'] = peers
                    results.append(file)
                else:
                    continue

            self.db.file_queries.update({"pktId": pktId},
                                        {
                                            "$set": {"results": results}
                                        })


    def get_peer_queries(self):
        """
            Restituisce tutte le ricerche di peers
        """
        cursor = self.db.peer_queries.find()
        return list(cursor)