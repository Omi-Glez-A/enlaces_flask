import sqlite3
from datetime import datetime

import click
from flask import current_app, g
'''
- g es un objeto especial para almacenar datos a los que accederán diferentes
funciones durante las peticiones y que serán reutilizadosen lugar crear nuevas
conexiones con la bd si se llama a get_db por seguna vez con la misma request.
- current_app, es otro objecto especial queseñala a la app que maneja las 
peticiones, puesto que al utilizar la "fábrica de apps" (el archivo __init__), 
no hay objeto "app" mientras escribimos este código
'''

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    # open_resource abre un archivo relativo al paquete flaskr.
    # (útil porque cuando despliegues la aplicación no sabremos
    # necesariamente la localización de ese recurso)
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# click.command() define una línea de comando que llama a la función
#  init_db
@click.command('init-db')
def init_db_command():
    # limpia los datos existentes y crea nuevas tablas
    init_db()
    click.echo('Inicializada la base de datos')

# para interpretar valores de timestamp en la base de datos.
sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app):
    '''
    - teardown_appcontext: llama a la función close_db cuando desaparece el
    contexto de aplicación al devolver la respuesta y finalizar la petición
    - cli.add_command añade una nueva orden que se puede ejecutar en la terminal
    junto al comando de flask
    '''
    app.teardown_appcontext(close_db) 
    app.cli.add_command(init_db_command)