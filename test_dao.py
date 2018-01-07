import unittest
import requests
import dao
from main import get_flexible_url
from google.cloud import datastore


def create_test_search_algorithm_list(data_list, length):
    """Prepare test data for search GAE as list by name data_list given by reference
     of length algorithm descriptions"""
    for i in range(length):
        data={}
        data['algorithmId'] = 'algorithmId' + str(i)
        data['algorithmSummary'] = 'algorithmSummary' + str(i)
        data['displayName'] = 'displayName' + str(i)
        data['linkURL'] = get_flexible_url() + '/algorithms/' + data['algorithmId']
        data_list.append(data)


def save_test_list_to_search_app(data_list):
    """Saves test algorithms to search GAE application"""
    url = dao.get_search_url()
    for item in data_list:
        index_data = {"algorithmId": item["algorithmId"],
                      "algorithmSummary": item["algorithmSummary"],
                      "displayName": item["displayName"],
                      "linkURL": item["linkURL"]}
        try:
            response = requests.post(url, json=index_data, headers={'Content-Type': 'application/json; charset=utf-8'})
        except requests.ConnectionError:
            return 2
        if response.status_code != 200:
            return 1
    return 0

def del_all_from_datastore():
    """Delete everything from datastore"""
    # deleting all from datastore
    ds = datastore.Client()
    q = ds.query(kind='__kind__')
    q.keys_only()
    kinds = [entity.key.id_or_name for entity in q.fetch()]
    for k in kinds:
        qk = ds.query(kind=k)
        qk.keys_only()
        kys = [entity.key for entity in qk.fetch()]
        ds.delete_multi(kys)


def del_all_from_search():
    """deletes everything from standard GAE search application"""
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
    Clears all databases for testing purposes. To start from scratch.
    usage:
    from test_dao import del_all
    del_all()
    :return: string OK if EOK or other if Search in GAE Standard didn't behave as expected
    """
    del_all_from_datastore()
    return del_all_from_search()


class DaoUnittestAlgorithmDaoTestCase(unittest.TestCase):
    def setUp(self):
        if 'Everything deleted OK' != del_all():
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
        right_algorithm_list = []
        create_test_search_algorithm_list(right_algorithm_list, 1)
        url = dao.get_search_url()
        index_data = {"algorithmId": right_algorithm_list[0]["algorithmId"],
                      "algorithmSummary": right_algorithm_list[0]["algorithmSummary"],
                      "displayName": right_algorithm_list[0]["displayName"],
                      "linkURL": right_algorithm_list[0]["linkURL"]}
        try:
            response = requests.post(url, json=index_data, headers={'Content-Type': 'application/json; charset=utf-8'})
        except requests.ConnectionError:
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
        create_test_search_algorithm_list(right_algorithm_list, 300)
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
        right_algorithm_list = []
        create_test_search_algorithm_list(right_algorithm_list, 300)
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


if __name__ == '__main__':
    unittest.main()
