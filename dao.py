__author__ = 'jan'
import requests
import json
from google.cloud import datastore
from datetime import datetime

# this is an address of standard appengine app to access Full Text Search
_ALGORITHM_SEARCH_URL = 'localhost:8080'
# name of kind to store algorithm data in Datastore
_DATASTORE_KIND = 'algorithms'


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


# Data Access Object Interface for Algorithm
class AlgorithmDAO:
    @staticmethod
    def setindex(algorithm):
        url = 'http://' + _ALGORITHM_SEARCH_URL
        index_data = {"algorithmId": algorithm.getalgorithm_id(),
                      "algorithmSummary": algorithm.getsummary(),
                      "displayName": algorithm.getdisplay_name(),
                      "linkURL": algorithm.getlink_url()}
        try:
            response = requests.post(url, json=index_data, headers={'content-type': 'application/json'})
        except requests.ConnectionError:
            return 2
        if response.status_code != 200:
            return 1
        return 0

    @staticmethod
    def setdata(algorithm):
        """
        Writing main blob algorithm data to Datastore
        :rtype : int
        """
        ds = datastore.Client()
        try:
            entity = datastore.Entity(key=ds.key(_DATASTORE_KIND, algorithm.getalgorithm_id()))
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
        Writing whole algorithm partly to index in Full Text Search and mainly to Datastre
        :rtype : int
        """
        idx = AlgorithmDAO.setindex(algorithm)
        if idx == 0:
            dat = AlgorithmDAO.setdata(algorithm)
        else:
            dat = 2
        return idx + 10 * dat

    @staticmethod
    def searchindex(found_algorithms_list, tags=''):
        """
        search for algorithms in index from Full Text Search
        :rtype : int
        """
        url = 'http://' + _ALGORITHM_SEARCH_URL
        if tags != '':
            query_string = ' OR '.join(tags.split(','))
            url += '?query=' + query_string
        try:
            response_from_url = requests.get(url)
        except requests.ConnectionError:
            return 2
        if response_from_url.status_code != 200:
            return 1
        # to pass list by reference one can't touch the outer list one can only append or extend
        # it's a major distinction of python from real programming languages
        found_algorithms_list.extend(json.loads(response_from_url.text))
        return 0

    @staticmethod
    def getindex(algorithm_id):
        """
        :rtype : dict : dictionary of a single algorithm index
        """
        url = 'http://' + _ALGORITHM_SEARCH_URL + '/algorithms/' + algorithm_id
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
        :rtype : dict
        """
        ds = datastore.Client()
        try:
            key = ds.key(_DATASTORE_KIND, algorithm_id)
            entity = ds.get(key)
            entity.pop('timestamp')
        except:
            return 1
        return entity

    @staticmethod
    def get(algorithm_id):
        """
        :rtype : Algorithm
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
