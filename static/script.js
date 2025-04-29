// This assumes your HTML and server support the necessary events
const socket = io();
let myMark = null;
let myName = null;

const boardDiv = document.getElementById("board");
const playerInfo = document.getElementById("playerInfo");
const turnInfo = document.getElementById("turnInfo");
const queueStatus = document.getElementById("queueStatus");

for (let i = 0; i < 9; i++) {
  const cell = document.createElement("div");
  cell.classList.add("cell");
  cell.dataset.index = i;
  cell.addEventListener("click", () => makeMove(i));
  boardDiv.appendChild(cell);
}

function joinGame() {
  const name = document.getElementById("nameInput").value.trim();
  if (!name) return alert("Please enter your name");
  myName = name;
  socket.emit("join", { name });
}

function makeMove(index) {
  if (myMark) {
    socket.emit("make_move", { index, mark: myMark });
  }
}

socket.on("player_assigned", ({ mark, name }) => {
  myMark = mark;
  playerInfo.innerText = `You are ${mark} (${name})`;
});

socket.on("start_game", ({ players }) => {
  playerInfo.innerText = `X: ${players.X} | O: ${players.O}`;
  queueStatus.innerText = "";
});

socket.on("queued", ({ position }) => {
  queueStatus.innerText = `You're in the queue. Position: ${position}`;
});

socket.on("board_update", ({ board, turn }) => {
  board.forEach((val, i) => {
    boardDiv.children[i].innerText = val;
  });
  turnInfo.innerText = `Turn: ${turn}`;
});

socket.on("game_over", ({ winner }) => {
  if (winner === 'tie') {
    alert("It's a tie! Challenger wins!");
  } else {
    alert(`${winner} wins!`);
  }
});
