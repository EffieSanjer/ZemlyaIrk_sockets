import json
import socket
import hashlib

sock = socket.socket()

prints = {
    'clients': {
        'full_name': 'ФИО',
        'phone1': 'основной телефон',
        'phone2': 'второй телефон',
        'email': 'email',
        'password': 'пароль'},

    'objects': {
       'id': 'Id',
       'type': 'Тип объекта',
       'address': 'Адрес',
       'area': 'Площадь',
       'cost': 'Стоимость',
       'status': 'Статус'
    }
}

def start_client():
    # sock.connect(('192.168.1.7', 8080))
    sock.connect(('127.0.0.1', 8080))


    main_dict = {
        0: ['clients', 'authorization', sign_in, False],  # не нужна авторизация
        1: ['clients', 'add', add_client, False],
        2: ['clients', 'edit', edit_client, True],
        3: ['clients', 'delete', del_client, True],
        4: ['clients', 'get', get_client, True],
        5: ['clients', 'get_objects', get_client_objects, True],
        6: ['clients', 'get_favs', get_client_favs, True],
        7: ['clients', 'sign_out', sign_out, True]
    }
    while True:
        client_data = {'content': {'data': {}}}
        while True:

            if not is_auth(client_data):
                print('0 - авторизоваться')
                print('1 - зарегистрироваться')
            else:
                print(client_data)
                print('')
                print('2 - изменить личные данные')
                print('3 - удалить профиль')
                print('4 - посмотреть профиль')
                print('5 - посмотреть объявления')
                print('6 - посмотреть избранное')
                print('7 - выйти')

            try:
                my_choice = int(input())
            except ValueError:
                print('Введите числовое значение!')
                break
            except TypeError:
                print('Введите соответствующую цифру!')
                break

            # if my_choice == 7:
            #     break
            md = main_dict.get(my_choice)
            if md[3] == is_auth(client_data):
                client_data['endpoint'] = md[0]
                client_data['action'] = md[1]
                client_data = md[2](client_data)
            else:
                print('Введите верное значение!')
                continue


def is_auth(client_data):
    if 'token' in client_data['content']:
        return True
    else:
        return False


def send_and_print(client_data, print_func):
    client_data = send_receive(client_data)

    if client_data['content']['status'] == '200':
        print_func(client_data['content']['data'])
    else:
        print(client_data['content']['message'])
    return client_data


def send_receive(client_data):
    json_str = json.dumps(client_data)
    sock.sendall(bytes(json_str, 'UTF-8'))

    client_data = sock.recv(4096).decode()
    client_data = json.loads(client_data)
    return client_data


def print_input(prints, client_data):
    for p in prints:
        print('Введите ' + prints[p])
        client_data['content']['data'][p] = input()

    if client_data['endpoint'] == 'clients' \
            and 'password' in client_data['content']['data']:
        ps = client_data['content']['data']['password']
        client_data['content']['data']['password'] = hashlib.sha256(ps.encode()).hexdigest()
        print('EE')
    return client_data


def print_output(client_data):
    print('')
    for p in prints[client_data['endpoint']]:
        print(prints[client_data['endpoint']][p] + ': ' + client_data['content']['data'][p])
    return client_data


def print_fk_output(client_data, action):
    for a in client_data['content']['data'][action]:
        print('')
        for p in prints['objects']:
            print(prints['objects'][p] + ': ' + str(a[p]))
    return client_data

#####################


def sign_in(client_data):
    prints = {
        'email': 'email',
        'password': 'пароль'
    }
    client_data = print_input(prints, client_data)
    client_data = send_and_print(client_data,
                                 lambda user: print('Добро пожаловать, ' + user['full_name']))
    return client_data


def add_client(client_data):
    client_data = print_input(prints['clients'], client_data)
    client_data = send_and_print(client_data,
                                 lambda user: print('Вы успешно зарегистрировались! Добро пожаловать, ', user['full_name']))
    return client_data


def edit_client(client_data):
    # prints = {
    #     'full_name': 'Введите ФИО',
    #     'phone1': 'Введите основной телефон',
    #     'phone2': 'Введите второй телефон',
    #     'email': 'Введите email',
    #     'password': 'Введите пароль'
    # }

    client_data = print_input(prints['clients'], client_data)
    client_data = send_and_print(client_data,
                                 lambda user: print('Данные успешно изменены!'))
    return client_data


def del_client(client_data):
    client_data = send_and_print(client_data,
                                 lambda user: print('Ваш профиль удален!'))
    client_data = {'content': {'data': {}}}
    return client_data


def get_client(client_data):
    # prints = {
    #     'full_name': 'Ваше имя: ',
    #     'phone1': 'Ваш сновной телефон: ',
    #     'phone2': 'Ваш второй телефон: ',
    #     'email': 'Ваш email: '
    # }

    client_data = send_and_print(client_data,
                                 lambda user: print('Ваши данные:'))
    client_data = print_output(client_data)
    return client_data


def get_client_objects(client_data):
    # prints = {
    #     'id': 'Id: ',
    #     'type': 'Тип объекта: ',
    #     'address': 'Адрес: ',
    #     'area': 'Площадь: ',
    #     'cost': 'Стоимость: ',
    #     'status': 'Статус: '
    # }
    print('')
    client_data = send_and_print(client_data,
                                 lambda user: print('Ваши объявления:'))
    client_data = print_fk_output(client_data, 'objects')
    return client_data


def get_client_favs(client_data):
    # prints = {
    #     'id': 'Id: ',
    #     'type': 'Тип объекта: ',
    #     'address': 'Адрес: ',
    #     'area': 'Площадь: ',
    #     'cost': 'Стоимость: ',
    # }
    print('')
    client_data = send_and_print(client_data,
                                 lambda user: print('Ваши избранные:'))
    client_data = print_fk_output(client_data, 'favourites')
    return client_data

def sign_out(client_data):
    client_data = send_and_print(client_data,
                                 lambda user: print('Выход...'))
    return client_data

start_client()
