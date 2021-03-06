from aiohttp import web
from aiohttp.abc import Application
from aiohttp.test_utils import AioHTTPTestCase

from main import get_tasks


class ScanTestCase(AioHTTPTestCase):
    async def get_application(self) -> Application:
        """
        Запуск приложения
        """
        app = web.Application()
        app.add_routes([web.get('/scan/{ip}/{begin_port}/{end_port}', get_tasks)])
        return app

    async def test_scan_true(self):
        """
        Тест успешного сканирования
        185.215.4.66 == ideco.ru
        """
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
        """
        Неправильный IP адресс
        """
        async with self.client.request('GET', '/scan/111.2222.44.33/1/8000') as response:
            self.assertEqual(response.status, 400)
            answer = await response.text()
            self.assertIn('400 bad request: illegal IP address string passed to inet_aton', answer)

    async def test_begin_port_is_not_int(self):
        """
        BEGIN_PORT не число
        """
        async with self.client.request('GET', '/scan/185.215.4.66/abc/2') as response:
            self.assertEqual(response.status, 400)
            answer = await response.text()
            self.assertIn('400 bad request: begin_port and end_port should consist of numbers only', answer)

    async def test_end_port_is_not_int(self):
        """
        END_PORT не число
        """
        async with self.client.request('GET', '/scan/185.215.4.66/1/abc') as response:
            self.assertEqual(response.status, 400)
            answer = await response.text()
            self.assertIn('400 bad request: begin_port and end_port should consist of numbers only', answer)

    async def test_big_begin_port(self):
        """
        BEGIN_PORT > END_PORT
        """
        async with self.client.request('GET', '/scan/185.215.4.66/8000/1') as response:
            self.assertEqual(response.status, 400)
            answer = await response.text()
            self.assertIn('400 bad request: begin_port cannot be greater than end_port and less than zero', answer)

    async def test_small_begin_port(self):
        """
        BEGIN_PORT < 0
        """
        async with self.client.request('GET', '/scan/185.215.4.66/-1/1') as response:
            self.assertEqual(response.status, 400)
            answer = await response.text()
            self.assertIn('400 bad request: begin_port cannot be greater than end_port and less than zero', answer)

    async def test_big_end_port(self):
        """
        END_PORT > 65535
        """
        async with self.client.request('GET', '/scan/185.215.4.66/1/65536') as response:
            self.assertEqual(response.status, 400)
            answer = await response.text()
            self.assertIn('400 bad request: end_port cannot be greater than 65535', answer)
