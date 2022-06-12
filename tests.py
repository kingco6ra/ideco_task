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
        async with self.client.request('GET', '/scan/185.215.4.66/79/81') as response:
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

    async def test_illgeal_ip(self):
        async with self.client.request('GET', '/scan/111.2222.44.33/1/8000') as response:
            self.assertEqual(response.status, 400)
            answer = await response.text()
            self.assertIn('400 bad request: illegal IP address string passed to inet_aton', answer)

    async def test_big_begin_port(self):
        async with self.client.request('GET', '/scan/185.215.4.66/8000/1') as response:
            self.assertEqual(response.status, 400)
            answer = await response.text()
            self.assertIn('400 bad request: begin_port cannot be greater than end_port and less than zero', answer)