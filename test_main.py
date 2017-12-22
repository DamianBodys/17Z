"""It's very important to install in virtualenv
pip install WebTest
"""
import unittest
import webtest
import main


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.testapp = webtest.TestApp(main.app)

    def tearDown(self):
        pass

    def test_algorithms_GET_Empty(self):
        response = self.testapp.get('/algorithms/')
        self.assertEqual(200, response.status_int)
        self.assertIsNotNone(response.charset, msg='There is no charset in response')
        self.assertEqual('[]', response.normal_body.decode(encoding=response.charset))
        self.assertEqual('application/json', response.content_type)


if __name__ == '__main__':
    unittest.main()
