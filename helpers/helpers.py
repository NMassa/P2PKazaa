# coding=utf-8
import os
import hashlib
import random, string


def hashfile(file, hasher, blocksize=65536):
    buf = file.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = file.read(blocksize)
    return hasher.hexdigest()

def get_shareable_files():
    files_list = []

    for root, dirs, files in os.walk("fileCondivisi"):
        for file in files:
            file_md5 = hashfile(open("fileCondivisi/" + file, 'rb'), hashlib.md5())
            files_list.append({
                'name': file,
                'md5': file_md5
            })

    return files_list

def id_generator(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

