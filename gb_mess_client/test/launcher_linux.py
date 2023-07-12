""" Модуль для тестового запуска приложения в Linux"""
import os
import subprocess
import time

PROCESS = []

print(os.getcwd())

while True:
    ACTION = input(
        "Выберите действие: q - выход, "
        "c  - запустить клиенты, x - закрыть все окна: "
    )

    if ACTION == "q":
        break
    # elif ACTION == "s":
    #     PROCESS.append(
    #         subprocess.Popen(
    #             "gnome-terminal -- python server.py",
    #             stdout=subprocess.PIPE,
    #             stderr=None,
    #             shell=True,
    #         )
    #     )
    #     time.sleep(0.1)
    elif ACTION == "c":
        for user in ["test1", "test2", "test3"]:
            PROCESS.append(
                subprocess.Popen(
                    f"gnome-terminal --disable-factory -- python ./src/client.py -u {user} -p 123",
                    stdout=subprocess.PIPE,
                    stderr=None,
                    shell=True,
                )
            )
            time.sleep(0.1)

    elif ACTION == "x":
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
