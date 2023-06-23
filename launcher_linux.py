import os
import subprocess
import time

PROCESS = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер, c  - запустить клиенты, x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        PROCESS.append(subprocess.Popen('gnome-terminal -- python server.py',
                                        stdout=subprocess.PIPE,
                                        stderr=None,
                                        shell=True
                                        ))
        time.sleep(0.1)
    elif ACTION == 'c':
        for user in ['test1', 'test2', 'test3']:
            PROCESS.append(subprocess.Popen(f'gnome-terminal --disable-factory -- python client.py -u {user}',
                                            stdout=subprocess.PIPE,
                                            stderr=None,
                                            shell=True
                                            ))
            time.sleep(0.1)

    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
