from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
from app import app, db
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
        return jsonify({"message": "File uploaded successfully"}), 200
    return jsonify({"error": "Invalid file type"}), 400

@main.route('/show_upload', methods=['GET'])
def show_upload():
    return render_template('upload.html')

@main.route('/videos', methods=['GET'])
def list_videos():
    videos = Video.query.all()
    return render_template('video_list.html', videos=videos)
    #return jsonify([video.filename for video in videos]), 200

@main.route('/play/<int:video_id>', methods=['GET'])
def play_video(video_id):
    video = Video.query.get(video_id)
    if not video:
        abort(404)  # Se o vídeo não for encontrado, retorne um erro 404
    
    # Determinar o tipo MIME
    file_extension = video.filename.rsplit('.', 1)[1].lower()  # Obtenha a extensão do arquivo
    mime_type = MIME_TYPES.get(file_extension, "video/mp4")  # Use um tipo padrão se a extensão não for reconhecida
    
    return render_template('play_video.html', video=video, mime_type=mime_type)





if __name__ == '__main__':
    app.run(debug=True)
