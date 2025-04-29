from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

board = ["" for _ in range(9)]
players = {}
turn = "X"
queue = []


def reset_board():
    global board, turn
    board = ["" for _ in range(9)]
    turn = "X"


def switch_turn():
    global turn
    turn = "O" if turn == "X" else "X"


def check_winner():
    wins = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6],
    ]
    for a, b, c in wins:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if all(cell != "" for cell in board):
        return "TIE"
    return None


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("join")
def on_join(data):
    global players
    name = data["name"]

    if len(players) < 2:
        mark = "X" if "X" not in players else "O"
        players[mark] = name
        emit("player_assigned", {"mark": mark, "name": name})
        if len(players) == 2:
            emit("start_game", {"players": players}, broadcast=True)
            emit("board_update", {"board": board, "turn": turn}, broadcast=True)
    else:
        queue.append(name)
        emit("queued", {"position": len(queue)})


@socketio.on("make_move")
def on_make_move(data):
    global board, turn, players, queue

    index = data["index"]
    mark = data["mark"]

    if board[index] == "" and mark == turn:
        board[index] = mark
        winner = check_winner()
        if winner:
            if winner == "TIE":
                winner_name = players["O"]  # Challenger wins on tie
            else:
                winner_name = players[winner]

            emit("game_over", {"winner": winner_name}, broadcast=True)

            # Queue logic: original host loses or ties → moves to back
            loser_mark = "X" if winner != "X" else "O"
            if loser_mark in players:
                loser_name = players[loser_mark]
                queue.append(loser_name)

            # Winner becomes X, next in queue becomes O
            players = {"X": winner_name}
            if queue:
                players["O"] = queue.pop(0)
            else:
                players["O"] = ""

            reset_board()
            emit("start_game", {"players": players}, broadcast=True)
        else:
            switch_turn()

        emit("board_update", {"board": board, "turn": turn}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=10000)
