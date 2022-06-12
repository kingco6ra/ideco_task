from aiohttp import web
from aiohttp.abc import Application
from aiohttp.test_utils import AioHTTPTestCase

from main import get_tasks


class ScannerPointTestCase(AioHTTPTestCase):
    async def get_application(self) -> Application:
        app = web.Application()
        app.add_routes([web.get('/scan/{ip}/{begin_port}/{end_port}', get_tasks)])
        return app

    async def test_scan_true(self):
        async with self.client.request('GET', f'/scan/185.215.4.66/79/81') as response:
            self.assertEqual(response.status, 200)
            answer = await response.json()

        self.assertIn(
            str([
                {"port": 79, "state": "close"},
                {"port": 80, "state": "open"},
                {"port": 81, "state": "close"}
            ]),
            str(answer)
        )

    async def test_scan_false(self):
        async with self.client.request('GET', '/scan/127.0.0.1/65555/65666') as response:
            self.assertEqual(response.status, 400)
            response = await response.text()
            self.assertIn('400 bad request: end_port cannot be greater than 65535', response)
