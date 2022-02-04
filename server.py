from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
import socket
import json
from models import *
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
    filename="logger.log")
logger = logging.getLogger('server')


# logger_handler = logging.FileHandler('python_logging.log')
# logger_handler.setLevel(logging.INFO)
# logger_formatter = logging.Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s')
# logger_handler.setFormatter(logger_formatter)
#
# logger.addHandler(logger_handler)
# logger.info('Настройка логгирования окончена!')

def start_server():
    engine = create_engine("postgresql+psycopg2://postgres:pass@localhost/postgres")
    session = sessionmaker(bind=engine)

    ADDRESS = 'localhost'
    PORT = 8080

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ADDRESS, PORT))
    sock.listen(1)

    ################################

    main_dict = {
        'authorization': People.sign_in,
        'add': People.add_client,
        'edit': People.edit_client,
        'delete': People.delete_client,
        'get': People.get_client,
        'get_objects': People.get_client_objects,
    }

    while True:
        conn, addr = sock.accept()
        logger.info('Connected:' + str(addr))
        print('Connected:', addr)

        while True:
            client_data = conn.recv(1024)  # данные от клиента
            if not client_data:
                logger.info('Disconnected:' + str(addr))
                break

            client_data = client_data.decode()
            client_data = json.loads(client_data)

            act = client_data['action']
            content = client_data['content']

            # if content['token'] != None:
            try:
                client_data['content'] = main_dict.get(act)(content)
                content['status'] = '200'
                content['message'] = ''
            except NotFoundError as e:
                content['status'] = e.status
                content['message'] = e.message
            # else:
            #     raise UnauthorizedError
            logger.info(act + ' - ' + client_data['content']['status'])

            conn.sendall(bytes(json.dumps(client_data, ensure_ascii=False, default=str), 'UTF-8'))  # возврат данных клиенту


start_server()
