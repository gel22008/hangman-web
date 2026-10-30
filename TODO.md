# TODO — Hangman Client/Server Project

This file is the implementation roadmap for the Hangman project.

The authoritative system requirements are defined in `Specification.md`.

This build is a **web-based Hangman game**: Flask backend, HTML/CSS/JS frontend, deployed on Render. Word lists already exist at `words/easy.txt`, `words/medium.txt`, and `words/hard.txt`.

## Implementation Rules

- Implement one in-scope phase at a time.
- Complete and test all items in the current phase before moving to the next phase.
- Do not change the architecture or REST API defined in `Specification.md` unless necessary.
- If a deviation is necessary, document it in the README and update the specification.
- Keep the game engine independent from Flask and the browser UI.
- The server must remain authoritative.
- Never expose the hidden word before a game ends.
- Use Flask for the REST API (not FastAPI).
- Add tests as each in-scope phase is implemented rather than postponing testing until the end.
- Do not implement out-of-scope phases.

## In Scope

Game engine, word management, Flask REST API, browser client, testing, Render deployment with gunicorn, and documentation.

## Out of Scope

Terminal client, bots, evaluation, scoring, leaderboard, and logging/replay. Those phases are listed later and must stay unmarked as work to do.

---

## Phase 1 — Project Skeleton and Core Game Engine

### Tasks

- [x] Create the project directory structure needed for the web app.
- [x] Create `game.py`.
- [x] Implement a `HangmanGame` class.
- [x] Store the hidden word internally.
- [x] Track guessed letters.
- [x] Track incorrect letters.
- [x] Track the maximum number of incorrect guesses (six).
- [x] Implement single-letter guess validation.
- [x] Detect duplicate guesses.
- [x] Implement masked-word generation.
- [x] Implement win detection.
- [x] Implement loss detection.
- [x] Implement game status values such as `playing`, `won`, and `lost`.
- [x] Implement a method that returns a client-safe game-state dictionary.
- [x] Reveal the answer only after the game ends.
- [x] Add unit tests for the game engine.

### Completion Criteria

The game engine can be tested entirely without running a web server.

All core rules are covered by unit tests.

---

## Phase 2 — Word Management

Word list files already exist. Do not replace them unless a format problem is found.

### Tasks

- [x] Create a word-loading module or helper functions.
- [x] Load the existing Easy, Medium, and Hard lists from `words/easy.txt`, `words/medium.txt`, and `words/hard.txt`.
- [x] Validate that loaded words contain only alphabetic characters.
- [x] Remove accidental duplicates when loading.
- [x] Support random word selection by difficulty.
- [x] Return an error for an invalid difficulty.
- [x] Add tests for word loading and word selection.

### Completion Criteria

The program can request a random word from each difficulty level reliably.

Invalid difficulty values are rejected cleanly.

---

## Phase 3 — Flask REST API

Casual-play endpoints only. Do not add evaluation, leaderboard, or replay routes.

### Tasks

- [x] Create `server.py`.
- [x] Configure Flask.
- [x] Serve the browser client static files from Flask.
- [x] Add in-memory storage for active games.
- [x] Generate unique game IDs.
- [x] Implement `POST /api/games`.
- [x] Implement `GET /api/games/{game_id}`.
- [x] Implement `POST /api/games/{game_id}/guess`.
- [x] Validate difficulty input.
- [x] Validate guess input.
- [x] Return JSON responses consistently.
- [x] Return appropriate HTTP status codes.
- [x] Handle unknown game IDs.
- [x] Handle malformed requests.
- [x] Ensure the hidden word is never leaked during an active game.
- [x] Add API tests.

### Completion Criteria

A complete Hangman game can be played using only `curl` or another HTTP client.

The browser client is not required for this phase.

---

## Phase 4 — Browser Client

### Tasks

- [x] Create `static/index.html`.
- [x] Create `static/style.css`.
- [x] Create `static/app.js`.
- [x] Add a difficulty selector.
- [x] Add a New Game button.
- [x] Display the masked word.
- [x] Display guessed letters.
- [x] Display incorrect letters.
- [x] Display remaining guesses.
- [x] Add an on-screen alphabet keyboard.
- [x] Accept guesses from the physical keyboard (A–Z / a–z), not only on-screen buttons.
- [x] Ignore non-letter keys and guesses after the game has ended.
- [x] Disable already-guessed letters on the on-screen keyboard.
- [x] Use `fetch()` to communicate with the REST API.
- [x] Draw the Hangman state visually.
- [x] Update the drawing after incorrect guesses.
- [x] Display win and loss messages.
- [x] Provide a restart/new-game flow.
- [x] Make the interface usable on common desktop and mobile browser sizes.

### Completion Criteria

A human player can play the server-hosted game from a browser using either the on-screen keyboard or a physical keyboard.

No hidden word is stored in browser-side JavaScript.

---

## Phase 5 — Testing

Cover only in-scope behavior. Do not add tests for terminal clients, bots, evaluation, scoring, or leaderboard.

### Tasks

- [x] Complete unit tests for `HangmanGame`.
- [x] Complete tests for word loading.
- [x] Complete REST API tests.
- [x] Test duplicate guesses.
- [x] Test invalid letters.
- [x] Test invalid difficulty.
- [x] Test missing game IDs.
- [x] Test win paths.
- [x] Test loss paths.
- [x] Test answer disclosure rules.
- [x] Add an end-to-end automated test of the casual-play API flow.
- [x] Manually verify the browser client, including physical keyboard input.

### Completion Criteria

The major in-scope user flows and failure cases are covered by automated tests.

---

## Phase 6 — Deployment (Render + gunicorn)

### Tasks

- [x] Add `requirements.txt` with Flask, gunicorn, and test dependencies as needed.
- [x] Configure gunicorn as the production WSGI server.
- [x] Add Render start configuration (Render start command `gunicorn --bind 0.0.0.0:$PORT --workers 1 server:app`, documented in README).
- [x] Bind gunicorn to the port provided by the host (`PORT`).
- [x] Confirm static files are served in production so the browser client loads on Render.
- [x] Document any required Render environment settings.
- [x] Verify a production-style run with gunicorn (on Render; gunicorn does not run on Windows, so local runs use `python server.py`).
- [x] Deploy to Render and confirm create-game, guess, and win/loss flows in the hosted browser client.

### Completion Criteria

The game is reachable on Render. A player can open the site, start a game, guess letters, and finish a game without running Flask’s development server.

---

## Phase 7 — Documentation

Document only what this build implements.

### Tasks

- [x] Create or update `README.md`.
- [x] Document installation.
- [x] Document how to start the Flask app locally.
- [x] Document how to run with gunicorn locally.
- [x] Document how to use the browser client, including physical keyboard input.
- [x] Document the REST API (`POST /api/games`, `GET /api/games/{game_id}`, `POST /api/games/{game_id}/guess`).
- [x] Provide example requests and responses.
- [x] Document Render deployment.
- [ ] Verify that a fresh installation works from the documented instructions.

### Completion Criteria

A new user can clone the project, install dependencies, start the server, play from the browser, and follow the Render deployment notes using only the documentation.

---

# Out of Scope

Do not implement these phases. They remain in the full specification for a later, larger project.

## Out of Scope — Human Terminal Client

- [ ] Create `terminal_client.py`.
- [ ] Connect to the Hangman server over HTTP.
- [ ] Let the user choose Easy, Medium, or Hard.
- [ ] Start a new game through the REST API.
- [ ] Display the masked word.
- [ ] Display guessed letters.
- [ ] Display incorrect letters.
- [ ] Display remaining incorrect guesses.
- [ ] Prompt for one letter at a time.
- [ ] Submit guesses through the REST API.
- [ ] Handle invalid input locally when appropriate.
- [ ] Handle server errors gracefully.
- [ ] Display win and loss messages.
- [ ] Allow the user to start another game.

## Out of Scope — Reference Automated Clients

- [ ] Create `bot_examples/`.
- [ ] Implement `random_bot.py`.
- [ ] Implement `frequency_bot.py`.
- [ ] Define a common bot interaction pattern.
- [ ] Create a reusable HTTP client helper if useful.
- [ ] Make each bot capable of playing a complete game automatically.
- [ ] Print game results and summary statistics.
- [ ] Ensure bots use only information exposed through the REST API.
- [ ] Document how students can write their own bot.

## Out of Scope — Dictionary-Based Bot Example

- [ ] Implement `dictionary_bot.py`.
- [ ] Load an allowed training dictionary.
- [ ] Filter candidate words by current pattern.
- [ ] Remove candidates containing known incorrect letters.
- [ ] Respect known letter positions.
- [ ] Track letters already guessed.
- [ ] Compute candidate-letter frequencies.
- [ ] Choose the next letter using the remaining candidates.
- [ ] Fall back to global letter frequency if no candidates remain.
- [ ] Compare its performance against the random and frequency bots.

## Out of Scope — Evaluation Mode

- [ ] Separate normal game play from official evaluation mode.
- [ ] Add an evaluation-session model.
- [ ] Generate a unique evaluation ID.
- [ ] Define the number of evaluation games.
- [ ] Support evaluation across Easy, Medium, and Hard words.
- [ ] Ensure the server controls all evaluation words.
- [ ] Prevent skipping or restarting unfavorable evaluation games.
- [ ] Require games to be played in the intended sequence.
- [ ] Record wins and losses.
- [ ] Record total guesses.
- [ ] Record incorrect guesses.
- [ ] Record remaining guesses after wins.
- [ ] Record per-game results.
- [ ] Add evaluation API endpoints.
- [ ] Add tests for evaluation integrity.

## Out of Scope — Scoring System

- [ ] Define the official scoring formula.
- [ ] Make wins the primary performance signal.
- [ ] Use guess efficiency as a secondary signal or tiebreaker.
- [ ] Define how losses are scored.
- [ ] Define how invalid guesses affect scoring.
- [ ] Define how duplicate guesses affect scoring.
- [ ] Define how abandoned games affect scoring.
- [ ] Record total score for each evaluation.
- [ ] Add tests for scoring calculations.
- [ ] Document the scoring rules clearly for students.

## Out of Scope — Leaderboard

- [ ] Define a leaderboard record format.
- [ ] Store participant or bot name.
- [ ] Store total games.
- [ ] Store games won.
- [ ] Store win rate.
- [ ] Store average guesses.
- [ ] Store average remaining guesses on wins.
- [ ] Store total score.
- [ ] Rank results consistently.
- [ ] Add a leaderboard API endpoint.
- [ ] Add a browser leaderboard view.
- [ ] Display rankings in the terminal if useful.
- [ ] Decide whether leaderboard data should persist across server restarts.

## Out of Scope — Evaluation Integrity and Anti-Cheating Safeguards

- [ ] Ensure game state responses never contain the answer while status is `playing`.
- [ ] Ensure evaluation words are server-controlled.
- [ ] Prevent clients from requesting arbitrary evaluation game IDs.
- [ ] Reject malformed or unauthorized evaluation requests.
- [ ] Add optional rate limiting if needed.
- [ ] Add optional per-request timeout rules.
- [ ] Log evaluation actions.
- [ ] Detect repeated invalid guesses.
- [ ] Define behavior for disconnected clients.
- [ ] Define behavior for incomplete evaluations.
- [ ] Keep training word lists separate from hidden evaluation lists if desired.

## Out of Scope — Logging and Replay

- [ ] Define a game-log format.
- [ ] Record game ID.
- [ ] Record difficulty.
- [ ] Record each guess in order.
- [ ] Record whether each guess was correct.
- [ ] Record pattern after each guess.
- [ ] Record remaining guesses after each move.
- [ ] Record final outcome.
- [ ] Add optional timestamps.
- [ ] Add a replay utility or endpoint.
- [ ] Ensure logs do not expose hidden evaluation words before evaluation completion.

---

# Optional Future Phases

These should not be implemented until the core web game is stable. They are not part of the current build.

## Persistent Storage

- [ ] Store games in a database.
- [ ] Persist game history across server restarts.

## Accounts and Authentication

- [ ] User accounts.
- [ ] API keys or tokens.

## Tournament Mode

- [ ] Batch evaluation of multiple bots.
- [ ] Scheduled tournaments.
- [ ] Tournament history.
- [ ] Public results page.

## Advanced Bot Analysis

- [ ] Entropy-based guessing.
- [ ] Information-gain strategies.
- [ ] Performance charts.
- [ ] Per-difficulty statistics.
- [ ] Head-to-head bot comparisons.

## Multiplayer

- [ ] Human-vs-human modes.
- [ ] Custom words.
- [ ] Spectator mode.

---

# Recommended Development Order

Use this order unless there is a compelling reason to change it:

1. Core Game Engine
2. Word Management
3. Flask REST API
4. Browser Client
5. Testing
6. Deployment (Render + gunicorn)
7. Documentation

The project should remain runnable after every completed in-scope phase.
