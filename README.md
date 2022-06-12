# Запуск:
    1. git clone https://github.com/kingco6ra/ideco_task.git
    2. cd ideco_task/
    3. python -m venv venv
    4. pip install -r requirements.txt
    5. source venv/bin/activate
    6. python main.py

# Задание 
Требуется разработать web-приложение для сканирования открытых TCP портов удаленного хоста.
Приложение должно реализовать следующее REST API:

    GET /scan/<ip>/<begin_port>/<end_port>

    Параметры:
        # ip - хост, который необходимо просканировать
        # begin_port - начала диапозона портов для сканирования
        # end_port - конец диапозона портов для сканирования

    Формат ответа:  [{"port": "integer", "state": "(open|close)"}]


Обработчик данного урла - запускает сканирование указанного хоста, и отдает информацию клиенту. В формате JSON (можно частями).
