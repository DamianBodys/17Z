"""It's very important to install in virtualenv
pip install WebTest
"""
import unittest
import webtest
import main
from test_auth import get_id_token_for_testing
from test_dao import del_all
import xml.etree.cElementTree as ET


class AlgorithmHTTPTestCase(unittest.TestCase):
    def setUp(self):
        self.test_app = webtest.TestApp(main.app)
        del_all()

    def test_algorithms_GET_Empty(self):
        """Tests empty database"""
        response = self.test_app.get('/algorithms/')
        self.assertEqual(200, response.status_int)
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('[]', response.normal_body.decode(encoding=response.charset))
        self.assertEqual('application/json', response.content_type)

    def test_algorithms_GET_EmptyWith1Tag(self):
        """Test Get with tags on empty database"""
        response = self.test_app.get('/algorithms/', params={'tags': 'algorithm'})
        self.assertEqual(200, response.status_int)
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('[]', response.normal_body.decode(encoding=response.charset))
        self.assertEqual('application/json', response.content_type)

    def test_algorithms_GET_EmptyWith2Tags(self):
        """Test Get with tags on empty database"""
        response = self.test_app.get('/algorithms/', params={'tags': 'algorithm,data'})
        self.assertEqual(200, response.status_int)
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('[]', response.normal_body.decode(encoding=response.charset))
        self.assertEqual('application/json', response.content_type)

    def test_algorithms_GET_EmptyWith2TagsAndSpace(self):
        """Test Get with tags on empty database"""
        response = self.test_app.get('/algorithms/', params={'tags': 'algorithm, data'})
        self.assertEqual(200, response.status_int)
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('[]', response.normal_body.decode(encoding=response.charset))
        self.assertEqual('application/json', response.content_type)

    def test_algorithms_GET_EmptyWithEmptyTags(self):
        """Test Get with tags on empty database"""
        response = self.test_app.get('/algorithms/', params={'tags': ''})
        self.assertEqual(200, response.status_int)
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('[]', response.normal_body.decode(encoding=response.charset))
        self.assertEqual('application/json', response.content_type)

    def test_algorithms_GET_EmptyWithWrongTagsJustSpaceChar(self):
        """Test Get with tags on empty database with space in empty looking tags parameter"""
        response = self.test_app.get('/algorithms/', params={'tags': ' '}, expect_errors=True)
        self.assertEqual(400, response.status_int, msg='Wrong response status')
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('application/json', response.content_type)

    def test_algorithms_GET_EmptyWithWrongTagsJustComaChar(self):
        """Test Get with tags on empty database with coma in empty looking tags parameter"""
        response = self.test_app.get('/algorithms/', params={'tags': ','}, expect_errors=True)
        self.assertEqual(400, response.status_int, msg='Wrong response status')
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('application/json', response.content_type)

    def test_algorithms_GET_EmptyWithWrongTagsJustComaAndSpaceChar(self):
        """Test Get with tags on empty database with empty looking tags parameter"""
        response = self.test_app.get('/algorithms/', params={'tags': ', '}, expect_errors=True)
        self.assertEqual(400, response.status_int, msg='Wrong response status')
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('application/json', response.content_type)

    def test_algorithms_GET_EmptyWithWrongTagsJustSpaceComaAndSpaceChars(self):
        """Test Get with tags on empty database with empty looking tags parameter"""
        response = self.test_app.get('/algorithms/', params={'tags': ' , '}, expect_errors=True)
        self.assertEqual(400, response.status_int, msg='Wrong response status')
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('application/json', response.content_type)

    def test_algorithms_GET_EmptyWithWrongTags(self):
        """Test Get with tags on empty database with wrong tags (space delimited)"""
        response = self.test_app.get('/algorithms/', params={'tags': 'algorithm data'}, expect_errors=True)
        self.assertEqual(400, response.status_int, msg='Wrong response status')
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('application/json', response.content_type)


class BillingHTTPTestCase(unittest.TestCase):
    def setUp(self):
        self.test_app = webtest.TestApp(main.app)

    def test_bill_GET(self):
        """ Test normal GET - it should receive mok-up data"""
        self.test_app.authorization = ('Bearer', get_id_token_for_testing())
        response = self.test_app.get('/bill/')
        self.assertEqual(200, response.status_int, msg='Wrong response status')
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('text/xml', response.content_type)


    def test_bill_with_period_GET(self):
        """ Test normal GET - it should receive mok-up data"""
        self.test_app.authorization = ('Bearer', get_id_token_for_testing())
        begin = '20180402'
        end = '20180403'
        response = self.test_app.get('/bill/', params={'begin': begin, 'end': end})
        self.assertEqual(200, response.status_int, msg='Wrong response status')
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('text/xml', response.content_type)
        self.assertEqual(begin,response.xml.findall('./head/period/begin')[0].text)
        self.assertEqual(end, response.xml.findall('./head/period/end')[0].text)


    def test_bill_with_resultsetid_GET(self):
        """ Test normal GET - it should receive mok-up data"""
        self.test_app.authorization = ('Bearer', get_id_token_for_testing())
        resultsetid = 'ResultsetID'
        response = self.test_app.get('/bill/result/' + resultsetid)
        self.assertEqual(200, response.status_int, msg='Wrong response status')
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('text/xml', response.content_type)
        self.assertEqual(resultsetid,response.xml.findall('./head/billedobj')[0].text)


    def test_bill_with_algorithmid_GET(self):
        """ Test normal GET - it should receive mok-up data"""
        self.test_app.authorization = ('Bearer', get_id_token_for_testing())
        algorithmid = 'AlgorithmID'
        response = self.test_app.get('/bill/algorithm/' + algorithmid)
        self.assertEqual(200, response.status_int, msg='Wrong response status')
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('text/xml', response.content_type)
        self.assertEqual(algorithmid,response.xml.findall('./head/billedobj')[0].text)

if __name__ == '__main__':
    unittest.main()
