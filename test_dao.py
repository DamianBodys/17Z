import unittest
import requests
import dao
from google.cloud import datastore


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


if __name__ == '__main__':
    unittest.main()
