from flask import Blueprint, abort, flash, redirect, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
import socket
from flask_socketio import SocketIO, emit
from app import app, db
from app import socketio
import os

main = Blueprint('main', __name__)

MIME_TYPES = {
    "mp4": "video/mp4",
    "avi": "video/x-msvideo",
    "mkv": "video/x-matroska",
    "flv": "video/x-flv"
}

# Modelo para metadados de vídeo no banco de dados
class Video(db.Model):
    __tablename__ = 'video'
    __table_args__ = {'extend_existing': True}
    
    # ... outros campos aqui ...
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)  # Descrição do vídeo (opcional)

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


CHUNK_SIZE = 1024  # Define o tamanho do pacote. Pode ser ajustado conforme necessário.

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
    client.connect(("localhost", 9999))

    file_size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    client.send(str(file_size).encode().zfill(10))  # enviando o tamanho do arquivo como uma string de tamanho 10
    
    # Enviando o tamanho do nome do arquivo
    client.send(str(len(filename)).encode().zfill(10))
    
    # Enviando o nome do arquivo
    client.send(filename.encode())

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
    #return jsonify([video.filename for video in videos]), 200

# @main.route('/play/<int:video_id>', methods=['GET'])
# def play_video(video_id):
#     video = Video.query.get(video_id)
#     if not video:
#         abort(404)  # Se o vídeo não for encontrado, retorne um erro 404
    
#     # Determinar o tipo MIME
#     file_extension = video.filename.rsplit('.', 1)[1].lower()  # Obtenha a extensão do arquivo
#     mime_type = MIME_TYPES.get(file_extension, "video/mp4")  # Use um tipo padrão se a extensão não for reconhecida
    
#     return render_template('play_video.html', video=video, mime_type=mime_type)

@main.route('/play/<int:video_id>', methods=['GET'])
def play_video(video_id):
    video = Video.query.get(video_id)
    if not video:
        abort(404)  # Se o vídeo não for encontrado, retorne um erro 404

    return render_template('play_video.html', video=video)

@socketio.on('start_stream')
def handle_start_stream(video_id):
    video = Video.query.get(video_id)
    if not video:
        emit('video_stream_end')
        return

    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    
    with open(video_path, 'rb') as f:
        while True:
            chunk = f.read(4096)  # ler em pedaços de 4KB
            if not chunk:
                break
            emit('video_chunk', chunk)
        
    emit('video_stream_end')



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



@socketio.on('play_video')
def handle_message(message):
    # Aqui você colocaria a lógica de transmitir o vídeo usando sockets.
    # Por simplicidade, estou apenas enviando uma mensagem de volta.
    # Na prática, você enviaria chunks do vídeo e os renderizaria no cliente.
    send('This is a message from the server.', broadcast=True)



if __name__ == '__main__':
    app.run(debug=True)
