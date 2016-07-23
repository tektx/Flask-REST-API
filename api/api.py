#!flask/bin/python
"""Provides REST API endpoints to serve business data.

Business information is retrieved from a CSV file and processed into JSON
format. This data is then accessible from REST API endpoints.
"""

import csv
import os
from sqlite3 import dbapi2 as sqlite3
import sys
from functools import wraps
from flask import Flask, jsonify, make_response, request, abort, Response, g

__author__ = "Travis Knight"
__email__ = "Travisknight@gmail.com"
__license__ = "BSD"

app = Flask(__name__)

app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'businesses.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='pass'
))
app.config.from_envvar('API_SETTINGS', silent=True)


def connect_db():
    """Connects to the database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    import_db('api' + os.sep + 'sample.csv')
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def import_db(csv_path):
    """Reads a CSV of businesses and imports them into the database.

    Args:
        csv_path (str): The path to the CSV file.

    Raises:
        IOError: No file was found using the provided path.
    """
    db = get_db()
    try:
        with open(csv_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                db.execute('insert into entries ('
                           'uuid, name, address, address2, city, state, zip,'
                           'country, phone, website, created_at) values'
                           '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                           [row['uuid'], row['name'], row['address'],
                            row['address2'], row['city'], row['state'],
                            row['zip'], row['country'], row['phone'],
                            row['website'], row['created_at']])
                db.commit()

    except IOError as ioe:
        print(ioe)
        sys.exit(1)


def check_auth(username, password):
    """Checks if a username and password combination is valid.

    Args:
        username (str): The username to check.
        password (str): The password to check.

    Returns:
        bool: True if the combination is authentication, False otherwise.
    """
    return username == 'admin' and password == 'secret'


def authenticate():
    """Sends a 401 response that enables basic auth."""
    return Response('Could not verify your access level for that URL.\n'
                    'You need proper credentials', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def check_num(val):
    """Throws an error if expected value is not an integer.

    Args:
        val (str): The value expected to be an integer.

    Returns:
        int: The input value as an integer, or an error thrown if not an int.
    """
    try:
        return int(val)
    except ValueError:
        abort(404)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/secret-page')
@requires_auth
def secret_page():
    return ""


@app.route('/businesses')
def show_entries():
    """Displays a paginated list of businesses sorted by ID.

    Shows the information for the first 50 businesses by default. Accepts
    parameters to display a certain page or change the number of entries
    displayed per page.

    Returns:
        json: Business information and pagination metadata.
    """
    db = get_db()
    entries = check_num(request.args['entries']) if 'entries' in request.args\
        else 50
    page = check_num(request.args['page']) if 'page' in request.args else 1
    start = (page-1) * entries
    end = start + entries
    cur = db.execute('select * from entries '
                     'where id > ? and id <= ? '
                     'order by id asc', [start, end])
    fetched = cur.fetchall()
    rv = {'businesses': [dict((cur.description[idx][0], value)
                              for idx, value in enumerate(row))
                         for row in fetched],
          'page': page,
          'entries': entries}

    return jsonify(rv)


@app.route('/businesses/<int:business_id>', methods=['GET'])
def get_business(business_id):
    db = get_db()
    business = [business for business in db if business['id'] == business_id]
    if len(business) == 0:
        abort(404)
    return jsonify({'businesses': business[0]})


@app.errorhandler(400)
def bad_request(error):
    return make_response(
        jsonify({'status': 400,
                 'error': 'The server cannot process the request.'}), 400)


@app.errorhandler(401)
def unauthorized(error):
    return make_response(
        jsonify({'status': 401,
                 'error': 'The authentication was not successful.'}), 401)


@app.errorhandler(403)
def forbidden(error):
    return make_response(
        jsonify({'status': 403,
                 'error': 'The request is not authorized.'}), 403)


@app.errorhandler(404)
def not_found(error):
    return make_response(
        jsonify({'status': 404,
                 'error': 'The requested resource was not found.'}), 404)


@app.errorhandler(405)
def not_allowed(error):
    return make_response(
        jsonify({'status': 405,
                 'error': 'The request method is not supported.'}), 405)


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
