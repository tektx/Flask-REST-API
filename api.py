#!flask/bin/python
"""Provides REST API endpoints to serve business data.

Business information is retrieved from a CSV file and processed into JSON
format. This data is then accessible from REST API endpoints.
"""

import csv
import sys
import flask

__author__ = "Travis Knight"
__email__ = "Travisknight@gmail.com"
__license__ = "BSD"

app = flask.Flask(__name__)
tasks = []


def get_businesses(csv_path):
    """Reads the CSV of businesses and processes them into dictionaries.

    Args:
        csv_path (str): The path to the CSV file.

    Returns:
        bool: True if the processing was successful, False otherwise.

    Raises:
        IOError: No file was found using the provided path.
    """
    try:
        with open(csv_path, 'r') as csv_file:
            csv_file.seek(0)
            reader = csv.DictReader(csv_file)
            for row in reader:
                row['id'] = int(row['id'])
                tasks.append(row)

    except IOError as ioe:
        print ioe
        sys.exit(1)


@app.route('/businesses', methods=['GET'])
def get_tasks():
    records = 3
    # Pagination
    if flask.request.json and 'page' in flask.request.json:
        page = flask.request.json.get('page')
        start = (page-1) * records
        end = start + records
        return flask.jsonify({'tasks': tasks[start:end]})
    else:
        return flask.jsonify({'tasks': tasks[:records]})


@app.route('/businesses/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        flask.abort(404)
    return flask.jsonify({'task': task[0]})


@app.errorhandler(400)
def bad_request(error):
    return flask.make_response(flask.jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({'error': 'Not found'}), 404)


@app.errorhandler(405)
def not_allowed(error):
    return flask.make_response(flask.jsonify({'error': 'Not allowed'}), 405)


def main():
    get_businesses('sample.csv')
    app.run(debug=True)


if __name__ == '__main__':
    main()
