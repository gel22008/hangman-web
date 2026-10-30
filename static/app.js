"use strict";

// Browser client for the Hangman REST API.
// The server is authoritative: this file never knows the word while a game is
// playing and never decides whether a guess is right. It sends requests and
// redraws the page from whatever JSON the server returns.

const LETTERS = "abcdefghijklmnopqrstuvwxyz".split("");
const TOTAL_PARTS = 6;
const SERVER_UNREACHABLE =
  "Can't reach the server. If it was asleep, wait a moment and try again.";

const els = {
  app: document.getElementById("app"),
  difficulty: document.getElementById("difficulty"),
  newGame: document.getElementById("new-game"),
  drawing: document.getElementById("drawing"),
  parts: document.querySelectorAll("#drawing .part"),
  pattern: document.getElementById("pattern"),
  message: document.getElementById("message"),
  remaining: document.getElementById("remaining"),
  guessed: document.getElementById("guessed"),
  incorrect: document.getElementById("incorrect"),
  keyboard: document.getElementById("keyboard"),
};

const keyButtons = new Map();
let gameId = null;
let gameStatus = null;
let pending = false;

function buildKeyboard() {
  for (const letter of LETTERS) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = letter;
    button.setAttribute("aria-label", `Guess ${letter.toUpperCase()}`);
    button.addEventListener("click", () => guess(letter));
    els.keyboard.appendChild(button);
    keyButtons.set(letter, button);
  }
}

function setBusy(busy) {
  pending = busy;
  els.app.setAttribute("aria-busy", String(busy));
}

function showMessage(text, kind = "") {
  els.message.textContent = text;
  els.message.className = kind ? `message ${kind}` : "message";
}

function errorText(response) {
  if (response.data && typeof response.data.error === "string") {
    return response.data.error;
  }
  return `Request failed (HTTP ${response.status}).`;
}

function listText(letters) {
  return letters.length ? letters.join(", ") : "none";
}

async function api(path, body) {
  const options = { method: body === undefined ? "GET" : "POST" };
  if (body !== undefined) {
    options.headers = { "Content-Type": "application/json" };
    options.body = JSON.stringify(body);
  }
  const response = await fetch(path, options);
  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }
  return { ok: response.ok, status: response.status, data };
}

// Redraw everything from one server response.
function render(state) {
  gameId = state.game_id;
  gameStatus = state.status;

  els.pattern.textContent = state.pattern;
  els.remaining.textContent = String(state.remaining_guesses);
  els.guessed.textContent = listText(state.guessed_letters);
  els.incorrect.textContent = listText(state.incorrect_letters);

  const misses = Math.min(state.incorrect_letters.length, TOTAL_PARTS);
  els.parts.forEach((part, index) => {
    part.classList.toggle("shown", index < misses);
  });
  els.drawing.setAttribute(
    "aria-label",
    `Hangman drawing: ${misses} of ${TOTAL_PARTS} parts`
  );

  const guessed = new Set(state.guessed_letters);
  const incorrect = new Set(state.incorrect_letters);
  const over = state.status !== "playing";
  for (const [letter, button] of keyButtons) {
    button.disabled = over || guessed.has(letter);
    button.classList.toggle("hit", guessed.has(letter) && !incorrect.has(letter));
    button.classList.toggle("miss", incorrect.has(letter));
  }

  // The word only exists in the response after the game has ended.
  if (state.status === "won") {
    showMessage(`You won! The word was "${state.word}".`, "win");
  } else if (state.status === "lost") {
    showMessage(`Out of guesses. The word was "${state.word}".`, "loss");
  } else {
    showMessage("");
  }
}

async function newGame(notice) {
  setBusy(true);
  try {
    const response = await api("/api/games", { difficulty: els.difficulty.value });
    if (response.ok) {
      render(response.data);
      if (notice) showMessage(notice, "info");
    } else {
      showMessage(errorText(response), "error");
    }
  } catch {
    showMessage(SERVER_UNREACHABLE, "error");
  } finally {
    setBusy(false);
  }
}

async function guess(letter) {
  if (pending || !gameId || gameStatus !== "playing") return;
  const button = keyButtons.get(letter);
  if (!button || button.disabled) return;

  setBusy(true);
  let expired = false;
  try {
    const response = await api(
      `/api/games/${encodeURIComponent(gameId)}/guess`,
      { letter }
    );
    if (response.ok) {
      render(response.data);
    } else if (response.status === 404) {
      expired = true;
    } else {
      showMessage(errorText(response), "error");
    }
  } catch {
    showMessage(SERVER_UNREACHABLE, "error");
  } finally {
    setBusy(false);
  }

  // The server restarted (for example, Render's free tier went to sleep),
  // so this game no longer exists there.
  if (expired) {
    await newGame("This game expired. Starting a new one.");
  }
}

function onKeyDown(event) {
  if (event.ctrlKey || event.metaKey || event.altKey || event.repeat) return;
  const target = event.target;
  if (
    target instanceof HTMLSelectElement ||
    target instanceof HTMLInputElement ||
    target instanceof HTMLTextAreaElement ||
    (target instanceof HTMLElement && target.isContentEditable)
  ) {
    return;
  }
  const key = event.key.toLowerCase();
  if (key.length !== 1 || key < "a" || key > "z") return;
  event.preventDefault();
  guess(key);
}

buildKeyboard();
els.newGame.addEventListener("click", () => newGame());
document.addEventListener("keydown", onKeyDown);
newGame();
