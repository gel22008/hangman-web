"""Core Hangman game engine. Independent of Flask and any user interface."""

from __future__ import annotations


def _is_ascii_alpha(value: str) -> bool:
    return value.isascii() and value.isalpha()


class HangmanGame:
    """Server-authoritative Hangman rules for a single hidden word."""

    MAX_INCORRECT_GUESSES = 6

    def __init__(self, word: str) -> None:
        if not isinstance(word, str) or not word or not _is_ascii_alpha(word):
            raise ValueError("Word must contain only letters a-z")
        self._word = word.lower()
        self._guessed_letters: list[str] = []
        self._incorrect_letters: list[str] = []
        self._status = "playing"

    def guess(self, letter: str) -> dict:
        """Apply one letter guess and return the updated client-safe state."""
        if self._status != "playing":
            raise ValueError("No guesses allowed after the game has ended")

        if not isinstance(letter, str):
            raise ValueError("Guess must be a single letter")

        normalized = letter.lower()
        if len(normalized) != 1 or not _is_ascii_alpha(normalized):
            raise ValueError("Guess must be a single letter")

        if normalized in self._guessed_letters:
            raise ValueError("Letter already guessed")

        self._guessed_letters.append(normalized)
        if normalized in self._word:
            if all(character in self._guessed_letters for character in self._word):
                self._status = "won"
        else:
            self._incorrect_letters.append(normalized)
            if len(self._incorrect_letters) >= self.MAX_INCORRECT_GUESSES:
                self._status = "lost"

        return self.state()

    def state(self) -> dict:
        """Return a client-safe snapshot. The answer is included only after the game ends."""
        #remaining guesses calculated each time
        data = {
            "pattern": self._pattern(),
            "guessed_letters": list(self._guessed_letters),
            "incorrect_letters": list(self._incorrect_letters),
            "remaining_guesses": self.MAX_INCORRECT_GUESSES - len(self._incorrect_letters),
            "status": self._status,
        }
        if self._status in ("won", "lost"):
            data["word"] = self._word
        return data

    def _pattern(self) -> str:
        return " ".join(
            character if character in self._guessed_letters else "_"
            for character in self._word
        )
