"""Load and select Hangman words by difficulty. Independent of Flask and UI."""

from __future__ import annotations

import random
from pathlib import Path


DIFFICULTIES = ("easy", "medium", "hard")
_DEFAULT_WORDS_DIR = Path(__file__).parent / "words"


def _is_ascii_alpha(value: str) -> bool:
    return value.isascii() and value.isalpha()


class WordManager:
    """Load curated word lists once and return random words by difficulty."""

    def __init__(
        self,
        directory: str | Path | None = None,
        rng: random.Random | None = None,
    ) -> None:
        self._directory = Path(directory) if directory is not None else _DEFAULT_WORDS_DIR
        self._rng = rng if rng is not None else random.Random()
        self._words: dict[str, list[str]] = {}
        for difficulty in DIFFICULTIES:
            loaded = self._load(difficulty)
            if not loaded:
                raise ValueError(f"{difficulty} word list is empty")
            self._words[difficulty] = loaded

    def words(self, difficulty: str) -> list[str]:
        """Return a copy of the cleaned words for a difficulty."""
        return list(self._words[self._normalize_difficulty(difficulty)])

    def random_word(self, difficulty: str) -> str:
        """Return a random word from the given difficulty list."""
        return self._rng.choice(self._words[self._normalize_difficulty(difficulty)])

    def _normalize_difficulty(self, difficulty: object) -> str:
        if not isinstance(difficulty, str):
            raise ValueError("Invalid difficulty")
        key = difficulty.strip().lower()
        if key not in self._words:
            raise ValueError("Invalid difficulty")
        return key

    def _load(self, difficulty: str) -> list[str]:
        path = self._directory / f"{difficulty}.txt"
        seen: set[str] = set()
        words: list[str] = []
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                word = line.strip().lower()
                if not word or not _is_ascii_alpha(word) or word in seen:
                    continue
                seen.add(word)
                words.append(word)
        return words
