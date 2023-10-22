import socket
import os

SERVER_IP = "localhost"
SERVER_PORT = 9999
BUFFER_SIZE = 1024
SAVE_DIR = "received_files"

def handle_client(client_socket):
    # Recebendo o tamanho do arquivo
    size_data = client_socket.recv(10).decode('utf-8')
    expected_size = int(size_data)
    received_size = 0
    
    # Recebendo o tamanho do nome do arquivo
    filename_length = int(client_socket.recv(10).decode('utf-8'))

    # Recebendo o nome do arquivo
    file_name = client_socket.recv(filename_length).decode()

    save_path = os.path.join(SAVE_DIR, file_name)

    with open(save_path, "wb") as f:
        while received_size < expected_size:
            data = client_socket.recv(min(BUFFER_SIZE, expected_size - received_size))
            received_size += len(data)
            f.write(data)

    print(f"File {file_name} received and saved to {save_path}.")
    client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(5)

    print(f"[*] Listening on {SERVER_IP}:{SERVER_PORT}")

    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    while True:
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        handle_client(client_socket)

if __name__ == "__main__":
    main()
