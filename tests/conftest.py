import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def app():

    ''' tempfile mkstemp crea y abre un archivo temporal. En create_app se 
    sobreescribe la ruta a la base de datos temporalmente para utilizar la db
    de prueba.
    '''
    db_fb, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True, # indica a Flask que la app está en modo test
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fb)
    os.unlink(db_path)

'''
Fixture es un pequeño trozo de código (una función, vamos) que nos ayuda a 
definir y manejar el montaje y desmontaje de los recursos que necesitamos 
para ejecutar nuestros tests.
Pytest usa las fixtures emparejando los nombres de las funciones con los nombres 
de los argumentos de las funciones de los test.
'''
@pytest.fixture
def client(app):
    return app.test_client() # crea un cliente para la app de prueba

@pytest.fixture
def runner(app):
    return app.test_cli_runner() # similar al test_client pero con una 
    # consola de comandos, ejecutando comandos de manera aislada y capturando
    # el resultado en un objeto Resultado

'''
Para no tener que estar escribiendo todo el tiempo una petición POST para 
loguearnos y testear si funciona la vista de login y autenticación, 
creamos una clase que se loguée y pasarle el cliente para los tests
'''
class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)
