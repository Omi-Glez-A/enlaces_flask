import pytest
from flask import g, session
from flaskr.db import get_db

'''
Location en el header de la respuesta cuando el registro ha ido bien,
indica la url a la que se debe hacer la redirección. 
Data contiene el cuerpo de la respuesta en forma de bytes (y se comparará con
bytes. Si queremos comparar texto utilizamos get_data(as_text=True))
'''
def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None

'''
Parametrize nos permite ejecutar la misma función pasándole argumentos 
diferentes. Le pasamos distintos inputs erróneos para comprobar los
mensajes de error.
'''
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Se requiere nombre de usuario.'),
    ('a', '', b'Se requiere contrasenya.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data

'''
El bloque with utilizado con client nos permite acceder a variables del 
contexto (como la session) después de que nos devuelvan la response (es decir, fuera de 
la petición). Normalmente eso daría un error.
'''
def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Nombre incorrecto.'),
    ('test', 'a', b'Contrasenya incorrecta.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session