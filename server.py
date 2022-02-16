import socket
import json
from models import *
import logging

file_log = logging.FileHandler('logger.log')
console_log = logging.StreamHandler()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
    handlers=(file_log, console_log))
logger = logging.getLogger('server')

def start_server():
    # ADDRESS = '192.168.1.7'
    ADDRESS = '127.0.0.1'
    PORT = 8080

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ADDRESS, PORT))
        sock.listen(1)
        logger.info('Server is running')
    except:
        print('Port is occupied')
        sock.settimeout(5)

    ################################

    main_dict = {
        'authorization': People.sign_in,
        'add': People.add_client,
        'edit': People.edit_client,
        'delete': People.delete_client,
        'get': People.get_client,
        'get_objects': People.get_client_objects,
        'get_favs': People.get_client_favourites,
        'sign_out': People.sign_out,
    }

    while True:
        conn, addr = sock.accept()
        logger.info('Connected:' + str(addr))

        while True:
            try:
                client_data = conn.recv(4096)
                client_data = client_data.decode()
                client_data = json.loads(client_data)
            except:
                logger.error('Receiving Error!')

            if not client_data:
                logger.info('Disconnected:' + str(addr))
                break

            # if content['token'] != None:
            try:
                act = client_data['action']
                content = client_data['content']
                client_data['content'] = main_dict.get(act)(content)
                content['status'] = '200'
                content['message'] = ''
            except NotFoundError as e:
                content['status'] = e.status
                content['message'] = e.message
                logger.warning('Not Found!')
            except InternalServerError as e:
                content['status'] = e.status
                content['message'] = e.message
            except UnauthorizedError as e:
                content['status'] = e.status
                content['message'] = e.message
                logger.error('Unauthorized Error!')
            # else:
            #     raise UnauthorizedError
            logger.info(act + ' - ' + client_data['content']['status'])

            try:
                conn.sendall(bytes(json.dumps(client_data, ensure_ascii=False, default=str), 'UTF-8'))
            except:
                logger.error('Sending Error!')


start_server()
