import os
from flask import Flask
from . import db

def create_app(test_config=None):
  # create and configure the app 
    #create flask instance
    app = Flask(__name__, instance_relative_config=True)
    #  instance_relative_config=True tells the app that configuration files are relative to the instance folder.
    #  __name__ is the name of the current Python module. 
    
    
    #set some default config the app will use
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    #  SECRET_KEY is used by Flask to keep data safe (should be overwrited)
    #  DATABASE is the path to SQLite database file
    #    app.instance_path path of the instance folder

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists or create it if doesnt
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    

    #DB definition and access
    db.init_app(app)

    return app