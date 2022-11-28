from nis import cat
from flask import Flask, session, render_template, redirect, url_for, request, jsonify
import re
import os
from base64 import b64encode
import uuid
import random
import traceback
import mysql.connector
import string

SECRET_KEY = ''.join(random.choice(string.printable) for i in range(64))
DANGER_CHARSET = '"\'\\;\n\r\t'
ALL_MOVES = list(range(1,10))
WINNER_MOVES = [
    [1, 2, 3], [4, 5, 6], [7, 8, 9],
    [1, 4, 7], [2, 5, 8], [3, 6, 9],
    [1, 5, 9], [3, 5, 7]
]

db = mysql.connector.connect(
    user=os.getenv('MYSQL_USER'), password=os.getenv('MYSQL_PASSWORD'),
    host=os.getenv('MYSQL_HOST'),
    database='ttt',
    connection_timeout=30,
    pool_name='ttt',
    pool_size=5)

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config.update(SECRET_KEY=SECRET_KEY)

# Filter params to avoid dangerous values
def filter_param(name, value):
    if not isinstance(value, str):
        raise ValueError(f'Invalid parameter format for "{name}"!')

    for ch in DANGER_CHARSET:
        if ch in value:
            raise ValueError(f'Invalid character in parameter "{name}"!')

    if value.find('--') > 0 or value.find('/*') > 0:
        raise ValueError(f'SQL comment not allowed in parameter "{name}"!')

def getdb():
    global db
    cursor = db.cursor()
    return db, cursor

def getuser():
    if not ('user_id' in session.keys()):
        return None, None

    return (session['user_id'], session['username'])

def translate_moves(game_id, game_key, db_moves, winner):
    translated_moves = {
        'game_id': game_id,
        'game_key': game_key,
        'X': [],
        'O': [],
        'winner': winner
    }

    for move in db_moves:
        _, position, value = move
        translated_moves['X' if value == 'X' else 'O'].append(int(position))

    return translated_moves

def get_moves(game_key, user_id):
    _, command = getdb()
    command.execute(f'select id, winner from games where game_key = "{game_key}" and user_id = {user_id}')
    game_info = command.fetchone()

    if game_info is None:
        raise ValueError('Game Key not found!')

    game_id = game_info[0]
    winner = game_info[1]

    command.execute(f'select g.game_key, m.position, m.value from games g inner join moves m on m.game_id = g.id where game_key = "{game_key}" and user_id = {user_id}')
    db_moves = command.fetchall()
    return translate_moves(game_id, game_key, db_moves, winner)

def set_winner(game_id, winner):
    db, command = getdb()
    command.execute(f'update games set winner = "{winner}" where id = {game_id}')
    db.commit()
    command.close()

def check_winner(game_id, moves, player):
    player_moves = moves[player]

    # Winner moves
    if any([all([win in player_moves for win in wins]) for wins in WINNER_MOVES]):
        set_winner(game_id, player)
        return player

    if len(moves['X']) + len(moves['O']) == 9:
        set_winner(game_id, '*')
        return '*' # Tie

    return '?' # Game still going

def insert_move(current_moves, position, player):

    game_id = current_moves['game_id']

    try:
        db, command = getdb()
        command.execute(f'insert into moves (game_id, position, value) values ({game_id}, {position}, "{player}")')
        db.commit()
        command.close()
    except mysql.connector.errors.IntegrityError:
        raise ValueError('Invalid Move! Try Again')


def user_move(game_key, user_id, position):
    current_moves = get_moves(game_key, user_id)
    game_id = current_moves['game_id']

    if current_moves['winner'] != '?':
        raise ValueError(f'Game is over!')

    # User Move
    insert_move(current_moves, position, 'X')

    current_moves['X'].append(int(position))
    current_moves['winner'] = check_winner(game_id, current_moves, 'X')

    # Check if ended
    if current_moves['winner'] in ['X', '*']:
        return current_moves

    # Bot Move
    available_moves = list(set(ALL_MOVES) - set(current_moves['X'] + current_moves['O']))
    bot_move = random.choice(available_moves)

    insert_move(current_moves, bot_move, 'O')
    current_moves['O'].append(bot_move)
    current_moves['winner'] = check_winner(game_id, current_moves, 'O')

    return current_moves

def translate_status(game_status):
    statuses = {
        "?": "Em andamento",
        "*": "Empate",
        "O": "Derrota",
        "X": "Vitória"
    }

    return statuses[game_status]

@app.route('/')
def index():
    _, username = getuser()

    return render_template('index.html', username=username)

@app.route('/register', methods=['GET', 'POST'])
def register():

    user_id, username = getuser()

    if request.method == 'GET':
        if not(user_id is None):
            return redirect(url_for('index'))
        return render_template('register.html', username=username)

    if not(user_id is None):
        return 'Already logged in', 400
        
    username = request.form.get('username')
    password = request.form.get('password')

    try:

        filter_param('username', username)
        filter_param('password', password)

        if not re.match(r'^[a-zA-Z0-9]{5,32}$', username):
            return 'Invalid Username!', 400

        if len(password) > 32:
            return 'Password Too Big!', 400

        password = b64encode(bytes(password, 'UTF-8')).decode('UTF-8')

        db, command = getdb()
        command.execute(f'insert into users (username, password) values ("{username}", "{password}")')
        user_id = command.lastrowid
        db.commit()
        command.close()

        return redirect(url_for('login'))
    except mysql.connector.errors.IntegrityError:
        return 'Username already exists!', 400
    except ValueError as valerr:
        return f'DANGER: {valerr}', 400
    except Exception as err:
        traceback.print_exc()
        return 'Internal Error!', 500

@app.route('/login', methods=['GET', 'POST'])
def login():

    user_id, username = getuser()

    if request.method == 'GET':
        if not(user_id is None):
            return redirect(url_for('index'))
        return render_template('login.html', username=username)

    if not(user_id is None):
        return 'Already logged in', 400
        
    username = request.form.get('username')
    password = request.form.get('password')

    try:

        filter_param('username', username)
        filter_param('password', password)

        password = b64encode(bytes(password, 'UTF-8')).decode('UTF-8')

        db, command = getdb()
        command.execute(f'select id from users where username = "{username}" and password = "{password}"')
        result = command.fetchone()

        if result is None:
            return 'Invalid Username or Password', 404

        user_id = result[0]
        if user_id is None:
            return 'Invalid Username or Password', 404

        command.close()

        session['user_id'] = user_id
        session['username'] = username

        return redirect(url_for('index'))
    except mysql.connector.errors.IntegrityError:
        return 'Username already exists!', 400
    except ValueError as valerr:
        return f'DANGER: {valerr}', 400
    except Exception as err:
        traceback.print_exc()
        return 'Internal Error!', 500

@app.route('/logout', methods=['POST'])
def logout():
    session['user_id'] = None
    session['username'] = None

    return redirect(url_for('index'))

@app.route('/newgame', methods=['POST'])
def newgame():

    user_id, _ = getuser()
    if user_id is None:
        return 'You need to log in first', 400

    game_key = str(uuid.uuid4())

    db, command = getdb()
    command.execute(f'insert into games (game_key, user_id) values ("{game_key}", {user_id})')
    db.commit()
    command.close()

    return jsonify({'game_key': game_key})

@app.route('/game/<string:game_key>/info', methods=['GET'])
def game_info(game_key):

    user_id, _ = getuser()
    if user_id is None:
        return 'You need to log in first', 400

    try:
        filter_param('game_key', game_key)

        uuid.UUID(game_key, version=4)

    except ValueError:
        return 'Invalid Game Key', 400

    try:
        moves = get_moves(game_key, user_id)
    except ValueError as valerr:
        return f'{valerr}', 400

    return jsonify(moves)

@app.route('/game/<string:game_key>', methods=['GET'])
def game(game_key):

    user_id, username = getuser()
    if user_id is None:
        return redirect(url_for('login'))

    return render_template('game.html', username=username, game_key=game_key)

@app.route('/game/<string:game_key>/move', methods=['POST'])
def move(game_key):

    user_id, _ = getuser()
    if user_id is None:
        return 'You need to log in first', 400

    param_position = request.form.get('position')

    try:
        filter_param('position', param_position)
        position = param_position
    except ValueError as valerr:
        traceback.print_exc()
        return f'Invalid Position for Move', 400

    try:
        filter_param('game_key', game_key)
        uuid.UUID(game_key, version=4)

    except ValueError:
        return 'Invalid Game Key', 400


    try:
        moves = user_move(game_key, user_id, position)
    except mysql.connector.errors.DatabaseError:
        traceback.print_exc()
        return 'Internal Error!', 500
    except ValueError as valerr:
        return f'{valerr}', 400

    return jsonify(moves)

@app.route('/games', methods=['GET'])
def games():
    user_id, username = getuser()
    if user_id is None:
        return 'You need to log in first', 400

    db, command = getdb()
    command.execute(f'select game_key, winner from games where user_id = {user_id}')
    games = command.fetchall()
    command.close()

    if games is None:
        games = []

    translated_games = [{'game_key': game[0], 'status': translate_status(game[1])} for game in games]

    return render_template('games.html', username=username, games=translated_games)