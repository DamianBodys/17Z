import requests
import json
import os
from google.cloud import datastore
from datetime import datetime

# name of kind to store data in Datastore
_DATASTORE_KIND_ALGORITHMS = 'algorithms'
_DATASTORE_KIND_USERS = 'users'
_DATASTORE_KIND_DATASETS = 'datasets'


def get_search_url():
    """
    Gets address of standard appengine app to access Full Text Search in test and GAE environment

    :returns: url of 17ZSearch
    :rtype: str
    """
    _SEARCH_PROJECT_NAME = 'zsearch1'
    if os.environ.get('GOOGLE_CLOUD_PROJECT') is None:
        url = 'http://localhost:8080'
    else:
        url = 'https://' + _SEARCH_PROJECT_NAME + '.appspot.com'
    return url


class User:
    """ User class"""
    _data = {
        #      userID: string # google id_info['sub']
        #      firstName: string
        #       lastName: string
        #       email: string
        #       phone: string
        #       userStatus: integer
    }

    def setuser_id(self, user_id):
        """
        Writes userID and converts parameters to str

        We have to make sure that every user_id is treated as string
        regardless of user input.

        :param user_id: id to write
        :type user_id: str, int
        """
        if type(user_id) is str:
            self._data['userID'] = user_id
        else:
            self._data['userID'] = str(user_id)
    
    def getuser_id(self):
        return self._data['userID']

    def setfirst_name(self, first_name):
        self._data['firstName'] = first_name

    def getfirst_name(self):
        return self._data['firstName']

    def setlast_name(self, last_name):
        self._data['lastName'] = last_name

    def getlast_name(self):
        return self._data['lastName']

    def setemail(self, email):
        self._data['email'] = email

    def getemail(self):
        return self._data['email']

    def setphone(self, phone):
        self._data['phone'] = phone

    def getphone(self):
        return self._data['phone']
    
    def setuser_status(self, user_status):
        self._data['userStatus'] = user_status

    def getuser_status(self):
        return self._data['userStatus']

    def __init__(self, dict_data):
        self.setuser_id(dict_data['userID'])
        self.setfirst_name(dict_data['firstName'])
        self.setlast_name(dict_data['lastName'])
        self.setemail(dict_data['email'])
        self.setphone(dict_data['phone'])
        self.setuser_status(dict_data['userStatus'])
        
    def get_dict(self):
        user_dict = {
            'userID': self.getuser_id(),
            'firstName': self.getfirst_name(),
            'lastName': self.getlast_name(),
            'email': self.getemail(),
            'phone': self.getphone(),
            'userStatus': self.getuser_status()
        }
        return user_dict


# Data Access Object Interface for User
class UserDAO:

    @staticmethod
    def set(user):
        """
        Writing user data to Datastore
        :rtype : int
        """
        ds = datastore.Client()
        try:
            entity = datastore.Entity(key=ds.key(_DATASTORE_KIND_USERS, user.getuser_id()))
            entity.update({
                'firstName': user.getfirst_name(),
                'lastName': user.getlast_name(),
                'email': user.getemail(),
                'phone': user.getphone(),
                'userStatus': user.getuser_status(),
                'timestamp': datetime.now()
            })
            ds.put(entity)
        except:
            return 1
        return 0

    @staticmethod
    def get(user_id):
        """
        Get a single algorithm data from Datastore
        :rtype : User
        """
        ds = datastore.Client()
        try:
            key = ds.key(_DATASTORE_KIND_USERS, user_id)
            entity = ds.get(key)
            entity.pop('timestamp')
        except:
            return 1
        entity['userID'] = user_id
        return User(entity)

# Dataset class
class Dataset:
    _data = {
        #    "dataset_id": "string",
        #    "summary": "string",
        #    "display_name": "string",
        #    "link_url": "string",
        #    "blob": "string",
        #    "description": "string"
    }

    def setdataset_id(self, dataset_id):
        self._data['dataset_id'] = dataset_id

    def getdataset_id(self):
        return self._data['dataset_id']

    def setsummary(self, summary):
        self._data['summary'] = summary

    def getsummary(self):
        return self._data['summary']

    def setdisplay_name(self, display_name):
        self._data['display_name'] = display_name

    def getdisplay_name(self):
        return self._data['display_name']

    def setlink_url(self, link_url):
        self._data['link_url'] = link_url

    def getlink_url(self):
        return self._data['link_url']

    def setblob(self, blob):
        self._data['blob'] = blob

    def getblob(self):
        return self._data['blob']

    def setdescription(self, description):
        self._data['description'] = description

    def getdescription(self):
        return self._data['description']

    def __init__(self, dict_data):
        self.setdataset_id(dict_data['datasetId'])
        self.setsummary(dict_data['datasetSummary'])
        self.setdisplay_name(dict_data['displayName'])
        self.setlink_url(dict_data['linkURL'])
        self.setblob(dict_data['datasetBLOB'])
        self.setdescription(dict_data['datasetDescription'])

    def get_dict(self):
        dataset_dict = {
            'datasetId': self.getdataset_id(),
            'datasetSummary': self.getsummary(),
            'displayName': self.getdisplay_name(),
            'linkURL': self.getlink_url(),
            'algorithmBLOB': self.getblob(),
            'algorithmDescription': self.getdescription(),
            'datasetDescription': self.getdataset_description()
        }
        return dataset_dict


# Algorithm class
class Algorithm:
    _data = {
        #    "algorithm_id": "string",
        #    "summary": "string",
        #    "display_name": "string",
        #    "link_url": "string",
        #    "blob": "string",
        #    "description": "string",
        #    "dataset_description": "string",
    }

    def setalgorithm_id(self, algorithm_id):
        self._data['algorithm_id'] = algorithm_id

    def getalgorithm_id(self):
        return self._data['algorithm_id']

    def setsummary(self, summary):
        self._data['summary'] = summary

    def getsummary(self):
        return self._data['summary']

    def setdisplay_name(self, display_name):
        self._data['display_name'] = display_name

    def getdisplay_name(self):
        return self._data['display_name']

    def setlink_url(self, link_url):
        self._data['link_url'] = link_url

    def getlink_url(self):
        return self._data['link_url']

    def setblob(self, blob):
        self._data['blob'] = blob

    def getblob(self):
        return self._data['blob']

    def setdescription(self, description):
        self._data['description'] = description

    def getdescription(self):
        return self._data['description']

    def setdataset_description(self, dataset_description):
        self._data['dataset_description'] = dataset_description

    def getdataset_description(self):
        return self._data['dataset_description']

    def __init__(self, dict_data):
        self.setalgorithm_id(dict_data['algorithmId'])
        self.setsummary(dict_data['algorithmSummary'])
        self.setdisplay_name(dict_data['displayName'])
        self.setlink_url(dict_data['linkURL'])
        self.setblob(dict_data['algorithmBLOB'])
        self.setdescription(dict_data['algorithmDescription'])
        self.setdataset_description(dict_data['datasetDescription'])

    def get_dict(self):
        algorithm_dict = {
            'algorithmId': self.getalgorithm_id(),
            'algorithmSummary': self.getsummary(),
            'displayName': self.getdisplay_name(),
            'linkURL': self.getlink_url(),
            'algorithmBLOB': self.getblob(),
            'algorithmDescription': self.getdescription(),
            'datasetDescription': self.getdataset_description()
        }
        return algorithm_dict


class AlgorithmDAO:
    """
    Data Access Object Interface for Algorithm

    aaa
    """

    @staticmethod
    def setindex(algorithm):
        """
        Writes algorithm to search database in standard

        :param algorithm: an algorithm to be written
        :type algorithm: Algorithm
        :returns: 2 - Connection Error, 1 - other status_code then 200, 0 - EOK
        :rtype: int
        """
        url = get_search_url()
        index_data = {"algorithmId": algorithm.getalgorithm_id(),
                      "algorithmSummary": algorithm.getsummary(),
                      "displayName": algorithm.getdisplay_name(),
                      "linkURL": algorithm.getlink_url()}
        try:
            response = requests.post(url, json=index_data, headers={'Content-Type': 'application/json; charset=utf-8'})
        except requests.ConnectionError:
            return 2
        if response.status_code != 200:
            return 1
        return 0

    @staticmethod
    def setdata(algorithm):
        """
        Writing main blob algorithm data to Datastore

        :param algorithm: an algorithm to be written
        :type algorithm: Algorithm
        :returns: 1 - Error, 0 - EOK
        :rtype: int
        """
        ds = datastore.Client()
        try:
            entity = datastore.Entity(key=ds.key(_DATASTORE_KIND_ALGORITHMS, algorithm.getalgorithm_id()))
            entity.update({
                'algorithmBLOB': algorithm.getblob(),
                'algorithmDescription': algorithm.getdescription(),
                'datasetDescription': algorithm.getdataset_description(),
                'timestamp': datetime.now()
            })
            ds.put(entity)
        except:
            return 1
        return 0

    @staticmethod
    def set(algorithm):
        """
        Writing the whole algorithm partly to index in Full Text Search and mainly to Datastore

        :param algorithm: an algorithm to be written
        :type algorithm: Algorithm
        :returns: 0 - EOK, first digit Datastore error code, second digit search GAE error code
        :rtype: int

        .. todo:: set digits according to returns description
        """
        idx = AlgorithmDAO.setindex(algorithm)
        if idx == 0:
            dat = AlgorithmDAO.setdata(algorithm)
        else:
            dat = 2
        return 10 * dat + idx

    @staticmethod
    def searchindex(found_algorithms_list, tags=''):
        """
        Search for algorithms in index from Full Text Search and write into found_algorithms_list

        :rtype : int
        :returns: 0 OK, 1 Malformed query in uri, 2 Connection error, 3 Application or server error
        """
        url = get_search_url()
        if tags != '':
            query_string = ' OR '.join(tags.split(','))
            url += '?query=' + query_string
        try:
            response_from_url = requests.get(url)
        except requests.ConnectionError:
            return 2
        if response_from_url.status_code > 499:
            # server error 500 and above
            return 3
        if response_from_url.status_code != 200:
            return 1
        # to pass list by reference one can't touch the outer list one can only append or extend
        # it's a major distinction of python from real programming languages like C
        try:
            js = json.loads(response_from_url.text)
            found_algorithms_list.extend(js)
        except:
            return 3
        return 0

    @staticmethod
    def getindex(algorithm_id):
        """
        Get a single algorithm data from GAE Search

        :param algorithm_id: id of an algorithm to be retrieved
        :type algorithm_id: str
        :rtype : dict
        :returns: dictionary of a single algorithm index
        """
        url = get_search_url() + '/algorithms/' + algorithm_id
        try:
            response_from_url = requests.get(url)
        except requests.ConnectionError:
            return 2
        if response_from_url.status_code != 200:
            return 1
        algorithm_index_dict = json.loads(response_from_url.text)
        return algorithm_index_dict

    @staticmethod
    def getdata(algorithm_id):
        """
        Get a single algorithm data from Datastore

        :param algorithm_id: id of an algorithm to be retrieved
        :type algorithm_id: str
        :returns: dictionary of a single algorithm data or 1 - Error
        :rtype : dict, int
        """
        ds = datastore.Client()
        try:
            key = ds.key(_DATASTORE_KIND_ALGORITHMS, algorithm_id)
            entity = ds.get(key)
            entity.pop('timestamp')
        except:
            return 1
        return entity

    @staticmethod
    def get(algorithm_id):
        """
        Get specific algorithm data

        :param algorithm_id: id of an algorithm to be retrieved
        :type algorithm_id: str
        :returns: Algorithm object or 1 - GAE search Error or 2 - Datastore Error
        :rtype : Algorithm, int
        """
        idx = AlgorithmDAO.getindex(algorithm_id)
        if idx in [1, 2]:
            return 1
        dat = AlgorithmDAO.getdata(algorithm_id)
        if dat == 1:
            return 2
        idx.update(dat)
        found_algorithm = Algorithm(idx)
        return found_algorithm

class DatasetDAO:
    """
    Data Access Object Interface for Dataset
    """

    @staticmethod
    def setindex(dataset):
        """
        Writes algorithm to search database in standard

        :param algorithm: an algorithm to be written
        :type algorithm: Algorithm
        :returns: 2 - Connection Error, 1 - other status_code then 200, 0 - EOK
        :rtype: int
        """
        url = get_search_url()
        index_data = {"datasetId": dataset.getalgorithm_id(),
                      "datasetSummary": dataset.getsummary(),
                      "displayName": dataset.getdisplay_name(),
                      "linkURL": dataset.getlink_url()}
        try:
            response = requests.post(url, json=index_data, headers={'Content-Type': 'application/json; charset=utf-8'})
        except requests.ConnectionError:
            return 2
        if response.status_code != 200:
            return 1
        return 0

    @staticmethod
    def setdata(dataset):
        """
        Writing main blob dataset data to Datastore

        :param dataset: a dataset to be written
        :type dataset: Dataset
        :returns: 1 - Error, 0 - EOK
        :rtype: int
        """
        ds = datastore.Client()
        try:
            entity = datastore.Entity(key=ds.key(_DATASTORE_KIND_DATASETS, dataset.getdataset_id()))
            entity.update({
                'datasetBLOB': dataset.getblob(),
                'datasetDescription': dataset.getdescription(),
                'timestamp': datetime.now()
            })
            ds.put(entity)
        except:
            return 1
        return 0

    @staticmethod
    def set(dataset):
        """
        Writing the whole algorithm partly to index in Full Text Search and mainly to Datastore

        :param dataset: a dataset to be written
        :type dataset: Dataset
        :returns: 0 - EOK, first digit Datastore error code, second digit search GAE error code
        :rtype: int

        .. todo:: set digits according to returns description
        """
        idx = DatasetDAO.setindex(dataset)
        if idx == 0:
            dat = DatasetDAO.setdata(dataset)
        else:
            dat = 2
        return 10 * dat + idx

    @staticmethod
    def searchindex(found_datasets_list, tags=''):
        """
        Search for datasets in index from Full Text Search and write into found_datasets_list

        :rtype : int
        :returns: 0 OK, 1 Malformed query in uri, 2 Connection error, 3 Application or server error
        """
        url = get_search_url()
        if tags != '':
            query_string = ' OR '.join(tags.split(','))
            url += '?query=' + query_string
        try:
            response_from_url = requests.get(url)
        except requests.ConnectionError:
            return 2
        if response_from_url.status_code > 499:
            # server error 500 and above
            return 3
        if response_from_url.status_code != 200:
            return 1
        # to pass list by reference one can't touch the outer list one can only append or extend
        # it's a major distinction of python from real programming languages like C
        try:
            js = json.loads(response_from_url.text)
            found_datasets_list.extend(js)
        except:
            return 3
        return 0

    @staticmethod
    def getindex(dataset_id):
        """
        Get a single algorithm data from GAE Search

        :param dataset_id: id of an algorithm to be retrieved
        :type dataset_id: str
        :rtype : dict
        :returns: dictionary of a single algorithm index
        """
        url = get_search_url() + '/datasets/' + dataset_id
        try:
            response_from_url = requests.get(url)
        except requests.ConnectionError:
            return 2
        if response_from_url.status_code != 200:
            return 1
        dataset_index_dict = json.loads(response_from_url.text)
        return dataset_index_dict

    @staticmethod
    def getdata(dataset_id):
        """
        Get a single algorithm data from Datastore

        :param dataset_id: id of an dataset to be retrieved
        :type dataset_id: str
        :returns: dictionary of a single dataset data or 1 - Error
        :rtype : dict, int
        """
        ds = datastore.Client()
        try:
            key = ds.key(_DATASTORE_KIND_DATASETS, dataset_id)
            entity = ds.get(key)
            entity.pop('timestamp')
        except:
            return 1
        return entity

    @staticmethod
    def get(dataset_id):
        """
        Get specific algorithm data

        :param dataset_id: id of an dataset to be retrieved
        :type dataset_id: str
        :returns: Dataset object or 1 - GAE search Error or 2 - Datastore Error
        :rtype : Dataset, int
        """
        idx = DatasetDAO.getindex(dataset_id)
        if idx in [1, 2]:
            return 1
        dat = DatasetDAO.getdata(dataset_id)
        if dat == 1:
            return 2
        idx.update(dat)
        found_dataset = Dataset(idx)
        return found_dataset



