import pytest

from server import create_app
from words import WordManager

WORDS = {"easy": "go", "medium": "apple", "hard": "zebra"}


@pytest.fixture
def client(tmp_path):
    for difficulty, word in WORDS.items():
        (tmp_path / f"{difficulty}.txt").write_text(f"{word}\n", encoding="utf-8")
    app = create_app(word_manager=WordManager(directory=tmp_path))
    app.config["TESTING"] = True
    return app.test_client()


def error_body(response):
    data = response.get_json()
    assert data is not None
    assert set(data) == {"error"}
    assert isinstance(data["error"], str) and data["error"]
    return data


def create_game(client, difficulty="easy"):
    response = client.post("/api/games", json={"difficulty": difficulty})
    assert response.status_code == 201
    payload = response.get_json()
    assert payload["game_id"]
    assert payload["status"] == "playing"
    return payload


def assert_playing_hides_word(payload, secret):
    assert payload["status"] == "playing"
    assert "word" not in payload
    assert secret not in str({k: v for k, v in payload.items() if k != "game_id"})


def test_create_game_each_difficulty(client):
    expected_pattern = {
        "easy": "_ _",
        "medium": "_ _ _ _ _",
        "hard": "_ _ _ _ _",
    }
    for difficulty, pattern in expected_pattern.items():
        payload = create_game(client, difficulty)
        assert payload["pattern"] == pattern
        assert payload["remaining_guesses"] == 6
        assert payload["guessed_letters"] == []
        assert payload["incorrect_letters"] == []
        assert_playing_hides_word(payload, WORDS[difficulty])


def test_difficulty_is_case_insensitive_and_stripped(client):
    for difficulty in ("EASY", "Easy", " medium ", "HARD"):
        response = client.post("/api/games", json={"difficulty": difficulty})
        assert response.status_code == 201
        assert response.get_json()["status"] == "playing"


def test_invalid_and_missing_difficulty(client):
    missing = client.post("/api/games", json={})
    assert missing.status_code == 400
    error_body(missing)

    for invalid in ("eassy", "", "   ", "expert"):
        response = client.post("/api/games", json={"difficulty": invalid})
        assert response.status_code == 400
        error_body(response)

    wrong_type = client.post("/api/games", json={"difficulty": 3})
    assert wrong_type.status_code == 400
    error_body(wrong_type)


def test_correct_and_incorrect_guesses(client):
    game_id = create_game(client, "easy")["game_id"]

    correct = client.post(f"/api/games/{game_id}/guess", json={"letter": "G"})
    assert correct.status_code == 200
    payload = correct.get_json()
    assert payload["game_id"] == game_id
    assert payload["pattern"] == "g _"
    assert payload["guessed_letters"] == ["g"]
    assert payload["incorrect_letters"] == []
    assert payload["remaining_guesses"] == 6
    assert_playing_hides_word(payload, "go")

    incorrect = client.post(f"/api/games/{game_id}/guess", json={"letter": "z"})
    assert incorrect.status_code == 200
    payload = incorrect.get_json()
    assert payload["incorrect_letters"] == ["z"]
    assert payload["remaining_guesses"] == 5
    assert_playing_hides_word(payload, "go")

    fetched = client.get(f"/api/games/{game_id}")
    assert fetched.status_code == 200
    assert fetched.get_json()["game_id"] == game_id
    assert fetched.get_json()["incorrect_letters"] == ["z"]


def test_duplicate_and_invalid_guesses(client):
    game_id = create_game(client, "easy")["game_id"]
    client.post(f"/api/games/{game_id}/guess", json={"letter": "g"})

    duplicate = client.post(f"/api/games/{game_id}/guess", json={"letter": "G"})
    assert duplicate.status_code == 400
    error_body(duplicate)
    assert_playing_hides_word(client.get(f"/api/games/{game_id}").get_json(), "go")

    for letter in ("", "ab", "1", "!", "é"):
        response = client.post(f"/api/games/{game_id}/guess", json={"letter": letter})
        assert response.status_code == 400
        error_body(response)

    wrong_type = client.post(f"/api/games/{game_id}/guess", json={"letter": 1})
    assert wrong_type.status_code == 400
    error_body(wrong_type)

    missing = client.post(f"/api/games/{game_id}/guess", json={})
    assert missing.status_code == 400
    error_body(missing)


def test_full_win_reveals_word(client):
    game_id = create_game(client, "easy")["game_id"]
    client.post(f"/api/games/{game_id}/guess", json={"letter": "g"})
    response = client.post(f"/api/games/{game_id}/guess", json={"letter": "o"})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "won"
    assert payload["pattern"] == "g o"
    assert payload["word"] == "go"
    assert payload["game_id"] == game_id


def test_full_loss_reveals_word(client):
    game_id = create_game(client, "easy")["game_id"]
    payload = None
    for letter in ("a", "b", "c", "d", "e", "f"):
        payload = client.post(f"/api/games/{game_id}/guess", json={"letter": letter}).get_json()
        if payload["status"] == "playing":
            assert_playing_hides_word(payload, "go")
    assert payload["status"] == "lost"
    assert payload["remaining_guesses"] == 0
    assert payload["word"] == "go"


def test_guess_after_game_over_returns_409(client):
    game_id = create_game(client, "easy")["game_id"]
    client.post(f"/api/games/{game_id}/guess", json={"letter": "g"})
    client.post(f"/api/games/{game_id}/guess", json={"letter": "o"})

    response = client.post(f"/api/games/{game_id}/guess", json={"letter": "z"})
    assert response.status_code == 409
    error_body(response)


def test_unknown_game_id_returns_404(client):
    missing_get = client.get("/api/games/not-a-real-id")
    assert missing_get.status_code == 404
    error_body(missing_get)

    missing_guess = client.post("/api/games/not-a-real-id/guess", json={"letter": "a"})
    assert missing_guess.status_code == 404
    error_body(missing_guess)


def test_wrong_method_returns_405(client):
    response = client.get("/api/games")
    assert response.status_code == 405
    error_body(response)

    created = create_game(client)
    response = client.post(f"/api/games/{created['game_id']}")
    assert response.status_code == 405
    error_body(response)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"data": "not json", "content_type": "text/plain"},
        {"data": "{", "content_type": "application/json"},
        {"data": '"easy"', "content_type": "application/json"},
        {"data": "[1]", "content_type": "application/json"},
        {"data": "null", "content_type": "application/json"},
        {"data": "3", "content_type": "application/json"},
    ],
)
def test_malformed_create_bodies(client, kwargs):
    response = client.post("/api/games", **kwargs)
    assert response.status_code == 400
    error_body(response)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"data": "not json", "content_type": "text/plain"},
        {"data": "{", "content_type": "application/json"},
        {"data": '["a"]', "content_type": "application/json"},
        {"data": '"a"', "content_type": "application/json"},
        {"data": "null", "content_type": "application/json"},
    ],
)
def test_malformed_guess_bodies(client, kwargs):
    game_id = create_game(client)["game_id"]
    response = client.post(f"/api/games/{game_id}/guess", **kwargs)
    assert response.status_code == 400
    error_body(response)
    assert_playing_hides_word(client.get(f"/api/games/{game_id}").get_json(), "go")


def test_separate_games_do_not_affect_each_other(client):
    first = create_game(client, "easy")
    second = create_game(client, "medium")

    client.post(f"/api/games/{first['game_id']}/guess", json={"letter": "g"})

    first_state = client.get(f"/api/games/{first['game_id']}").get_json()
    second_state = client.get(f"/api/games/{second['game_id']}").get_json()

    assert first_state["guessed_letters"] == ["g"]
    assert first_state["pattern"] == "g _"
    assert second_state["guessed_letters"] == []
    assert second_state["pattern"] == "_ _ _ _ _"
    assert first_state["game_id"] != second_state["game_id"]
    assert_playing_hides_word(second_state, "apple")


def test_word_never_appears_in_playing_or_error_responses(client):
    payload = create_game(client, "medium")
    game_id = payload["game_id"]
    secret = "apple"
    assert_playing_hides_word(payload, secret)

    duplicate_setup = client.post(f"/api/games/{game_id}/guess", json={"letter": "a"})
    assert_playing_hides_word(duplicate_setup.get_json(), secret)

    for response in (
        client.post(f"/api/games/{game_id}/guess", json={"letter": "a"}),
        client.post(f"/api/games/{game_id}/guess", json={"letter": "1"}),
        client.post(f"/api/games/{game_id}/guess", data="{", content_type="application/json"),
        client.get("/api/games/missing"),
    ):
        body = response.get_json()
        assert "word" not in body
        assert secret not in str(body)
        assert secret not in response.get_data(as_text=True)
