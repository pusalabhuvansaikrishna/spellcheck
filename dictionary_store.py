import threading
from pathlib import Path

from spylls.hunspell import Dictionary

# Resolve dictionaries/ relative to this file, not the process's CWD.
# This makes the service safe to run from any working directory.
DICTIONARIES_DIR = Path(__file__).resolve().parent / "dictionaries"

_cache: dict[str, Dictionary] = {}
_custom_words: dict[str, set[str]] = {}
_write_lock = threading.Lock()


def get_dictionary(locale: str) -> Dictionary:
    """
    Loads (and caches) the hunspell Dictionary for a given locale.
    Expects DICTIONARIES_DIR/<locale>.dic and DICTIONARIES_DIR/<locale>.aff to exist.
    """
    if locale not in _cache:
        path = DICTIONARIES_DIR / locale
        if not path.with_suffix(".dic").exists():
            raise FileNotFoundError(
                f"No dictionary files found for locale '{locale}' at {path}.dic"
            )
        _cache[locale] = Dictionary.from_files(str(path))
    return _cache[locale]


# --- PWL (Personal Word List) helpers ---

def _pwl_path(locale: str) -> Path:
    return DICTIONARIES_DIR / f"{locale}.pwl"


def load_custom_words(locale: str) -> set[str]:
    p = _pwl_path(locale)
    if p.exists():
        return set(p.read_text(encoding="utf-8").splitlines())
    return set()


def get_custom_words(locale: str) -> set[str]:
    if locale not in _custom_words:
        _custom_words[locale] = load_custom_words(locale)
    return _custom_words[locale]


def save_custom_word(locale: str, word: str) -> None:
    """
    Persists a new word to the locale's .pwl file.
    Thread-safe: guards the file append with a lock since this runs
    in a threadpool and could be called concurrently.
    """
    p = _pwl_path(locale)
    p.parent.mkdir(parents=True, exist_ok=True)
    with _write_lock:
        with p.open("a", encoding="utf-8") as f:
            f.write(word.lower() + "\n")
