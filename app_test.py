from app import app
import unittest


class FlaskAppTest(unittest.TestCase):
    def test_index_found(self):
        test_client = app.test_client()
        rv = test_client.get('/')
        self.assertEqual(rv.status, '200 OK')

    def test_sheet_not_found(self):
        test_client = app.test_client()
        rv = test_client.get('/cheatsheet/404')
        self.assertEqual(rv.status, '404 NOT FOUND')

    def test_no_such_api(self):
        test_client = app.test_client()
        rv = test_client.get('/spam')
        self.assertEqual(rv.status, '404 NOT FOUND')


if __name__ == "__main__":
    unittest.main()
