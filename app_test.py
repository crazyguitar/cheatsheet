from app import app
import unittest
import os


class FlaskAppTest(unittest.TestCase):

    sheet_path = 'server/templates/cheatsheet'

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

    def test_sheets_exists(self):
        test_client = app.test_client()
        sheets = os.listdir(self.sheet_path)
        for _s in sheets:
            rv = test_client.get('/' + _s.replace('.html', ''))
            self.assertEqual(rv.status, '200 OK')


if __name__ == "__main__":
    unittest.main()
