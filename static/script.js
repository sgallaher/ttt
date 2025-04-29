const socket = io();
const board = document.getElementById('board');
const player = Math.random() > 0.5 ? 'X' : 'O';
document.getElementById('player').innerText = player;
const room = 'room1'; // Hardcoded for now

// Send join request
socket.emit('join', { room, player });

// Render board
function renderBoard(state) {
    board.innerHTML = '';
    state.board.forEach((cell, index) => {
        const div = document.createElement('div');
        div.className = 'cell';
        div.textContent = cell;
        if (cell === '' && state.turn === player) {
            div.onclick = () => socket.emit('move', { room, index, player });
        }
        board.appendChild(div);
    });
}

// Listen for updates
socket.on('update', renderBoard);
