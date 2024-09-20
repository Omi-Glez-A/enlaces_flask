'''
A diferència de Django, s'arxiu __init__.py s'ha de crear manualment.
Aquest arxiu serveix com a fàbrica de s'aplicació i per indicar a Python que
es directori que conté aquest arxiu ha de ser tractat com un paquet.
'''
import os

from flask import Flask

def create_app(test_config=None):

    '''
    Se crea la instancia de Flask. 
    - __name__ se refiere al nombre del módulo de python, que se refiere al nombre del .py
    - instance_relative_config=True vol dir que els arxius de config son relatius al "instance folder" (mirar qué és)
    - app.config.from_mapping estableix configuració per defecte que s'utilitzarà
    - app.config.from_pyfile sobreescriu es from mapping, per exemple sa secret key dev per una real en
    entorn de producció
    ''' 

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # carga el config, si existe, y no está testeando
        app.config.from_pyfile('config.py', silent=True)
    else:
        # carga el test config si lo han pasado
        app.config.from_mapping(test_config)

    # se asegura de que existe la carpeta de la instancia
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'hola mundo!'
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    return app