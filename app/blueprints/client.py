import asyncio
from flask import Blueprint, abort, flash, redirect, render_template, request, jsonify, url_for, Response
from werkzeug.utils import secure_filename
import socket
from flask_socketio import SocketIO, emit
from app import app, db, socketio
import os
import time

HOST = "127.0.1.1"
WEBSOCKET_PORT = 9999
CHUNK_SIZE = 4096  # Define o tamanho do pacote. Pode ser ajustado conforme necessário.

main = Blueprint('main', __name__)

MIME_TYPES = {
    "mp4": "video/mp4",
    "avi": "video/x-msvideo",
    "mkv": "video/x-matroska",
    "flv": "video/x-flv"
}

class StreamingError(Exception):
    """Exceção personalizada para erros de streaming."""
    pass


class Video(db.Model):
    __tablename__ = 'video'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@main.route('/upload', methods=['POST'])
def upload_file():
     if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
     file = request.files['file']
     if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
     if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_video = Video(filename=filename)
        db.session.add(new_video)
        db.session.commit()
    #     return jsonify({"message": "Arquivo upado com sucesso!"}), 200
    # return jsonify({"error": "Invalid file type"}), 400
     client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     client.connect((HOST, 9999))
    
         # Enviar comando UPLOAD
     header = f"UPLOAD"
     client.send(header.encode())
    
    # Enviar tamanho do arquivo como uma string de tamanho 10
     file_size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], filename))
     client.send(str(file_size).encode().zfill(10))

    # Enviar tamanho do nome do arquivo
     client.send(str(len(filename)).encode().zfill(10))

    # Enviar nome do arquivo
     client.send(filename.encode())
    
    # Resetar ponteiro do arquivo e enviar seus dados
     file.seek(0)
     while True:
        chunk = file.read(CHUNK_SIZE)
        if not chunk:
            break  # Fim do arquivo
        client.sendall(chunk)

     client.close()
     return "File uploaded successfully! You can now upload another file."

@main.route('/', methods=['GET'])
def show_upload():
    return render_template('upload.html')

@main.route('/videos', methods=['GET'])
def list_videos():
    videos = Video.query.all()
    return render_template('video_list.html', videos=videos)

from websockets import connect as ws_connect

@main.route('/play/<int:video_id>', methods=['GET'])
def play_video(video_id):
    video = Video.query.get(video_id)
    video_name = video.filename

    # Adicionando failover para o streaming de vídeo
    for _ in range(3):  # Tenta até 3 vezes, uma para cada réplica
        try:
            return stream_video(video_name)
        except StreamingError:
            continue  # Se ocorrer um erro, tenta a próxima réplica

    return "Não foi possível reproduzir o vídeo."

def stream_video(video_name):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, 9999))

        header = f"STREAM"
        client.send(header.encode())
        client.send(str(len(video_name)).zfill(10).encode())
        client.send(video_name.encode())

        def generate():
            while True:
                chunk = client.recv(CHUNK_SIZE)
                if not chunk:
                    break
                yield chunk

        ext = video_name.split('.')[-1]
        mime_type = MIME_TYPES.get(ext, "video/mp4")
        return Response(generate(), content_type=mime_type)
    
    except ConnectionError:
            # Esta exceção pode ser lançada se houver um problema de conexão de rede
            raise StreamingError("Erro de conexão durante o streaming do vídeo")

@main.route('/delete_video/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    video = Video.query.get(video_id)
    if video:
        db.session.delete(video)
        db.session.commit()
        return redirect(url_for('main.list_videos'))
    else:
        # Caso o vídeo não seja encontrado no banco de dados
        flash('Vídeo não encontrado', 'error')
        return redirect(url_for('main.list_videos'))

if __name__ == '__main__':
    app.run(debug=True)
