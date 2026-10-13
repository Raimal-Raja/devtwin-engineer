import unittest
from fastapi.testclient import TestClient
from app import app


class HttpContract(unittest.TestCase):
    def setUp(self):
        # Observe HTTP 500 rather than letting TestClient raise the server error.
        self.client = TestClient(app, raise_server_exceptions=False)
        self.addCleanup(self.client.close)

    def assert_total(self, body, total):
        response = self.client.post('/checkout', json=body)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json(), {'total': total})

    def test_missing_discount(self):
        self.assert_total({'subtotal': 100}, 100)

    def test_null_discount(self):
        self.assert_total({'subtotal': 100, 'discount': None}, 100)

    def test_explicit_discounts_and_floor(self):
        for discount, expected in [(0, 100), (25, 75), (150, 0)]:
            with self.subTest(discount=discount):
                self.assert_total({'subtotal': 100, 'discount': discount}, expected)

    def test_validation_contract(self):
        for body in [{}, {'subtotal': -1}, {'subtotal': '100'},
                     {'subtotal': True}, {'subtotal': 1, 'discount': -1},
                     {'subtotal': 1, 'discount': '0'}, {'subtotal': 1, 'extra': 2}]:
            with self.subTest(body=body):
                self.assertEqual(self.client.post('/checkout', json=body).status_code, 422)

    def test_health_preserved(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})


if __name__ == '__main__':
    unittest.main()
