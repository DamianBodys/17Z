# This is only for testing purposes
# build as described at https://developers.google.com/api-client-library/python/start/get_started
from os import environ

import httplib2
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets, verify_id_token
from oauth2client.client import Credentials
import argparse

SCOPE = 'profile'  # this is needed to get id_token for Bearer authentication
CLIENT_SECRET_FILE = environ['GOOGLE_TEST_CREDENTIALS']
# this is client secrets file generated as "Inny" to have request uris fo localhost and loopback it requires a file
# path in environment variable GOOGLE_TEST_CREDENTIALS
# eg. = "/root/Downloads/client_secret_99905204066-aes52kn7u7qtboiaotpa2548l23vhq1k.apps.googleusercontent.com.json"

CREDENTIALS_FILE = environ['GOOGLE_TEST_CREDENTIALS_FILE']  # it's required by tools.run_flow
# it has to be a local filesystem path too GOOGLE_TEST_CREDENTIALS_FILE eg. '/root/Documents/credentials.dat'
flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPE)


def get_id_token_for_testing():

    storage = Storage(CREDENTIALS_FILE)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        parser = argparse.ArgumentParser(parents=[tools.argparser])
        parser.add_argument('args', nargs=argparse.REMAINDER)
        flags = parser.parse_args()
        flags.auth_host_port=[8089]
        credentials = tools.run_flow(flow, storage, flags)
    if credentials.access_token_expired:
        http = httplib2.Http()
        credentials.refresh(http)
        for conn in http.connections.values():
            conn.close()
    id_token = credentials.token_response['id_token']
    #id_info = verify_id_token(id_token, None)
    return id_token


if __name__ == '__main__':
    get_id_token_for_testing()