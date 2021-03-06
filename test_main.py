"""It's very important to install in virtualenv
pip install WebTest
"""
import unittest
import webtest
import main


class MainHTTPTestCase(unittest.TestCase):
    def setUp(self):
        self.test_app = webtest.TestApp(main.app)

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


if __name__ == '__main__':
    unittest.main()
