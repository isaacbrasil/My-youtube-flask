# Instalação de módulos 📜

Para rodar o projeto será necessário ter instalado o python e pip e baixar os seguintes pacotes:

```bash
# Instalar o gerenciador de pacotes pip
$ sudo apt install python3-pip

# Instalar o framework Flask
$ pip install -U Flask

# Install dependencies
$ pip install flask-socketio
$ pip install python-socketio
$ pip install websockets
$ pip install SQLAlchemy
$ pip install Flask-SQLAlchemy
$ pip install socketio

# Run the app
$ python3 run.py
```
# Manipulação dos dados 📜

Para rodar o projeto será necessário ter instalado o python e pip e baixar os seguintes pacotes:
```bash

# No caminho onde estiver armazenado o banco digite
$ sqlite3 [nome_do_banco].db

# Para ver as tabelas
$ .tables

# Queries

$ SELECT * FROM TABLE;
  INSERT INTO ...
  DELETE FROM ...

  # Para sair do sqlite3 basta digitar

  $ .quit
```