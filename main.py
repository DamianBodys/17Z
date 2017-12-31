# [START app]
import logging
import os
from dao import Algorithm, AlgorithmDAO, User, UserDAO
from flask import Flask, send_from_directory, url_for, redirect, json, \
    Response, request, render_template
from authentication import authenticated, get_user_from_id_token

app = Flask(__name__)


def get_flexible_url():
    """this gets address of flexible app for jinja"""
    _FLEXIBLE_PROJECT_NAME = 'zflexible1'
    if os.environ.get('GOOGLE_CLOUD_PROJECT') is None:
        url = 'http://localhost:5000'
    else:
        url = 'https://' + _FLEXIBLE_PROJECT_NAME + '.appspot.com'
    return url


@app.route('/')
def hello():
    """Return a human readable site in HTML."""
    return render_template('index.html')


@app.route('/authentication.html')
def authentication_html():
    """Return a friendly greeting in HTML."""
    url = get_flexible_url()
    return render_template('authentication.html', url=url)


@app.route('/environment.html')
def environment_html():
    """Return a environment variables in HTML."""
    env_vars = dict(os.environ)
    return render_template('environment.html', env_vars=env_vars)


@app.route('/favicon.ico')
def favicon():
    """Icon for browsers"""
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/swaggerui/<path:path>', methods=['GET'])
def swaggerui(path):
    """Main directory for swaggerui"""
    return send_from_directory('static/swaggerui', path)


@app.route('/doc/', methods=['GET'])
def doc():
    """Main documentation page"""
    return redirect(url_for('swaggerui', path='index.html', url='/swagger.json'))


@app.route('/swagger.json', methods=['GET'])
def swagger():
    """Main file for SwaggerUI prepared for automatic generation of data"""
    data = json.load(open('static/swagger.json'))
    # changing schemes and host in swagger.json to get_flexible_url()
    url = get_flexible_url()
    data['host'] = url.split('://')[1]
    data['schemes'].clear()
    data['schemes'].append(url.split('://')[0])
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    resp.headers.add_header('Access-Control-Allow-Origin', '*')
    resp.headers.add_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, OPTIONS')
    resp.headers.add_header(
        'Access-Control-Allow-Headers',
        'Content-Type, api_key, Authorization, x-requested-with, Total-Count, Total-Pages, Error-Message')
    return resp


@app.route('/algorithms.html')
def algorithms_html():
    """Return a friendly greeting in HTML."""
    return render_template('algorithms.html')


@app.route('/algorithms/', methods=['GET'])
def api_algorithms_get():
    """
    The Algorithms endpoint returns information about the available algorithms.
    The response includes the display name and other details about each algorithm.
    It also allows full-text search of tags.
    """
    algorithms_list = []
    if 'tags' in request.args:
        tags = request.args['tags']
        result_code = AlgorithmDAO.searchindex(tags=tags, found_algorithms_list=algorithms_list)
    else:
        result_code = AlgorithmDAO.searchindex(found_algorithms_list=algorithms_list)
    if result_code == 0:
        js = json.dumps(algorithms_list)
        resp = Response(js, status=200, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
        return resp
    else:
        data = [{
            "code": 400,
            "fields": "string",
            "message": "Malformed Data"
        }]
        js = json.dumps(data)
        resp = Response(js, status=400, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
        return resp


@app.route('/algorithms/', methods=['POST'])
@authenticated
def api_algorithms_post(user_id=None):
    """Add a new Algorithm"""
    if request.headers['Content-Type'] == 'application/json':
        dict_data = request.json
        algorithm = Algorithm(dict_data)
        returned_code = AlgorithmDAO.set(algorithm)
        if returned_code == 0:
            data = {
                "code": 200,
                "fields": user_id,
                "message": "OK"
            }
            js = json.dumps(data)
            resp = Response(js, status=200, mimetype='application/json')
            resp.headers['Content-Type'] = 'application/json; charset=utf-8'
            return resp
    data = {
        "code": 400,
        "fields": "string",
        "message": "Malformed Data"
    }
    js = json.dumps(data)
    resp = Response(js, status=400, mimetype='application/json')
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp


@app.route('/algorithms/<algorithm_id>', methods=['GET'])
def api_algorithm_get(algorithm_id):
    """
     Get a single algorithm detailed information
     Everything but algorithmBLOB
    """
    result = AlgorithmDAO.get(algorithm_id)
    if result not in [1, 2]:
        algorithm = result.get_dict()
        js = json.dumps(algorithm)
        resp = Response(js, status=200, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    else:
        data = {
            "code": 404,
            "fields": "string",
            "message": "Not Found"
        }
        js = json.dumps(data)
        resp = Response(js, status=404, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp


@app.route('/user/', methods=['POST'])
@authenticated
def create_user(user_id=None):
    """
    Create new user from json object
    :param user_id: 
    :return: 
    """
    if request.headers['Content-Type'] == 'application/json':
        dict_data = {
            'userID': 0,
            'firstName': "",
            'lastName': "",
            'email': "",
            'phone': "",
            'userStatus': 0
        }
        dict_data1 = request.json
        dict_data.update(dict_data1)
        user = User(dict_data)
    else:
        data = {
            "code": 400,
            "fields": "Content-Type",
            "message": "Malformed Data"
        }
        js = json.dumps(data)
        resp = Response(js, status=400, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
        return resp
    returned_code = UserDAO.set(user)
    if returned_code == 0:
        data = {
            "code": 200,
            "fields": "",
            "message": "OK"
        }
        js = json.dumps(data)
        resp = Response(js, status=200, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    else:
        data = {
            "code": 400,
            "fields": "returned_code",
            "message": "Malformed Data"
        }
        js = json.dumps(data)
        resp = Response(js, status=400, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp


@app.route('/user/signup/', methods=['POST'])
@authenticated
def self_sign_up(user_id=None):
    """
    :param user_id: 'sub' field from Google id_token supplied in header Authenticate: Bearer <id_token>  
    :return: OK
    """
    user = get_user_from_id_token(request.headers['Authorization'].split(" ")[1])
    returned_code = UserDAO.set(user)
    if returned_code == 0:
        data = {
            "code": 200,
            "fields": "",
            "message": "OK"
        }
        js = json.dumps(data)
        resp = Response(js, status=200, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    else:
        data = {
            "code": 400,
            "fields": "string",
            "message": "Malformed Data"
        }
        js = json.dumps(data)
        resp = Response(js, status=400, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp


@app.route('/user/<uid>', methods=['GET'])
@authenticated
def get_user_by_id(uid, user_id=None):
    """
    Get complete user data
    :param uid: ID of a user to get 
    :param user_id: ID of the logged on user
    :return: user_data
    """
    result = UserDAO.get(uid)
    if result != 1:
        user = result.get_dict()
        js = json.dumps(user)
        user_data = Response(js, status=200, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
        resp = user_data
    else:
        data = {
            "code": 404,
            "fields": "string",
            "message": "Not Found"
        }
        js = json.dumps(data)
        resp = Response(js, status=404, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp


@app.errorhandler(404)
def error404(e):
    return """
    Page Not Found.
    """, 404


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stack-trace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entry point in app.yaml.
    #    app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(host='localhost', port=5000, debug=False)
    # app.run(host='localhost', port=8080, debug=True)
# [END app]
