import pytest

from game import HangmanGame


def test_correct_guess_reveals_matching_letters_and_keeps_remaining():
    game = HangmanGame("apple")
    state = game.guess("p")

    assert state["pattern"] == "_ p p _ _"
    assert state["guessed_letters"] == ["p"]
    assert state["incorrect_letters"] == []
    assert state["remaining_guesses"] == 6
    assert state["status"] == "playing"
    assert "word" not in state


def test_guesses_are_normalized_to_lowercase():
    game = HangmanGame("Apple")
    state = game.guess("A")

    assert state["pattern"] == "a _ _ _ _"
    assert state["guessed_letters"] == ["a"]


def test_incorrect_guess_records_letter_and_decrements_remaining():
    game = HangmanGame("apple")
    state = game.guess("z")

    assert state["pattern"] == "_ _ _ _ _"
    assert state["guessed_letters"] == ["z"]
    assert state["incorrect_letters"] == ["z"]
    assert state["remaining_guesses"] == 5
    assert state["status"] == "playing"


def test_duplicate_guess_is_rejected_without_changing_state():
    game = HangmanGame("apple")
    game.guess("a")
    before = game.state()

    with pytest.raises(ValueError, match="already guessed"):
        game.guess("A")

    assert game.state() == before


def test_invalid_guesses_are_rejected():
    game = HangmanGame("apple")
    before = game.state()

    for invalid in ("", "ab", "1", "!", " e", None, 3):
        with pytest.raises(ValueError, match="single letter"):
            game.guess(invalid)

    assert game.state() == before


def test_non_ascii_letters_are_rejected_as_invalid_guesses():
    game = HangmanGame("apple")
    before = game.state()

    for invalid in ("é", "ñ", "ß"):
        with pytest.raises(ValueError, match="single letter"):
            game.guess(invalid)

    assert game.state() == before


def test_win_reveals_word_and_sets_status():
    game = HangmanGame("hi")
    game.guess("h")
    state = game.guess("i")

    assert state["status"] == "won"
    assert state["pattern"] == "h i"
    assert state["word"] == "hi"
    assert state["remaining_guesses"] == 6


def test_loss_after_six_incorrect_guesses_reveals_word():
    game = HangmanGame("hi")
    for letter in ("a", "b", "c", "d", "e", "f"):
        state = game.guess(letter)

    assert state["status"] == "lost"
    assert state["remaining_guesses"] == 0
    assert state["incorrect_letters"] == ["a", "b", "c", "d", "e", "f"]
    assert state["word"] == "hi"
    assert state["pattern"] == "_ _"


def test_no_guesses_allowed_after_win_or_loss():
    won = HangmanGame("a")
    won.guess("a")
    with pytest.raises(ValueError, match="ended"):
        won.guess("b")

    lost = HangmanGame("a")
    for letter in ("b", "c", "d", "e", "f", "g"):
        lost.guess(letter)
    with pytest.raises(ValueError, match="ended"):
        lost.guess("a")


def test_word_is_hidden_while_playing():
    game = HangmanGame("secret")
    state = game.state()

    assert state["status"] == "playing"
    assert "word" not in state
    assert "secret" not in str(state)
    assert state["pattern"] == "_ _ _ _ _ _"

    after_guess = game.guess("s")
    assert "word" not in after_guess
    assert after_guess["pattern"] == "s _ _ _ _ _"
