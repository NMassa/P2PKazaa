# coding=utf-8
from Client import Peer
import sys
from Client import _PeerServer

# main
# Inizializzazione del peer
p = Peer.Peer()

while p.session_id is None:
    print 'Select one of the following options (\'e\' to exit):'
    print 'Do you want to make the supernode?'
    print '1 -> YES'
    print '2 -> NO'

    int_choice = None
    while int_choice is None:
        try:
            option = raw_input()    # Input da tastiera
        except SyntaxError:
            option = None

        if option is None:
            print 'Please select YES or NO'
        else:
            try:
                int_choice = int(option)
            except ValueError:
                print "A choice is required"

    if int_choice == 1:
        print "YOU ARE A SUPERNODE"         # sei un supernodo
        sys.exit()
    else:
        print "YOU ARE A PEER!"          # sei un peer

        print '1: Log In'
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
                sys.exit()          # Interrompo l'esecuzione
            else:
                try:
                    int_option = int(option)
                except ValueError:
                    print "A number is required"

        if int_option != 1:
            print 'Option ' + str(option) + ' not available'
        else:
            p.login()           # Effettua il login

            if p.session_id is not None:
                # Inizializzazione del server multithread che risponde alle richieste di download
                peerserver = _PeerServer.PeerServer(p.my_ipv4, p.my_ipv6, p.my_port, p.files_list)
                peerserver.start()
            else:
                break

            while p.session_id is not None:     # Utente loggato
                print "\nSelect one of the following options:"
                print "1: Add File"
                print "2: Remove File"
                print "3: Search File"
                print "4: LogOut"

                int_option = None
                while int_option is None:
                    try:
                        option = raw_input()    # Input da tastiera
                    except SyntaxError:
                        option = None

                    if option is None:
                        print 'Please select an option'
                    else:
                        try:
                            int_option = int(option)
                        except ValueError:
                            print "A number is required"

                if int_option == 1:
                    p.share()           # Aggiunta di un file alla directory
                elif int_option == 2:
                    p.remove()          # Rimozione di un file dalla directory
                elif int_option == 3:
                    p.search()          # Ricerca ed eventuale download di un file
                elif int_option == 4:
                    p.logout()          # Logout
                    peerserver.stop()   # Terminazione del server multithread che risponde alle richieste di download
                    sys.exit()          # Interrompo l'esecuzione
                else:
                    print 'Option ' + str(int_option) + ' not available'

