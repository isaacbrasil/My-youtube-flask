import socket
import os
import shutil

SERVER_IP = "127.0.1.1"  # socket.gethostbyname(socket.gethostname())
SERVER_PORT = 9999
BUFFER_SIZE = 4096
SAVE_DIR = "received_files"

print("IP DA MÁQUINA:" + socket.gethostbyname(socket.gethostname()))

def handle_client(client, addr):
    header_method = client.recv(6).decode('utf-8', 'ignore')
    
    if header_method == 'UPLOAD':
        print('Handling upload...')
        upload_file(client)

    elif header_method == 'STREAM':
        filename_size_data = client.recv(10).decode('utf-8', 'ignore')
        filename_size = int(filename_size_data)
        filename = client.recv(filename_size).decode('utf-8', 'ignore')
        serve_file(client, filename)

    else:
        print(f"Unrecognized method: {header_method}")
        client.close()

def upload_file(client_socket):
    size_data = client_socket.recv(10).decode('utf-8')
    expected_size = int(size_data)
    received_size = 0

    filename_length = int(client_socket.recv(10).decode('utf-8'))
    file_name = client_socket.recv(filename_length).decode()
    save_path = os.path.join(SAVE_DIR, file_name)

    with open(save_path, "wb") as f:
        while received_size < expected_size:
            data = client_socket.recv(min(BUFFER_SIZE, expected_size - received_size))
            received_size += len(data)
            f.write(data)

    print(f"File {file_name} received and saved to {save_path}.")  

    # Simulação de réplicas em diferentes diretórios, quando tiver os ips basta apagar essa parte
    replica_dirs = ["replica1", "replica2", "replica3"]
    for replica_dir in replica_dirs:
        replica_path = os.path.join(SAVE_DIR, replica_dir, file_name)
        os.makedirs(os.path.dirname(replica_path), exist_ok=True)
        shutil.copyfile(save_path, replica_path)
    # até aqui
    
    client_socket.close()

def serve_file(client, filename):
    filepath = os.path.join(SAVE_DIR, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'rb') as file:
                while True:
                    chunk = file.read(BUFFER_SIZE)
                    if not chunk:
                        break
                    client.send(chunk)
        except Exception as e:
            print(f"Erro ao enviar arquivo: {e}")
    else:
        print(f"File {filename} not found.")
        client.send("ERROR".encode())

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
        handle_client(client_socket, addr)

if __name__ == "__main__":
    main()
