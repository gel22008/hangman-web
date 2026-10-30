# Hangman Web Game

A web-based Hangman game with a Python/Flask backend and an HTML/CSS/JavaScript frontend, deployed on Render.

**Live app:** https://hangman-web-e48t.onrender.com

The server is authoritative: all game rules and the hidden word stay on the server. The browser only displays the game state the server returns, and the word is included in a response only after the game is won or lost.

## Project structure

```
hangman-web/
├── game.py            # HangmanGame: rules, guesses, win/loss, client-safe state (no Flask)
├── words.py           # WordManager: loads word lists, picks a random word by difficulty
├── server.py          # Flask app: REST API + serves the browser client
├── static/
│   ├── index.html     # page layout
│   ├── style.css      # styles (desktop, mobile, light/dark)
│   └── app.js         # fetch() calls to the API and page updates
├── words/
│   ├── easy.txt       # 188 words (provided by the course instructor)
│   ├── medium.txt     # 211 words
│   └── hard.txt       # 234 words
├── tests/
│   ├── test_game.py   # game engine unit tests
│   ├── test_words.py  # word loading and selection tests
│   └── test_api.py    # REST API tests using Flask's test client
├── requirements.txt
├── Specification.md   # original project specification
└── TODO.md            # phased plan, revised for this web-only scope
```

## Run locally

Requires Python 3.10 or newer.

```bash
git clone https://github.com/gel22008/hangman-web.git
cd hangman-web
python -m venv venv
```

Activate the virtual environment:

- Windows (PowerShell): `venv\Scripts\Activate.ps1`
- Windows (Command Prompt): `venv\Scripts\activate`
- macOS / Linux: `source venv/bin/activate`

Install dependencies and start the server:

```bash
pip install -r requirements.txt
python server.py
```

Open http://127.0.0.1:5000 in a browser.

`python server.py` uses Flask's development server with debug mode on, for local use only. To run the production-style server locally on macOS or Linux (gunicorn does not run on Windows):

```bash
gunicorn --bind 0.0.0.0:5000 --workers 1 server:app
```

## Run the tests

```bash
python -m pytest -v
```

## How to play

1. Choose **Easy**, **Medium**, or **Hard** and click **New Game**. A game also starts automatically when the page loads.
2. Guess a letter by clicking an on-screen button or typing it on your keyboard. Guessed letters are disabled; correct ones turn green and incorrect ones red.
3. Each incorrect guess adds a part to the hangman. Six incorrect guesses lose the game.
4. Reveal every letter to win. The word is shown when the game ends, win or lose.
5. Click **New Game** to play again without reloading the page.

## REST API

All requests and responses use JSON. Errors are always returned as `{"error": "message"}`.

| Method | Endpoint | Body | Success |
| --- | --- | --- | --- |
| POST | `/api/games` | `{"difficulty": "easy"}` | 201, new game state |
| GET | `/api/games/{game_id}` | none | 200, current game state |
| POST | `/api/games/{game_id}/guess` | `{"letter": "e"}` | 200, updated game state |

Difficulty is case-insensitive (`"Easy"`, `"EASY"` work); guesses are a single letter a–z.

### Example: create a game

```
POST /api/games
{"difficulty": "medium"}
```

```json
{
  "game_id": "27e2df29471c2134396c67f084e80654",
  "pattern": "_ _ _ _ _ _",
  "guessed_letters": [],
  "incorrect_letters": [],
  "remaining_guesses": 6,
  "status": "playing"
}
```

### Example: guess a letter

```
POST /api/games/27e2df29471c2134396c67f084e80654/guess
{"letter": "e"}
```

```json
{
  "game_id": "27e2df29471c2134396c67f084e80654",
  "pattern": "_ e _ _ _ _",
  "guessed_letters": ["e"],
  "incorrect_letters": [],
  "remaining_guesses": 6,
  "status": "playing"
}
```

When the game ends, `status` becomes `"won"` or `"lost"` and the response adds `"word"`.

### Status codes

| Code | Meaning |
| --- | --- |
| 200 | OK |
| 201 | Game created |
| 400 | Invalid or missing difficulty or letter, duplicate guess, or malformed JSON body |
| 404 | Unknown game ID or route |
| 405 | Wrong HTTP method |
| 409 | Guess sent after the game has ended |
| 413 | Request body larger than 1 KB |

### Trying the API from a terminal

PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/api/games -ContentType 'application/json' -Body '{"difficulty":"easy"}'
```

macOS / Linux:

```bash
curl -X POST http://127.0.0.1:5000/api/games -H "Content-Type: application/json" -d '{"difficulty":"easy"}'
```

## Deployment (Render)

The app is deployed as a Render **Web Service** on the free instance type, connected to this GitHub repository. Each push to `main` redeploys automatically.

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn --bind 0.0.0.0:$PORT --workers 1 server:app`
- **Environment variables:** none required (the app uses no secrets).

`server:app` points gunicorn at the `app` object in `server.py`. One worker is required because games are stored in that process's memory.

## Known limitations

- **Games are stored in memory.** They are lost whenever the server restarts, sleeps, or redeploys. If that happens mid-game, the page shows "This game expired. Starting a new one." and starts a fresh game.
- **Render's free tier sleeps** after about 15 minutes without traffic. The first request afterward can take up to a minute while the server wakes up.
- **Single worker only.** Running more than one gunicorn worker would split games across processes and cause 404 errors.
- **Finished games are never deleted** from memory until the server restarts.

## Development notes

Phases 1–3 (game engine, word management, REST API) were built with Cursor's Agent mode, one TODO phase per prompt. When Cursor's free usage limit ran out, Phase 4 onward (browser client, deployment notes, documentation) was completed with Claude as the coding agent, following the same phase-by-phase plan. Word lists were provided by the course instructor and are used unchanged.
