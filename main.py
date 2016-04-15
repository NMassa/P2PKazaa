# coding=utf-8
from Client.Peer import Peer
from servers import multithread_server
from dbmodules.dbconnection import *
import config

supernode_mode = False

# Avvio il server in ascolto sulle porte 80 e 6000
server = multithread_server.Server()
server.start()

db = MongoConnection()

print 'Are you a supernode?'
print '1: YES'
print '2: NO'

int_choice = None
while int_choice is None:
    try:
        option = raw_input()    # Input da tastiera
    except SyntaxError:
        option = None

    if option is None:
        print 'Please select an option'
    else:
        try:
            int_choice = int(option)
        except ValueError:
            print "A choice is required"


if int_choice == 1:
    print "YOU ARE A SUPERNODE"         # sei un supernodo
    supernode_mode = True
else:
    print "YOU ARE A PEER!"          # sei un peer

p = Peer()

while True:
    print "Select one of the following options ('e' to exit):"
    print "1: Search supernodes"

    int_option = None
    while int_option is None:
        try:
            option = raw_input()
        except SyntaxError:
            option = None

        if option is None:
            print 'Please select an option'
        elif option == 'e':
            print 'Bye bye'
            server.stop()
            sys.exit()  # Interrompo l'esecuzione
        else:
            try:
                int_option = int(option)
            except ValueError:
                print "A number is required"

    if int_option != 1:
        print 'Option ' + str(option) + ' not available'
    else:
        # TODO: ricerca dei supernodi tramite i vicini nella tabella neighbor, i supernodi vanno salvati nella tabella neighbor con is_supernode = true


        # una volta trovato almeno un supernodo


        if supernode_mode:
            while True:
                print "Select one of the following options ('e' to exit):"
                print "1: Search supernodes"
                print "2: Add file (to myself)"
                print "3: Delete file (from myself)"
                print "4: Search file"

                int_option = None
                try:
                    option = raw_input()
                except SyntaxError:
                    option = None

                if option is None:
                    print 'Please select an option'
                elif option == 'e':
                    print 'Bye bye'
                    server.stop()
                    sys.exit()  # Interrompo l'esecuzione
                else:
                    try:
                        int_option = int(option)
                    except ValueError:
                        print "A number is required"
                    else:
                        if int_option == 1:
                            # ricerca supernodi e salvataggio nel db
                            print "ricerca supernodi"
                        elif int_option == 2:
                            # scelgo un file dalla cartella e lo aggiungo alla directory
                            print "aggiunta file"
                        elif int_option == 3:
                            # scelgo un file dalla directory (tra i miei) e lo rimuovo
                            print "rimozione file"
                        elif int_option == 4:
                            # creo una query e la invio agli altri supernodi
                            print "query file"
                            # aspetto i risultati
                            print "wait 20s"

                            not_done = True
                            while not_done:
                                print "Select one of the following options ('e' to exit):"
                                print "1: View query results"
                                print "2: Download"

                                int_option = None
                                try:
                                    option = raw_input()
                                except SyntaxError:
                                    option = None

                                if option is None:
                                    print 'Please select an option'
                                elif option == 'e':
                                    print 'Bye bye'
                                    server.stop()
                                    sys.exit()  # Interrompo l'esecuzione
                                else:
                                    try:
                                        int_option = int(option)
                                    except ValueError:
                                        print "A number is required"
                                    else:
                                        if int_option == 1:
                                            # stampo a video i risultati della ricerca
                                            print "risultati"
                                        elif int_option == 2:
                                            # stampo i risultati e faccio scegliere il file da scaricare
                                            print "risultati + download"

                                            # Torno al menu principale
                                            not_done = False

                                        else:
                                            print 'Option ' + str(int_option) + ' not available'

                        else:
                            print 'Option ' + str(int_option) + ' not available'



        else:
            # se trovo almeno un supernodo faccio scegliere quale utilizzare per fare il login
            print "Select a supernode to log in:"
            print "lista supernodi"

            int_option = None
            while int_option is None:
                try:
                    option = raw_input()
                except SyntaxError:
                    option = None

                if option is None:
                    print 'Please select an option'
                else:
                    try:
                        int_option = int(option)
                    except ValueError:
                        print "A number is required"
                    else:
                        #TODO: impostare l'indirizzo del supernodo che fa da directory
                        p.dir_ipv4 = ""
                        p.dir_ipv6 = ""
                        p.dir_port = ""

                        # faccio il login
                        #p.login()
                        p.session_id = "269d4afsfdaf645as1"

                        while p.session_id is not None:
                            print "Select one of the following options:"
                            print "1: Add file"
                            print "2: Delete file"
                            print "3: Search file"
                            print "4: Log out"

                            int_option = None
                            try:
                                option = raw_input()
                            except SyntaxError:
                                option = None

                            if option is None:
                                print 'Please select an option'
                            else:
                                try:
                                    int_option = int(option)
                                except ValueError:
                                    print "A number is required"
                                else:
                                    if int_option == 1:
                                        # scelgo un file dalla cartella e lo aggiungo alla directory
                                        print "aggiunta file"
                                        #p.share()
                                    elif int_option == 2:
                                        # scelgo un file dalla directory (tra i miei) e lo rimuovo
                                        print "rimozione file"
                                        #p.remove()
                                    elif int_option == 3:
                                        # creo una query e la invio agli altri supernodi
                                        print "query file"
                                        #p.search()


                                        not_done = True
                                        while not_done:
                                            print "Select one of the following options ('e' to exit):"
                                            print "1: View query results"
                                            print "2: Download"

                                            int_option = None
                                            try:
                                                option = raw_input()
                                            except SyntaxError:
                                                option = None

                                            if option is None:
                                                print 'Please select an option'
                                            elif option == 'e':
                                                break
                                            else:
                                                try:
                                                    int_option = int(option)
                                                except ValueError:
                                                    print "A number is required"

                                                if int_option == 1:
                                                    # stampo a video i risultati della ricerca
                                                    print "risultati"
                                                elif int_option == 2:
                                                    # stampo i risultati e faccio scegliere il file da scaricare
                                                    print "risultati + download"

                                                    not_done = False
                                                else:
                                                    print 'Option ' + str(int_option) + ' not available'
                                    elif int_option == 4:
                                        print "logging out"
                                        p.session_id = None

                                    else:
                                        print 'Option ' + str(int_option) + ' not available'

        # int_option = None
        # while int_option is None:
        #     try:
        #         option = raw_input()
        #     except SyntaxError:
        #         option = None
        #
        #     if option is None:
        #         print 'Please select an option'
        #     elif option == 'e':
        #         print 'Bye bye'
        #         server.stop()
        #         sys.exit()  # Interrompo l'esecuzione
        #     else:
        #         try:
        #             int_option = int(option)
        #         except ValueError:
        #             print "A number is required"
        #
        #
        # while p.session_id is not None:     # Utente loggato
        #     print "\nSelect one of the following options:"
        #     print "1: Add File"
        #     print "2: Remove File"
        #     print "3: Search File"
        #     print "4: LogOut"
        #
        #     int_option = None
        #     while int_option is None:
        #         try:
        #             option = raw_input()    # Input da tastiera
        #         except SyntaxError:
        #             option = None
        #
        #         if option is None:
        #             print 'Please select an option'
        #         else:
        #             try:
        #                 int_option = int(option)
        #             except ValueError:
        #                 print "A number is required"
        #
        #     if int_option == 1:
        #         p.share()           # Aggiunta di un file alla directory
        #     elif int_option == 2:
        #         p.remove()          # Rimozione di un file dalla directory
        #     elif int_option == 3:
        #         p.search()          # Ricerca ed eventuale download di un file
        #     elif int_option == 4:
        #         p.logout()          # Logout
        #         peerserver.stop()   # Terminazione del server multithread che risponde alle richieste di download
        #         sys.exit()          # Interrompo l'esecuzione
        #     else:
        #         print 'Option ' + str(int_option) + ' not available'


