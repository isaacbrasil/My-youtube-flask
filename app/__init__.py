from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

app = Flask(__name__)

# Configurações básicas
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
app.config['THUMBNAIL_FOLDER'] = 'app/static/thumbnails'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mkv', 'flv'}


# Inicialização das extensões
db = SQLAlchemy(app)
socketio = SocketIO(app)

# Importação dos blueprints
from app.blueprints import main

# Registro dos blueprints
app.register_blueprint(main.main)

# Este arquivo não deve conter as rotas diretamente, elas devem estar em seus respectivos blueprints.
