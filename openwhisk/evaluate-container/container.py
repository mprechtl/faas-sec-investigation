import os
import time
import json

def evaluate(file_folder, filename, file_content):

    # check for read-only filesystem
    read_only_filesystem = False
    try:
        with open('{0}/{1}'.format(file_folder, filename), 'w+') as file:
            file.write(file_content)
    except IOError:
        read_only_filesystem = True

    # check container user
    user = os.popen('whoami').read().rstrip()

    return {'whoami': user, 'read-only-fs': read_only_filesystem}
