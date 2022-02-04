import json
import socket
import hashlib
from uuid import uuid4

sock = socket.socket()


def start_client():
    client_data = {'content': {'data': {}}}
    sock.connect(('localhost', 8080))

    while True:
        while True:
            if not ('token' in client_data['content']):  # checkToken
                print('')
                print('0 - авторизоваться')
                print('1 - зарегистрироваться')

                # if int(input()) != (0 or 1):
                #     raise UnauthorizedError
                #     break
            else:
                print(client_data)
                print('')
                print('2 - изменить личные данные')
                print('3 - удалить профиль')
                print('4 - посмотреть профиль')
                print('5 - посмотреть объявления')
                print('6 - выйти')

            try:
                my_choice = int(input())
            except ValueError:
                print('Введите числовое значение!')  # Принты в отдельную функцию?
                break


            # client_data = {}  # словарь для отправки серверу

            main_dict = {
                0: ['clients', 'authorization', sign_in],
                1: ['clients', 'add', add_client],
                2: ['clients', 'edit', edit_client],
                3: ['clients', 'delete', del_client],
                4: ['clients', 'get', get_client],
                5: ['clients', 'get_objects', get_client_objects],
                6: ['clients', 'sign_out', sign_out]
            }

            if my_choice < 7:
                md = main_dict.get(my_choice)
                client_data['endpoint'] = md[0]
                client_data['action'] = md[1]
                client_data = md[2](client_data)


def send_and_print(client_data, print_func):
    client_data = send_receive(client_data)

    if client_data['content']['status'] == '200':
        print_func(client_data['content']['data'])
    else:
        print(client_data['content']['message'])
    return client_data


def send_receive(client_data):  # try except!!!
    json_str = json.dumps(client_data)
    sock.sendall(bytes(json_str, 'UTF-8'))

    client_data = sock.recv(1024).decode()
    client_data = json.loads(client_data)
    return client_data


def print_input(prints, client_data):
    for p in prints:
        print(prints[p])
        client_data['content']['data'][p] = input()

    if client_data['endpoint'] == 'clients' and (client_data['action'] == ('authorization' or 'add')):
        ps = client_data['content']['data']['password']
        client_data['content']['data']['password'] = hashlib.sha256(ps.encode()).hexdigest()
        print('EE')
    return client_data

#####################


def sign_in(client_data):
    prints = {
        'email': 'Введите email',
        'password': 'Введите пароль'
    }
    client_data = print_input(prints, client_data)
    client_data = send_and_print(client_data,
                                 lambda user: print('Добро пожаловать, ' + user['full_name']))
    return client_data


def add_client(client_data):
    # client_data = {}

    # content = {}
    # content['i_key'] = str(uuid4())
    # content['token'] = ''
    # data = {}  # словарь с данными клиента

    prints = {
        'full_name': 'Введите ФИО',
        'phone1': 'Введите основной телефон',
        'phone2': 'Введите второй телефон',
        'email': 'Введите email',
        'password': 'Введите пароль'
    }

    client_data = print_input(prints, client_data)


    # client_data['content'] = content
    # content['data'] = data  # словарь с данными клиента

    # client_data = send_receive(client_data)
    client_data = send_and_print(client_data,
                                 lambda user: print('Вы успешно зарегистрировались! Ваш id: ', user['id']))

    return client_data

def edit_client(client_data):
    # content = {}
    data = {}  # словарь с данными клиента

    prints = {
        'full_name': 'Введите ФИО',
        'phone1': 'Введите основной телефон',
        'phone2': 'Введите второй телефон',
        'email': 'Введите email',
        'password': 'Введите пароль'
    }

    for p in prints:
        print(prints[p])
        data[p] = input()

    # client_data['content'] = content
    client_data['content']['data'] = data  # словарь с данными клиента

    client_data = send_receive(client_data)

    if client_data['content']['status'] == '200':
        print('Данные успешно изменены!')
    else:
        print(client_data['content']['message'])
    return client_data

def del_client(client_data):
    # client_data = {}
    # client_data['action'] = 'delete'
    # client_data['endpoint'] = 'clients'
    # content = {}
    data = {}  # словарь с данными клиента

    # print('Введите свой id')
    # data['id'] = input()

    # client_data['content'] = content
    client_data['content']['data'] = data  # словарь с данными клиента

    client_data = send_receive(client_data)
    if client_data['content']['status'] == '200':
        print('Ваш профиль удален!')
        client_data = {}
    else:
        print(client_data['content']['message'])
    return client_data

def get_client(client_data):
    # content = {}
    data = {}  # словарь с данными клиента
    #
    # print('Введите свой id')
    # data['id'] = input()
    #
    client_data['content']['data'] = data
    # content['data'] = data  # словарь с данными клиента
    #
    client_data = send_receive(client_data)

    prints = {
        'full_name': 'Ваше имя: ',
        'phone1': 'Ваш телефон: ',
        'email': 'Ваш email: ',
        'password': 'Ваш пароль: '
    }

    for p in prints:
        print(prints[p] + client_data['content']['data'][p])

    # print('Ваше имя: ', client_data['content']['data']['full_name'])
    # print('Ваши телефоны: ', client_data['content']['data']['phone1'], ', ',
    #       client_data['content']['data']['phone2'])
    # print('Ваш email: ', client_data['content']['data']['email'])
    # print('Ваш пароль: ', client_data['content']['data']['password'])
    return client_data

def get_client_objects(client_data):
    # client_data = {}
    # client_data['action'] = 'get_objects'
    # client_data['endpoint'] = 'clients'
    # content = {}
    data = {}  # словарь с данными клиента

    # print('Введите свой id')
    # data['id'] = input()

    # client_data['content'] = content
    client_data['content']['data'] = data  # словарь с данными клиента

    client_data = send_receive(client_data)

    # prints = {
    #     'full_name': 'Ваше имя: ',
    #     'phone1': 'Ваши телефон: ',
    #     'email': 'Ваш email: ',
    #     'password': 'Ваш пароль: '
    # }
    print('')
    print('Ваши объявления:')

    # for p in prints:
    #     print(prints[p] + client_data['content']['data'][p])
    if client_data['content']['status'] == '200':
        for o in client_data['content']['data']['objects']:
            print('id', o['id'])
            print('Тип', o['type'])
            print('Адрес', o['address'])
    else:
        print(client_data['content']['message'])
    return client_data

def sign_out(client_data):
    client_data = {}
    return client_data

start_client()
