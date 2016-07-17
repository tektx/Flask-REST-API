#!flask/bin/python
"""Provides REST API endpoints to serve business data.

Business information is retrieved from a CSV file and processed into JSON
format. This data is then accessible from REST API endpoints.
"""

import csv
import sys
from functools import wraps
from flask import Flask, jsonify, make_response, request, abort, Response

__author__ = "Travis Knight"
__email__ = "Travisknight@gmail.com"
__license__ = "BSD"

app = Flask(__name__)
db = []


def create_db(csv_path):
    """Reads the CSV of businesses and processes them into dictionaries.

    Args:
        csv_path (str): The path to the CSV file.

    Returns:
        list[dict]: The business info in JSON-formatted dictionaries.

    Raises:
        IOError: No file was found using the provided path.
    """
    businesses = []

    try:
        with open(csv_path, 'r') as csv_file:
            csv_file.seek(0)
            reader = csv.DictReader(csv_file)
            for row in reader:
                row['id'] = int(row['id'])
                businesses.append(row)
        return businesses

    except IOError as ioe:
        print ioe
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
    return Response('Could not verify your access level for that URL.\nYou need proper credentials', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def check_num(val):
    """Throws an error if expected integer values are not ints.

    Args:
        val (str): The value expected to be an integer.

    Returns:
        int: The input value as an integer, or an error thrown if it isn't an integer.
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


@app.route('/businesses', methods=['GET'])
def get_businesses():
    """Displays a paginated list of businesses sorted by ID.

    Shows the information for the first 50 businesses by default. Accepts
    parameters to display a certain page or change the number of entries
    displayed per page.

    Returns:
        dict: Business information and pagination metadata.
    """
    entries = check_num(request.args['entries']) if 'entries' in request.args else 50
    page = check_num(request.args['page']) if 'page' in request.args else 1
    start = (page-1) * entries
    end = start + entries
    if len(db[start:end]) > 0:
        return jsonify({'businesses': db[start:end],
                        'page': page,
                        'entries': entries})
    else:
        abort(404)


@app.route('/businesses/<int:business_id>', methods=['GET'])
def get_business(business_id):
    business = [business for business in db if business['id'] == business_id]
    if len(business) == 0:
        abort(404)
    return jsonify({'business': business[0]})


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
    global db
    db = create_db('50k_businesses.csv')
    app.run(debug=True)


if __name__ == '__main__':
    main()
