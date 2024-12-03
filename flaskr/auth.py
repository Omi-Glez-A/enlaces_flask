'''
El módulo FUNCTOOLS es para funciones que devuelven o actúan sobre 
otras funciones.
Una BLUEPRINT es una forma de organizar un grupo de vistas y otro 
código relacionado enrte sí. En lugar de registrar vistas y demás código,
lo registramos con una blueprint. Entonces la blueprint se registra con
la app cuando está disponible en la función "fábrica" (sería la de 
create_app())
'''
import functools

from flask import ( 
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# creamos una blueprint con los siguientes argumentos:
# 'auth' es el nombre de la blueprint
# con __name__ decimos dónde la hemos definido (__name__ es el nómbre
# del modulo de python y sería la carpeta flaskr, que es donde está el
# __init__.py) 
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET','POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Se requiere nombre de usuario.'
        elif not password:
            error = 'Se requiere contrasenya.'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?,?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"La persona usuaria {username} already registered."
            else:
                return redirect(url_for('auth.login'))

        flash(error)
    
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET','POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            # "," després de username indica que és una tupla, si no
            # se posa, dona error perque ho interpreta com una sola
            # expresió, i interpretarà que estam passant es número de parámetres
            # corresponent al numero de caracters que té es valor de sa variable 
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Nombre incorrecto.'
        elif not check_password_hash(user['password'], password):
            error = 'Contrasenya incorrecta.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


'''
bp.before_app_request registra una función que se ejectua antes de la
función de la vista (view) indiferentemente de la url solicitada. Comprueba
si un usuario está almacenado en la sessión y obtiene los datos de ese 
usuario y lo guarda en g
'''
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    
    return wrapped_view