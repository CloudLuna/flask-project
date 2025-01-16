import sqlite3
from datetime import datetime

import click
from flask import current_app, g
#  g is an object unique for each request, used to store data that might be accessed by multiple functions during the request. (por si get_db is called more than 1nce in the same req)
#  current_app points to the flask app handling the request(the one that called get_db)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        #   sqlite3.conect() establish the conection (to the file that DATABASE pointed in the config file) 
        
        g.db.row_factory = sqlite3.Row
        #   sqlite3.Row tells the connection to return rows that behave like dicts. This allows accessing the columns by name. 

    return g.db

#to close the connection
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


#To init the db
def init_db():
    db = get_db()
    #  return a db connection
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    #  .open_resource() opens a file relative with flaskr packages (usefull if you don't know the location)

# click.command() defines a command line called init-db that calls that function and show follow msg
@click.command('init-db')

def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# sqlite3.register_converter() tells python how to interpret timestamp valuesa in database
sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)
#  convert timestamp value to datatime.datatime

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)