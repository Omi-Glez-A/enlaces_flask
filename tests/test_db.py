import sqlite3

import pytest
from flaskr.db import get_db

'''
monkeypatch es una fixture de pytest que permite modificar, establecer, 
borrar atributos, variables de entorno, elementos de un diccionario, sys.path 
y/u otras configuraciones globales de las que dependen funcionalidades que podrían 
ser invocadas durante nuestros tests de forma segura. Todas estas modificaciones
se deshacen una vez transcurrida la función o fixture que hace la petición.
'''

def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value) # después del app_context, la 
    # conexión a la base de datos debería cerrarse.

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Inicializada la base de datos' in result.output
    assert Recorder.called



