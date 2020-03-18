import os
import subprocess
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

    lynis_output = ''
    if not read_only_filesystem:
        # Install curl and tar
        process_install_packages = subprocess.Popen('apk add --no-cache curl tar', shell=True)
        # Install Lynis
        process_install_packages.wait()
        process_install_lynis = subprocess.Popen('cd /tmp/ && curl -s https://downloads.cisofy.com/lynis/lynis-2.7.5.tar.gz | tar xvz -C {0}/'.format(file_folder), shell=True)
        # Execute Lynis
        process_install_lynis.wait()
        subprocess.Popen('cd /lynis && ./lynis audit system', shell=True)

    return json.dumps({'whoami': user, 'read-only-fs': read_only_filesystem})
