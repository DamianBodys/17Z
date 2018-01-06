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

    def test_algorithms_GET_EmptyWithTags(self):
        """TODO: not started just copied"""
        response = self.test_app.get('/algorithms/')
        self.assertEqual(200, response.status_int)
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('[]', response.normal_body.decode(encoding=response.charset))
        self.assertEqual('application/json', response.content_type)

if __name__ == '__main__':
    unittest.main()
