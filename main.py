import logging
import os
from dao import Algorithm, AlgorithmDAO, User, UserDAO, Dataset, DatasetDAO, ExecutorMockup, Bill, BillDAO, Period, ResultSet, ResultSetDAO
from flask import Flask, send_from_directory, url_for, redirect, json, \
    Response, request, render_template
from authentication import authenticated, get_user_from_id_token
import string
import datetime

app = Flask(__name__)

class WrongBillingPeriodError(Exception):
    """
    Exception raised when there are errors in suplied begin and end parameters for Period object

    Attributes:
        message (str): message

    """
    def __init__(self, message=None):
        """
        Exception constructor

        Args:
            message (str):  message
        """
        if message is not None:
            self.message = message
        else:
            self.message = 'Period related error'

class WrongPathIdError(Exception):
    """
    Exception raised when there are errors in suplied id in request path ie. algorithmid

    Attributes:
        message (str): message

    """
    def __init__(self, message=None):
        """
        Exception constructor

        Args:
            message (str):  message
        """
        if message is not None:
            self.message = message
        else:
            self.message = 'ID related error'

def get_billingperiod(requestargs):
    """
    Gets period of a billing query from request.args dictionary provided
    Args:
        requestargs (dict): request arguments where we look for begin and end

    Returns:
        period (Period): period of billing or None if not specified

    Raises:
        WrongBillingPeriodError: if there is begin argument in request query and something is wrong or missing
    """
    if 'begin' in requestargs:
        if 'end' in requestargs:
            begin = convert_to_date(requestargs['begin'])
            end = convert_to_date(requestargs['end'])
            if end < begin:
                raise WrongBillingPeriodError('End date ' + str(end) + ' is less then begin date' + str(begin))
            period = Period(begin, end)
            return period
        else:
            raise WrongBillingPeriodError("Wrong period in request query: there was a begin without an end")
    else:
        return None

def convert_to_date(date):
    """
    Converts date in integer like string rrrrmmdd format to datetime.date
    Args:
        date (str): date in rrrrmmdd format

    Returns:
        date_out (datetime.date):

    Raises:
        WrongBillingPeriodError: if there is something wrong in provided parameter

    """
    if len(date) == 8 and date.isnumeric():
        try:
            day = int(date[6:])
            month = int(date[4:6])
            year = int(date[0:4])
            date_out = datetime.date(year, month, day)
        except ValueError as err:
            raise WrongBillingPeriodError('The provided parameter ' + date + ' is not date in a form of yyyymmdd')
        return date_out
    else:
        raise WrongBillingPeriodError('The provided parameter ' + date + ' is not numeric or is not 8 digits long')


def has_no_whitespaces(my_string):
    for my_char in my_string:
        if my_char in string.whitespace:
            return False
    return True


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


# "Dataset API"
@authenticated
@app.route('/datasets/', methods=['GET'])
def api_datasets_get():
    """
    The Datasets endpoint returns information about the available datasets.
    The response includes the display name and other details about each dataset.
    It also allows full-text search of tags.
    result_code:
        0 OK
        1 Malformed query in uri
        2 Connection error
        3 Application or server error
        4 Wrong tags parameter
    """
    userID = get_user_from_id_token(request.headers['Authorization'].split(" ")[1])
    user = UserDAO.get(userID.getuser_id())
    datasets_list = []
    if 'tags' in request.args:
        tags = request.args['tags']
        # check if tags is a string and a coma delimited list of words (one space is acceptable only after coma)
        if not isinstance(tags, str):
            result_code = 4
        else:
            tags = tags.replace(', ', ',')
            tags_are_ok = True
            for tag in tags.split(','):
                if not has_no_whitespaces(tag):
                    tags_are_ok = False
                    break
            if not tags_are_ok:
                result_code = 4
            else:
                result_code = DatasetDAO.searchindex(tags=tags, found_datasets_list=datasets_list)
    else:
        result_code = DatasetDAO.searchindex(found_datasets_list=datasets_list)
    if result_code == 0:
        for dataset in datasets_list:
            dtst = DatasetDAO.get(dataset['datasetId'])
            if dtst.getuserID() != user.getuser_id():
                datasets_list.remove(dataset)

        js = json.dumps(datasets_list)
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


@app.route('/datasets', methods=['POST'])
@authenticated
def api_datasets_post(user_id=None):
    """Add a new Dataset"""
    if request.headers['Content-Type'] == 'application/json':
        dict_data = request.json
        userID = get_user_from_id_token(request.headers['Authorization'].split(" ")[1])
        user = UserDAO.get(userID.getuser_id())
        if user != 1:
            if (DatasetDAO.getindex(dict_data['datasetId']) != 1 and DatasetDAO.isOwner(user.getuser_id(), dict_data['datasetId']) == 0) or DatasetDAO.getindex(dict_data['datasetId']) == 1:
                dict_data['userID'] = user.getuser_id()
                dataset = Dataset(dict_data)
                returned_code = DatasetDAO.set(dataset)
                if returned_code == 0:
                    data = {
                        "code": 200,
                        "fields": "string",
                        "message": "OK"
                    }
                    js = json.dumps(data)
                    resp = Response(js, status=200, mimetype='application/json')
                    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
                    return resp
                data = {
                    "code": 401,
                    "fields": "string",
                    "message": "Failed to add Dataset"
                }
                js = json.dumps(data)
                resp = Response(js, status=401, mimetype='application/json')
                resp.headers['Content-Type'] = 'application/json; charset=utf-8'
                return resp
            data = {
                "code": 403,
                "fields": "string",
                "message": "Forbidden"
            }
            js = json.dumps(data)
            resp = Response(js, status=403, mimetype='application/json')
            resp.headers['Content-Type'] = 'application/json; charset=utf-8'
            return resp
        data = {
            "code": 401,
            "fields": "string",
            "message": "Unauthorized"
        }
        js = json.dumps(data)
        resp = Response(js, status=400, mimetype='application/json')
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


@app.route('/datasets/<dataset_id>', methods=['DELETE'])
@authenticated
def api_dataset_delete(dataset_id, user_id=None):
    """
     Remove a single dataset
    """
    userID = get_user_from_id_token(request.headers['Authorization'].split(" ")[1])
    user = UserDAO.get(userID.getuser_id())

    if user != 1:
        if (DatasetDAO.getindex(dataset_id) != 1 and DatasetDAO.isOwner(user.getuser_id(), dataset_id) == 0) or DatasetDAO.getindex(dataset_id) == 1:
            result = DatasetDAO.delete(dataset_id)
            if result not in [1, 2]:
                resp = Response(status=200, mimetype='application/json')
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
        else:
            data = {
                "code": 403,
                "fields": "string",
                "message": "Forbidden - dataset not owned by user"
            }
            js = json.dumps(data)
            resp = Response(js, status=403, mimetype='application/json')
            resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    else:
        data = {
            "code": 401,
            "fields": "string",
            "message": "Unauthorized - user not registered"
        }
        js = json.dumps(data)
        resp = Response(js, status=401, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp


@app.route('/datasets/<dataset_id>', methods=['GET'])
@authenticated
def api_dataset_get(dataset_id, user_id=None):
    """
     Get a single dataset detailed information
     Everything but algorithmBLOB
    """
    userID = get_user_from_id_token(request.headers['Authorization'].split(" ")[1])
    user = UserDAO.get(userID.getuser_id())

    if user != 1:
        if (DatasetDAO.getindex(dataset_id) != 1 and DatasetDAO.isOwner(user.getuser_id(), dataset_id) == 0) or DatasetDAO.getindex(dataset_id) == 1:
            result = DatasetDAO.get(dataset_id)
            if result not in [1, 2]:
                dataset = result.get_dict()
                js = json.dumps(dataset)
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
        else:
            data = {
                "code": 403,
                "fields": "string",
                "message": "Forbidden - dataset not owned by user"
            }
            js = json.dumps(data)
            resp = Response(js, status=403, mimetype='application/json')
            resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    else:
        data = {
            "code": 401,
            "fields": "string",
            "message": "Unauthorized - user not registered"
        }
        js = json.dumps(data)
        resp = Response(js, status=401, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp


# "Algorithm API"
@app.route('/algorithms/', methods=['GET'])
def api_algorithms_get():
    """
    The Algorithms endpoint returns information about the available algorithms.
    The response includes the display name and other details about each algorithm.
    It also allows full-text search of tags.
    result_code:
        0 OK
        1 Malformed query in uri
        2 Connection error
        3 Application or server error
        4 Wrong tags parameter
    """
    algorithms_list = []
    if 'tags' in request.args:
        tags = request.args['tags']
        # check if tags is a string and a coma delimited list of words (one space is acceptable only after coma)
        if not isinstance(tags, str):
            result_code = 4
        else:
            tags = tags.replace(', ', ',')
            tags_are_ok = True
            for tag in tags.split(','):
                if not has_no_whitespaces(tag):
                    tags_are_ok = False
                    break
            if not tags_are_ok:
                result_code = 4
            else:
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


@app.route('/algorithms/<algorithm_id>', methods=['DELETE'])
@authenticated
def api_algorithm_delete(algorithm_id, user_id=None):
    """
     Remove a single algorithm
    """
    userID = get_user_from_id_token(request.headers['Authorization'].split(" ")[1])
    user = UserDAO.get(userID.getuser_id())
    if user != 1:
        if AlgorithmDAO.isOwner(user.getuser_id(), algorithm_id) == 0:
            result = AlgorithmDAO.delete(algorithm_id)
            if result not in [1, 2]:
                resp = Response(status=200, mimetype='application/json')
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
        else:
            data = {
                "code": 403,
                "fields": "string",
                "message": "Forbidden"
            }
            js = json.dumps(data)
            resp = Response(js, status=404, mimetype='application/json')
            resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    else:
        data = {
            "code": 401,
            "fields": "string",
            "message": "Unauthorized"
        }
        js = json.dumps(data)
        resp = Response(js, status=401, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp


@app.route('/algorithms/', methods=['POST'])
@authenticated
def api_algorithms_post(user_id=None):
    """Add a new Algorithm"""
    if request.headers['Content-Type'] == 'application/json':
        dict_data = request.json
        userID = get_user_from_id_token(request.headers['Authorization'].split(" ")[1])
        user = UserDAO.get(userID.getuser_id())
        if user != 1:
            if (AlgorithmDAO.getindex(dict_data['algorithmId']) != 1 and AlgorithmDAO.isOwner(user.getuser_id(),dict_data['algorithmId']) == 0) or AlgorithmDAO.getindex(dict_data['algorithmId']) == 1:
                dict_data['userID'] = user.getuser_id()
                algorithm = Algorithm(dict_data)
                returned_code = AlgorithmDAO.set(algorithm)
                if returned_code == 0:
                    data = {
                        "code": 200,
                        "fields": "string",
                        "message": "OK"
                    }
                    js = json.dumps(data)
                    resp = Response(js, status=200, mimetype='application/json')
                    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
                    return resp
                data = {
                    "code": 401,
                    "fields": "string",
                    "message": "Failed to add Algorithm"
                }
                js = json.dumps(data)
                resp = Response(js, status=401, mimetype='application/json')
                resp.headers['Content-Type'] = 'application/json; charset=utf-8'
                return resp
            data = {
                "code": 403,
                "fields": "string",
                "message": "Forbidden"
            }
            js = json.dumps(data)
            resp = Response(js, status=403, mimetype='application/json')
            resp.headers['Content-Type'] = 'application/json; charset=utf-8'
            return resp
        data = {
            "code": 401,
            "fields": "string",
            "message": "Unauthorized"
        }
        js = json.dumps(data)
        resp = Response(js, status=400, mimetype='application/json')
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

@app.route('/algorithms/<algorithm_id>/<dataset_id>', methods=['POST'])
@authenticated
def api_algorithm_post(algorithm_id, dataset_id, user_id=None):
    """
     Execute algorithm with a dataset_id
    """
    userID = get_user_from_id_token(request.headers['Authorization'].split(" ")[1])
    user = UserDAO.get(userID.getuser_id())

    if user != 1:
        if DatasetDAO.getindex(dataset_id) != 1 and DatasetDAO.isOwner(user.getuser_id(), dataset_id) == 0:
            result_body = ExecutorMockup.execute(algorithm_id, dataset_id)
            emptyresult_data = {"resultSetID": 'empty',
                                "resultBody": 'empty'}
            result = ResultSet(emptyresult_data)
            user = get_user_from_id_token(request.headers['Authorization'].split(" ")[1])
            result.setresultset_id(result.generateresultset_id(user.getuser_id(), algorithm_id, dataset_id))
            result.setresult_body(result_body)
            check = ResultSetDAO.set(result)

            if check == 0:
                resp = Response(status=200, mimetype='application/json')
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
        else:
            data = {
                "code": 403,
                "fields": "string",
                "message": "Forbidden - dataset not owned by user"
            }
            js = json.dumps(data)
            resp = Response(js, status=403, mimetype='application/json')
            resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    else:
        data = {
            "code": 401,
            "fields": "string",
            "message": "Unauthorized - user not registered"
        }
        js = json.dumps(data)
        resp = Response(js, status=401, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp

# "ResultSet API"

@app.route('/results/<algorithm_id>/<dataset_id>', methods=['GET'])
@authenticated
def api_resultset_get(algorithm_id, dataset_id, user_id=None):
    """
     Get resultset from datastore
    """
    emptyresult_data = {"resultSetID": 'empty',
                        "resultBody": 'empty'}
    result = ResultSet(emptyresult_data)
    user = get_user_from_id_token(request.headers['Authorization'].split(" ")[1])
    resultset_id = result.generateresultset_id(user.getuser_id(), algorithm_id, dataset_id)
    result = ResultSetDAO.get(resultset_id)
    if result != 1:
        resultset = result.get_dict()
        js = json.dumps(resultset)
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

@app.route('/results/<algorithm_id>/<dataset_id>', methods=['DELETE'])
@authenticated
def api_resultset_delete(algorithm_id, dataset_id, user_id=None):
    """
     Remove resultset from datastore
    """
    emptyresult_data = {"resultSetID": 'empty',
                        "resultBody": 'empty'}
    result = ResultSet(emptyresult_data)
    user = get_user_from_id_token(request.headers['Authorization'].split(" ")[1])
    resultset_id = result.generateresultset_id(user.getuser_id(), algorithm_id, dataset_id)
    result = ResultSetDAO.delete(resultset_id)
    if result == 0:
        resp = Response(status=200, mimetype='application/json')
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

# "User API"
@app.route('/user/', methods=['POST'])
@authenticated
def create_user(user_id=None):
    """
    Create new user
    :param user_id: 
    :return: 
    """
    returned_code = UserDAO.set(get_user_from_id_token(request.headers['Authorization'].split(" ")[1]))
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


@app.route('/user/', methods=['GET'])
@authenticated
def get_user_by_id(user_id=None):
    """
    Get complete user data
    :param user_id: ID of the logged on user
    :return: user_data
    """
    user = get_user_from_id_token(request.headers['Authorization'].split(" ")[1])
    result = UserDAO.get(user.getuser_id())
    if result != 1:
        user = result.get_dict()
        js = json.dumps(user)
        user_data = Response(js, status=200, mimetype='application/json')
        resp = user_data
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

@app.route('/user/', methods=['DELETE'])
@authenticated
def delete_user(user_id=None):
    """
    Delete user information
    :param user_id:
    :return:
    """
    user = get_user_from_id_token(request.headers['Authorization'].split(" ")[1])
    result = UserDAO.delete(user.getuser_id())
    if result == 0:
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

# "Billing API"
@app.route('/bill/', methods=['GET'])
@app.route('/bill/result/<resultsetid>', methods=['GET'])
@app.route('/bill/algorithm/<algorithmid>', methods=['GET'])
@authenticated
def bill_rcv(resultsetid=None, algorithmid=None, user_id=None):
    user = get_user_from_id_token(request.headers['Authorization'].split(" ")[1])
    bill = Bill(user)
    try:
        period = get_billingperiod(request.args)
        if period is not None:
            bill.setperiod(period)
        if resultsetid is not None:
            if not has_no_whitespaces(resultsetid):
                raise WrongPathIdError('resutlsetid has whitespaces')
            bill.setbilled_obj_id(billed_obj_id=resultsetid)
        if algorithmid is not None:
            if not has_no_whitespaces(algorithmid):
                raise WrongPathIdError('algorithmid has whitespaces')
            bill.setbilled_obj_id(billed_obj_id=algorithmid)
    except WrongBillingPeriodError as err:
        data = {
            "code": 400,
            "fields": err.message,
            "message": "Wrong period in request query"
            }
        js = json.dumps(data)
        resp = Response(js, status=400, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
        return resp
    except WrongPathIdError as err:
        data = {
            "code": 400,
            "fields": err.message,
            "message": "Wrong id in request path"
            }
        js = json.dumps(data)
        resp = Response(js, status=400, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
        return resp
    returned_billing = BillDAO.getbilling(bill)
    if returned_billing == 1:
        data = {
            "code": 404,
            "fields": "string",
            "message": "There is no billing for a given parameters"
        }
        js = json.dumps(data)
        resp = Response(js, status=404, mimetype='application/json')
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    else:
        bill_str = '<?xml version="1.0" encoding="UTF-8"?>' + returned_billing
        bill_data = Response(bill_str, status=200, mimetype='text/xml', content_type='text/xml;charset=utf-8')
        resp = bill_data
        resp.headers['Content-Type'] = 'text/xml; charset=utf-8'
    return resp


@app.errorhandler(404)
def error404(e):
    return """
    Page Not Found.
    """, 404


@app.errorhandler(500)
def server_error(e):
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

