
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

games = {}  # room_id -> game state

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    if room not in games:
        games[room] = {
            'board': [''] * 9,
            'turn': 'X',
            'players': [],
        }
    if data['player'] not in games[room]['players']:
        games[room]['players'].append(data['player'])
    emit('update', games[room], room=room)

@socketio.on('move')
def on_move(data):
    room = data['room']
    idx = data['index']
    player = data['player']
    game = games.get(room)
    if game and game['board'][idx] == '' and game['turn'] == player:
        game['board'][idx] = player
        game['turn'] = 'O' if player == 'X' else 'X'
        emit('update', game, room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
