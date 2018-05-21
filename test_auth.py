# This is only for testing purposes
# build as described at https://developers.google.com/api-client-library/python/start/get_started
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets, verify_id_token

SCOPE = 'profile'  # this is needed to get id_token for Bearer authentication
CLIENT_SECRET_FILE = '/root/Downloads/client_secret_99905204066-aes52kn7u7qtboiaotpa2548l23vhq1k.' +\
                     'apps.googleusercontent.com.json'  # this is client secrets file generated as "Inny" to have
#                                                         request uris fo localhost and loopback
CREDENTIALS_FILE = '/root/Documents/credentials.dat'  # it's required by tools.run_flow
flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPE)


def get_id_token_for_testing():

    storage = Storage(CREDENTIALS_FILE)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, tools.argparser.parse_args())
    id_token = credentials.token_response['id_token']
    #id_info = verify_id_token(id_token, None)
    return id_token


if __name__ == '__main__':
    get_id_token_for_testing()