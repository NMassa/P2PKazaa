# coding=utf-8
import os
import hashlib
import random
import string
import socket
import connection


def hashfile(file, hasher, blocksize=65536):
    buf = file.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = file.read(blocksize)
    return hasher.hexdigest()


def get_shareable_files():
    files_list = []

    for root, dirs, files in os.walk("shareable"):
        for file in files:
            file_md5 = hashfile(open("shareable/" + file, 'rb'), hashlib.md5())
            files_list.append({
                'name': file,
                'md5': file_md5
            })

    return files_list


def id_generator(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def recvall(socket, chunk_size):
    """
    Legge dalla socket un certo numero di byte, evitando letture inferiori alla dimensione specificata

    :param socket: socket per le comunicazioni
    :type socket: object
    :param chunk_size: lunghezza (numero di byte) di una parte di file
    :type chunk_size: int
    :return: dati letti dalla socket
    :rtype: bytearray
    """

    data = socket.recv(chunk_size)  # Lettura di chunk_size byte dalla socket
    actual_length = len(data)

    # Se sono stati letti meno byte di chunk_size continua la lettura finchè non si raggiunge la dimensione specificata
    while actual_length < chunk_size:
        new_data = socket.recv(chunk_size - actual_length)
        actual_length += len(new_data)
        data += new_data

    return data


def filesize(self, n):
        """
        Calcola la dimensione del file

        :param n: nome del file
        :type n: str
        :return: dimensione del file
        :rtype: int
        """

        f = open(n, 'r')
        f.seek(0, 2)
        sz = f.tell()
        f.seek(0, 0)
        f.close()
        return sz


def print_menu_top(lock):
    lock.acquire()
    print "########################################################"
    print "##                                                    ##"
    print "## |  \  /  \                                         ##\n" + \
          "## | $$ /  $$  ______   ________   ______    ______   ##\n" + \
          "## | $$/  $$  |      \ |        \ |      \  |      \  ##\n" + \
          "## | $$  $$    \$$$$$$\ \$$$$$$$$  \$$$$$$\  \$$$$$$\ ##\n" + \
          "## | $$$$$\   /      $$  /    $$  /      $$ /      $$ ##\n" + \
          "## | $$ \$$\ |  $$$$$$$ /  $$$$_ |  $$$$$$$|  $$$$$$$ ##\n" + \
          "## | $$  \$$\ \$$    $$|  $$    \ \$$    $$ \$$    $$ ##\n" + \
          "## \$$   \$$  \$$$$$$$ \$$$$$$$$  \$$$$$$$  \$$$$$$$  ##"
    print "##                                                    ##"
    print "########################################################"
    print "##                                                    ##"
    lock.release()


def print_menu_bottom(lock):
    lock.acquire()
    print "##                                                    ##"
    print "########################################################"
    lock.release()


def output(lock, message):
    lock.acquire()
    print message
    lock.release()

def update_progress(lock, count, total, suffix=''):
    """
    Stampa la barra di progresso di download e upload

    :param count: progresso
    :type count: int
    :param total: totale
    :type total: int
    :param suffix: nome del file
    :type suffix: str
    """
    lock.acquire()

    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('\r[%s] %s%s ...%s' % (bar, percents, '%', suffix))
    sys.stdout.flush()

    lock.release()

def sendTo(output_lock, ipv4, ipv6, port, msg):

    # Non invio all'indirizzo da cui è arrivato il pacchetto
    try:
        output(output_lock, "\nConnecting to: " + ipv4 + "\t" + ipv6 + "\t" + port)

        c = connection.Connection(ipv4, ipv6, port, output_lock)
        c.connect()
        peerSock = c.socket

        peerSock.send(msg)

        output(output_lock, "\nMessage sent : ")
        output(output_lock, msg)

        peerSock.close()
    except IOError as e:
        output(output_lock, 'send_near-Socket Error: ' + e.message)
    except socket.error, msg:
        output(output_lock, 'send_near-Socket Error: ' + str(msg))

    except Exception as e:
        output(output_lock, 'send_near-Error: ' + e.message)