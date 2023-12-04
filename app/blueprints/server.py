import socket
import os
import shutil

SERVER_IP = "127.0.1.1" #socket.gethostbyname(socket.gethostname())
SERVER_PORT = 9999
BUFFER_SIZE = 4096
SAVE_DIR = "received_files"


print("IP DA MÁQUINA:" + socket.gethostbyname(socket.gethostname()))
# Dicionário para armazenar a localização das réplicas
video_replicas = {}

def handle_client(client, addr):
    header_method = client.recv(6).decode('utf-8', 'ignore')
    
    if header_method == 'UPLOAD':
        print('LETS UPLOAD')
        upload_file(client)

    elif header_method == 'STREAM':
        filename_size_data = client.recv(10).decode('utf-8', 'ignore')
        filename_size = int(filename_size_data)
        filename = client.recv(filename_size).decode('utf-8', 'ignore')

        # Modificado para verificar todas as réplicas
        for replica_path in video_replicas.get(filename, []):
            if os.path.exists(replica_path):
                serve_file(client, replica_path)
                break
        else:
            response = "ERROR"
            client.send(response.encode())

    else:
        print(f"Unrecognized method: {header_method}")
        client.close()


def upload_file(client_socket):
    # Receber tamanho do arquivo
    size_data = client_socket.recv(10).decode('utf-8')
    expected_size = int(size_data)
    received_size = 0

    # Receber nome do tamanho do arquivo
    filename_length = int(client_socket.recv(10).decode('utf-8'))

    # Receber nome do arquivo
    file_name = client_socket.recv(filename_length).decode()

    save_path = os.path.join(SAVE_DIR, file_name)

    with open(save_path, "wb") as f:
        while received_size < expected_size:
            data = client_socket.recv(min(BUFFER_SIZE, expected_size - received_size))
            received_size += len(data)
            f.write(data)

    print(f"File {file_name} received and saved to {save_path}.")  

    # Simulando a criação de réplicas
    replica_locations = [f"{SAVE_DIR}/replica1/{file_name}", 
                         f"{SAVE_DIR}/replica2/{file_name}", 
                         f"{SAVE_DIR}/replica3/{file_name}"]
    for location in replica_locations:
        os.makedirs(os.path.dirname(location), exist_ok=True)
        shutil.copyfile(save_path, location)

    # Atualizando o dicionário de réplicas
    video_replicas[file_name] = replica_locations

    client_socket.close()


def serve_file(client, filepath):
    try:
        with open(filepath, 'rb') as file:
            while True:
                chunk = file.read(BUFFER_SIZE)
                if not chunk:
                    break
                client.send(chunk)
    except Exception as e:
        print(f"Erro ao enviar arquivo: {e}")


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
