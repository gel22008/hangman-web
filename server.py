"""Flask REST API for Hangman. Game rules stay in game.py; words stay in words.py."""

from __future__ import annotations

import secrets
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from game import HangmanGame
from words import WordManager

MAX_CONTENT_LENGTH = 1024


def create_app(word_manager: WordManager | None = None) -> Flask:
    app = Flask(
        __name__,
        static_folder=str(Path(__file__).parent / "static"),
        static_url_path="/static",
    )
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    manager = word_manager if word_manager is not None else WordManager()
    games: dict[str, HangmanGame] = {}

    def json_error(message: str, status: int):
        return jsonify(error=message), status

    def game_response(game_id: str, game: HangmanGame, status: int = 200):
        payload = game.state()
        payload["game_id"] = game_id
        return jsonify(payload), status

    def read_json_object():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return None, json_error("Request body must be a JSON object", 400)
        return data, None

    @app.errorhandler(404)
    def not_found(_error):
        return json_error("Not found", 404)

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return json_error("Method not allowed", 405)

    @app.errorhandler(413)
    def too_large(_error):
        return json_error("Request too large", 413)

    @app.errorhandler(500)
    def server_error(_error):
        return json_error("Internal server error", 500)

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.post("/api/games")
    def create_game():
        data, error = read_json_object()
        if error is not None:
            return error
        if "difficulty" not in data:
            return json_error("Missing difficulty", 400)
        difficulty = data["difficulty"]
        if not isinstance(difficulty, str):
            return json_error("Invalid difficulty", 400)
        try:
            word = manager.random_word(difficulty)
        except ValueError:
            return json_error("Invalid difficulty", 400)
        game_id = secrets.token_hex(16)
        game = HangmanGame(word)
        games[game_id] = game
        return game_response(game_id, game, 201)

    @app.get("/api/games/<game_id>")
    def get_game(game_id: str):
        game = games.get(game_id)
        if game is None:
            return json_error("Game not found", 404)
        return game_response(game_id, game)

    @app.post("/api/games/<game_id>/guess")
    def guess_letter(game_id: str):
        game = games.get(game_id)
        if game is None:
            return json_error("Game not found", 404)
        data, error = read_json_object()
        if error is not None:
            return error
        if "letter" not in data:
            return json_error("Missing letter", 400)
        letter = data["letter"]
        if not isinstance(letter, str):
            return json_error("Invalid letter", 400)
        try:
            game.guess(letter)
        except ValueError as exc:
            message = str(exc)
            if "ended" in message.lower():
                return json_error(message, 409)
            return json_error(message, 400)
        return game_response(game_id, game)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
