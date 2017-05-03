from functools import wraps
from flask import request, abort
from oauth2client import client, crypt
from dao import User


def get_user_from_id_token(id_token):
    """
    :param id_token: 
    :return: User object 
    """
    id_info = client.verify_id_token(id_token, None)
    dict_data = {
        'userID': id_info['sub'],
        'firstName': id_info['given_name'],
        'lastName': id_info['family_name'],
        'email': id_info['email'],
        'phone': "",
        'userStatus': 0
    }
    user = User(dict_data)
    return user


def verify_google_id_token(id_token):
    """
    Verifies if id_token is a valid google account token
    :param id_token: 
    :return: None or sub
    """

    try:
        # id_info = client.verify_id_token(id_token, CLIENT_ID)

        # Or, if multiple clients access the backend server:
        id_info = client.verify_id_token(id_token, None)
        # if id_info['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #    raise crypt.AppIdentityError("Unrecognized client.")

        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")

            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #    raise crypt.AppIdentityError("Wrong hosted domain.")
    except crypt.AppIdentityError:
        # Invalid token
        return None
    user_id = id_info['sub']
    return user_id


def authenticated(fn):
    """
    Decorator which checks if there is Authenticate: Bearer id_token in headers and then 
    checks if it's a valid Google ID
    Returns sub of the user or None if error
    :param fn: 
    :return: None or sub
    Usage:
    @app.route("/")
    @authenticated
    def something(user_id=None):
        pass
    """
    @wraps(fn)
    def wrapped_function(*args, **kwargs):
        # TODO: input data verification to be handled by separate module
        if 'Authorization' not in request.headers:
            # Unauthorized
            print("There is no id_token in header")
            abort(401)
            return None

        if not(request.headers['Authorization'].startswith("Bearer ")):
            # Unauthorized
            print("Authentication doesn't contain Bearer in front")
            abort(401)
            return None

        print("Checking token...")
        # extracts 'Authorization: Bearer <id_token>' and checks id_token
        user_id = verify_google_id_token(request.headers['Authorization'].split(" ")[1])
        if user_id is None:
            print("This is not a valid Google account id_token")
            # Unauthorized
            abort(401)
            return None

        return fn(user_id=user_id, *args, **kwargs)
    return wrapped_function
