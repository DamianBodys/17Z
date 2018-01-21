import unittest
import requests
import dao
from main import get_flexible_url
from google.cloud import datastore


class WrongStatusCodeError(Exception):
    """
    Exception raised when Http status code is greater then 399 -> Http Errors

    Attributes:
        returned_http_status_code (int): http status code
        message (str): message

    """
    def __init__(self, returned_http_status_code, message='Http status code from Search GAE > 399 - check ' + dao.get_search_url()):
        """
        Exception constructor

        Args:
            returned_http_status_code (int): http status code
            message (str):  message
        """
        self.returned_http_status_code = returned_http_status_code
        self.message = message


class SearchConnectionError(requests.RequestException):
    """
    Exception rised by requests to Search Database in GAE standard
    """


def create_test_search_algorithm_dict(id_number):
    """
    Creates part of the algorithm for search GAE app for testing purposes

    Args:
        id_number (int): number of an algorithm to be created

    Returns:
        dict: algorithm as dictionary

    """
    data = {}
    data['algorithmId'] = 'algorithmId' + str(id_number)
    data['algorithmSummary'] = 'algorithmSummary' + str(id_number)
    data['displayName'] = 'displayName' + str(id_number)
    data['linkURL'] = get_flexible_url() + '/algorithms/' + data['algorithmId']
    return data


def create_test_search_algorithm_list(length):
    """
    Generate test data for search GAE as list by name data_list given by reference of length algorithm descriptions

    Args:
        length (int): the length of the list to generate

    Returns:
        list: generated list of algorithm indexes

    """
    data_list = []
    for i in range(length):
        data_list.append(create_test_search_algorithm_dict(i))
    return data_list


def save_test_list_to_search_app(data_list):
    """
    Saves test algorithms to search GAE application

    Args:
        data_list (list): the list of algorithmss to be written to search GAE application

    Raises:
        SearchConnectionError: requests.ConnectionError
        WrongStatusCodeError: errors from Search GAE standard

    """
    url = dao.get_search_url()
    for item in data_list:
        index_data = {"algorithmId": item["algorithmId"],
                      "algorithmSummary": item["algorithmSummary"],
                      "displayName": item["displayName"],
                      "linkURL": item["linkURL"]}
        try:
            response = requests.post(url, json=index_data, headers={'Content-Type': 'application/json; charset=utf-8'})
        except SearchConnectionError:
            raise
        if response.status_code > 399:
            raise WrongStatusCodeError(response.status_code)


def del_all_from_datastore():
    """
    Delete everything from datastore

    Retrieves all kinds from datastore and for each kind deletes all entities
    """
    ds = datastore.Client()
    q = ds.query(kind='__kind__')
    q.keys_only()
    kinds = []
    for entity in q.fetch():
        kinds.append(entity.key.id_or_name)
    for k in kinds:
        qk = ds.query(kind=k)
        qk.keys_only()
        kys = []
        for ent in qk.fetch():
            kys.append(ent.key)
        ds.delete_multi(kys)


def del_all_from_search():
    """
    Deletes everything from standard GAE search application

    Sends http DELETE to GAE search application

    :returns: string 'Everything deleted OK' if EOK or other if Search in GAE Standard didn't behave as expected
    :rtype: str
    """
    url = dao.get_search_url()
    try:
        response = requests.delete(url)
    except requests.ConnectionError:
        return 'Can not connect to GAE Standard Search'
    if response.status_code != 200:
        return 'GAE Standard Error - did not return 200'
    return 'Everything deleted OK'


def del_all():
    """
    Clears all databases for testing purposes to start from scratch.

    :returns: string 'Everything deleted OK' if EOK or other if Search in GAE Standard didn't behave as expected
    :rtype: str

    :Example:

    >>>import test_dao
    >>>test_dao.del_all()
    Everything deleted OK

    """

    del_all_from_datastore()
    return del_all_from_search()


class DaoUnittestAlgorithmDaoTestCase(unittest.TestCase):
    """Tests of all static methods of class AlgorithmDAO"""
    def setUp(self):
        """Deletes everything from all databases"""
        if del_all() != 'Everything deleted OK':
            self.fail("there was a problem while deleting everything check if search GAE standard app is OK?" +
                      dao.get_search_url())

    def test_AlgorithmDAO_searchindex_Empty(self):
        """ checks if from empty Search database nothing is returned and statuscode =0"""
        right_algorithm_list = []
        test_algorithm_list = []
        ret_code = dao.AlgorithmDAO.searchindex(test_algorithm_list)
        self.assertNotEqual(2, ret_code, msg='Can not connect to search GAE standard - check ' + dao.get_search_url())
        self.assertEqual(0, ret_code, msg='Wrong status Code')
        self.assertCountEqual(right_algorithm_list, test_algorithm_list)

    def test_AlgorithmDAO_searchindex_EmptyWithTags(self):
        """ checks if from empty Search database nothing is returned and statuscode =0"""
        tags = 'algo,rithm'
        right_algorithm_list = []
        test_algorithm_list = []
        ret_code = dao.AlgorithmDAO.searchindex(test_algorithm_list, tags=tags)
        self.assertNotEqual(2, ret_code, msg='Can not connect to search GAE standard - check ' + dao.get_search_url())
        self.assertEqual(0, ret_code, msg='Wrong status Code')
        self.assertCountEqual(right_algorithm_list, test_algorithm_list)

    def test_AlgorithmDAO_searchindex_1Algorithm(self):
        """ checks if from 1 algorithm Search database exactly 1 algorithm is returned and statuscode =0"""
        right_algorithm_list = create_test_search_algorithm_list(1)
        url = dao.get_search_url()
        index_data = {"algorithmId": right_algorithm_list[0]["algorithmId"],
                      "algorithmSummary": right_algorithm_list[0]["algorithmSummary"],
                      "displayName": right_algorithm_list[0]["displayName"],
                      "linkURL": right_algorithm_list[0]["linkURL"]}
        try:
            response = requests.post(url, json=index_data, headers={'Content-Type': 'application/json; charset=utf-8'})
        except SearchConnectionError:
            self.fail(msg='Can not connect to search GAE standard while adding test data - check ' + dao.get_search_url())
        if response.status_code != 200:
            self.fail(msg='Wrong status code while adding test data to search GAE standard ' + dao.get_search_url())
        test_algorithm_list = []
        ret_code = dao.AlgorithmDAO.searchindex(test_algorithm_list)
        self.assertNotEqual(2, ret_code, msg='Can not connect to search GAE standard - check ' + dao.get_search_url())
        self.assertEqual(0, ret_code, msg='Wrong status Code')
        self.assertCountEqual(right_algorithm_list, test_algorithm_list)

    def test_AlgorithmDAO_searchindex_300Algorithms(self):
        """ checks if from 300 algorithms Search database exactly 300 algorithms is returned and statuscode =0"""
        right_algorithm_list = []
        create_test_search_algorithm_list(300)
        result = save_test_list_to_search_app(right_algorithm_list)
        if result == 2:
            self.fail(msg='Can not connect to search GAE standard while adding test data - check ' + dao.get_search_url())
        elif result == 1:
            self.fail(msg='Wrong status code while adding test data to search GAE standard ' + dao.get_search_url())
        test_algorithm_list = []
        ret_code = dao.AlgorithmDAO.searchindex(test_algorithm_list)
        self.assertNotEqual(2, ret_code, msg='Can not connect to search GAE standard - check ' + dao.get_search_url())
        self.assertEqual(0, ret_code, msg='Wrong status Code')
        self.assertCountEqual(right_algorithm_list, test_algorithm_list)

    def test_AlgorithmDAO_searchindex_300AlgorithmsWithTag(self):
        """ checks if from 300 algorithms Search database exactly 1 algorithm is returned  'algorithm69' by searching
        for tag 'algorithmSummary69'"""
        searched_string = 'algorithmSummary69'
        right_algorithm_list = create_test_search_algorithm_list(300)
        result = save_test_list_to_search_app(right_algorithm_list)
        expected_list=[]
        expected_list.append(right_algorithm_list[69])
        if result == 2:
            self.fail(msg='Can not connect to search GAE standard while adding test data - check ' + dao.get_search_url())
        elif result == 1:
            self.fail(msg='Wrong status code while adding test data to search GAE standard ' + dao.get_search_url())
        test_algorithm_list = []
        ret_code = dao.AlgorithmDAO.searchindex(test_algorithm_list, tags=searched_string)
        self.assertNotEqual(2, ret_code, msg='Can not connect to search GAE standard - check ' + dao.get_search_url())
        self.assertEqual(0, ret_code, msg='Wrong status Code')
        self.assertCountEqual(expected_list, test_algorithm_list)

    def test_AlgorithmDAO_getindex_Empty(self):
        """checks if from empty Search database returns other status code then 200 so getindex returns 1"""
        algorithm_id_to_get = 'algorithmId0'
        returned = dao.AlgorithmDAO.getindex(algorithm_id_to_get)
        self.assertNotEqual(2, returned, msg='Can not connect to search GAE standard - check ' + dao.get_search_url())
        self.assertEqual(1, returned, msg='Wrongly status Code returned from empty GAE standard is 200')

    def test_AlgorithmDAO_getindex_NotFound(self):
        """
        checks if get of nonexistent algorithmID Search database returns other status code then 200
        so getindex returns 1
        """
        list_of_algorithms_to_put = []
        create_test_search_algorithm_list(5)
        save_test_list_to_search_app(list_of_algorithms_to_put)
        algorithm_id_to_get = 'WrongAlgorithmID'
        returned = dao.AlgorithmDAO.getindex(algorithm_id_to_get)
        self.assertNotEqual(2, returned, msg='Can not connect to search GAE standard - check ' + dao.get_search_url())
        self.assertEqual(1, returned, msg='Wrongly status Code returned from GAE standard is 200')

    def test_AlgorithmDAO_getindex_Found(self):
        """
        checks if get of existent algorithmID Search database returns correct data
        """
        list_of_algorithms_to_put = create_test_search_algorithm_list(5)
        try:
            save_test_list_to_search_app(list_of_algorithms_to_put)
        except WrongStatusCodeError as err:
            self.fail(err.message)
        except SearchConnectionError:
            self.fail('Can not connect to search GAE standard - check ' + dao.get_search_url())
        algorithm_id_to_get = 'algorithmId2'
        right_dict = create_test_search_algorithm_dict(2)
        returned = dao.AlgorithmDAO.getindex(algorithm_id_to_get)
        self.assertDictEqual(right_dict, returned, msg='Returned data is not as expected')

    def test_AlgorithmDAO_getdata_Empty(self):
        """Search algorithmid from empty Datastore and return error"""
        algorithm_id_to_get = 'algorithmId2'
        returned = dao.AlgorithmDAO.getdata(algorithm_id_to_get)
        self.assertEqual(1, returned, msg='Wrongly error status Code not returned from Datastore')

    def test_AlgorithmDAO_getdata_NotFound(self):
        """Search nonexistent algorithmid from empty Datastore and return error"""
        algorithm_id_to_get = 'Wrong algorithmId'
        #TODO: add data to Datastore
        returned = dao.AlgorithmDAO.getdata(algorithm_id_to_get)
        self.assertEqual(1, returned, msg='Wrongly error status Code not returned from Datastore')


if __name__ == '__main__':
    unittest.main()
