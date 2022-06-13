import asyncio
import logging
import socket
from time import time

from aiohttp import web


async def port_scan(ip, port, timeout) -> dict:
    """
    Открывается STREAM соединение с IP:PORT, и ожидается ответ в течении указанного TIMEOUT.
    Если TIMEOUT истекает, то для проверяемого порта возвращается словарь со значением {"state": "close"}, в ином случае
    {"state": "open"}.
    """
    info = {'port': port}
    connection = asyncio.open_connection(ip, port)
    try:
        await asyncio.wait_for(connection, timeout)
        info['state'] = 'open'
        logging.info(f"ip: {ip} port: {port} state: {info['state']}")
        connection.close()
    except:
        info['state'] = 'close'
    finally:
        return info


async def get_tasks(request: web.Request):
    """
     Извлекает IP, BEGIN_PORT, END_PORT из URL и отправляет их на валидацию.
     Затем запускается функция проверки для каждого порта.
     После проверки возвращается JSON ответ со статусами всех проверяемых портов.
     """
    start_time = time()
    ip = request.match_info['ip']
    begin_port = request.match_info['begin_port']
    end_port = request.match_info['end_port']
    begin_port, end_port, timeout = validate(ip, begin_port, end_port)

    tasks = [port_scan(ip, i, timeout) for i in range(begin_port, end_port + 1)]
    tasks = await asyncio.gather(*tasks)

    logging.info(msg=f'{end_port - begin_port} ports were scanned')
    logging.info(msg=f'{round(time() - start_time, 2)} seconds were spent on scanning')
    return web.json_response(tasks, status=200)


def validate(ip, begin_port, end_port) -> list[int]:
    """
    Введенные данные проверяются на наличие ошибок.
    Если находится хоть одна ошибка, то поднимается 400 BAD REQUEST.
     """
    try:
        socket.inet_aton(ip)
    except OSError as error:
        error = f'400 bad request: {str(error)}'
        logging.error(msg=error)
        raise web.HTTPBadRequest(text=error)

    try:
        begin_port = int(begin_port)
        end_port = int(end_port)
    except ValueError:
        error = '400 bad request: begin_port and end_port should consist of numbers only'
        logging.error(msg=error)
        raise web.HTTPBadRequest(text=error)

    if begin_port > end_port or begin_port < 0:
        error = '400 bad request: begin_port cannot be greater than end_port and less than zero'
        logging.error(msg=error)
        raise web.HTTPBadRequest(text=error)

    if end_port > 65535:
        error = '400 bad request: end_port cannot be greater than 65535'
        logging.error(msg=error)
        raise web.HTTPBadRequest(text=error)

    # опытным путем было выяснено что при сканировании более чем 8000 портов одновременно - нужен больший таймаут
    timeout = 10 if end_port - begin_port > 8000 else 5
    return [begin_port, end_port, timeout]


def main():
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    app = web.Application()
    app.add_routes([
        web.get('/scan/{ip}/{begin_port}/{end_port}', get_tasks)
    ])
    web.run_app(app)


if __name__ == '__main__':
    main()
