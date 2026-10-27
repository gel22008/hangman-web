import random

import pytest

from words import WordManager


def test_real_files_load_expected_counts_and_ascii_words():
    manager = WordManager()
    expected = {"easy": 188, "medium": 211, "hard": 234}

    for difficulty, count in expected.items():
        loaded = manager.words(difficulty)
        assert len(loaded) == count
        assert len(loaded) == len(set(loaded))
        assert all(word == word.lower() and word.isascii() and word.isalpha() for word in loaded)


def test_random_word_comes_from_the_correct_difficulty_list():
    manager = WordManager()

    for difficulty in ("easy", "medium", "hard"):
        word = manager.random_word(difficulty)
        assert word in manager.words(difficulty)


def test_mixed_case_and_padded_difficulties_are_accepted():
    manager = WordManager()
    easy = set(manager.words("easy"))
    hard = set(manager.words("hard"))

    for difficulty in ("EASY", "Easy", "EAsy", " hard "):
        word = manager.random_word(difficulty)
        if difficulty.strip().lower() == "easy":
            assert word in easy
        else:
            assert word in hard


def test_invalid_difficulties_raise_value_error():
    manager = WordManager()

    for invalid in ("eassy", "", "   ", "expert", None, 3, ["easy"]):
        with pytest.raises(ValueError, match="Invalid difficulty"):
            manager.random_word(invalid)


def test_seeded_randomness_is_reproducible():
    first = WordManager(rng=random.Random(42))
    second = WordManager(rng=random.Random(42))

    first_draws = [first.random_word("medium") for _ in range(8)]
    second_draws = [second.random_word("medium") for _ in range(8)]

    assert first_draws == second_draws
    assert all(word in first.words("medium") for word in first_draws)


def _write_lists(directory, easy, medium="ok", hard="ok"):
    (directory / "easy.txt").write_bytes(easy.encode("utf-8"))
    (directory / "medium.txt").write_bytes(medium.encode("utf-8") + b"\n")
    (directory / "hard.txt").write_bytes(hard.encode("utf-8") + b"\n")


def test_fake_files_clean_blank_lines_crlf_uppercase_duplicates_and_invalid(tmp_path):
    messy = "Apple\r\n\r\nbanana\r\nAPPLE\r\nxyz1\r\ncaf\u00e9\r\nCherry\r\nbanana\r\n\u00f1o\r\n"
    _write_lists(tmp_path, messy)

    manager = WordManager(directory=tmp_path)

    assert manager.words("easy") == ["apple", "banana", "cherry"]
    assert manager.random_word("easy") in {"apple", "banana", "cherry"}


def test_empty_file_raises(tmp_path):
    _write_lists(tmp_path, easy="", medium="ok", hard="ok")

    with pytest.raises(ValueError, match="empty"):
        WordManager(directory=tmp_path)
