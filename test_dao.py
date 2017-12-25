import unittest
import dao


class DaoUnittestAlgorithmDaoTestCase(unittest.TestCase):
    def test_AlgorithmDAO_searchindex_Empty(self):
        """ checks if from empty Search database nothing is returned and statuscode =0"""
        right_algorithm_list = []
        test_algorithm_list = []
        ret_code = dao.AlgorithmDAO.searchindex(test_algorithm_list)
        self.assertNotEqual(2, ret_code, msg='Can not connect to search GAE standard - check ' + dao._ALGORITHM_SEARCH_URL)
        self.assertEqual(0, ret_code, msg='Wrong status Code')
        self.assertCountEqual(right_algorithm_list, test_algorithm_list)

    def test_AlgorithmDAO_searchindex_EmptyWithTags(self):
        """ checks if from empty Search database nothing is returned and statuscode =0"""
        tags = 'algo,rithm'
        right_algorithm_list = []
        test_algorithm_list = []
        ret_code = dao.AlgorithmDAO.searchindex(test_algorithm_list,tags=tags)
        self.assertNotEqual(2, ret_code, msg='Can not connect to search GAE standard - check ' + dao._ALGORITHM_SEARCH_URL)
        self.assertEqual(0, ret_code, msg='Wrong status Code')
        self.assertCountEqual(right_algorithm_list, test_algorithm_list)


if __name__ == '__main__':
    unittest.main()
