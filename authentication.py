"""
Description of a Google ID Tokens implemented in this module:
These six fields are included in all Google ID Tokens.
 "iss": "https://accounts.google.com",
 "sub": "110169484474386276334",
 "azp": "1008719970978-hb24n2dstb40o45d4feuo2ukqmcc6381.apps.googleusercontent.com",
 "aud": "1008719970978-hb24n2dstb40o45d4feuo2ukqmcc6381.apps.googleusercontent.com",
 "iat": "1433978353",
 "exp": "1433981953",

 These seven fields are only included when the user has granted the "profile" and
 "email" OAuth scopes to the application.
 "email": "testuser@gmail.com",
 "email_verified": "true",
 "name" : "Test User",
 "picture": "https://lh4.googleusercontent.com/-kYgzyAWpZzJ/ABCDEFGHI/AAAJKLMNOP/tIXL9Ir44LE/s99-c/photo.jpg",
 "given_name": "Test", as of May the 25th that data is no longer available in ID token because of RODO i EU
 "family_name": "User",  as of May the 25th that data is no longer available in ID token because of RODO i EU
 "locale": "en"
"""
from functools import wraps
from flask import request, abort
from oauth2client import client, crypt
from dao import User


def get_user_from_id_token(id_token):
    """
    Extracts user data from Google Identity Platform id_token.
    There is no phone in id_token so it's set to ""
    :param id_token: 
    :return: User object 
    """
    id_info = client.verify_id_token(id_token, None)
    dict_data = {
        'userID': id_info['sub'],
        # the following lines ware removed because of RODO in EU
        # 'firstName': id_info['given_name'],
        # 'lastName': id_info['family_name'],
        # 'email': id_info['email'],
        # 'phone': "",
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
    print(client.verify_id_token(id_token, None))
    try:
        id_info = client.verify_id_token(id_token, None)
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")
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
