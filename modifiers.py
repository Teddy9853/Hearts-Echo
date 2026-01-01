import re
from typing import Callable, Dict, Any, List


def _split_words(text: str) -> List[str]:
    # split on any non-alphanumeric character
    return [w for w in re.split(r"[^A-Za-z0-9]+", text) if w]


# Casing modifiers
def titleCase(text: str, **_globals) -> str:
    words = _split_words(text)
    return " ".join(w.capitalize() for w in words) if words else text


def camelCase(text: str, **_globals) -> str:
    words = _split_words(text)
    if not words:
        return text
    first = words[0].lower()
    rest = [w.capitalize() for w in words[1:]]
    return first + "".join(rest)


def capitalize(text: str, **_globals) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


def kebabCase(text: str, **_globals) -> str:
    words = _split_words(text)
    return "-".join(w.lower() for w in words) if words else text


def lowerCase(text: str, **_globals) -> str:
    return text.lower()


def snakeCase(text: str, **_globals) -> str:
    words = _split_words(text)
    return "_".join(w.lower() for w in words) if words else text


def startCase(text: str, **_globals) -> str:
    words = _split_words(text)
    return " ".join(w.capitalize() for w in words) if words else text


def upperCase(text: str, **_globals) -> str:
    return text.upper()


def pascalCase(text: str, **_globals) -> str:
    words = _split_words(text)
    return "".join(w.capitalize() for w in words) if words else text


# Simple morphological modifiers (heuristic, deterministic, failure-safe)

def adjective(text: str, **_globals) -> str:
    if not text:
        return text
    t = text
    if t.endswith("y") or t.endswith("ful") or t.endswith("ous") or t.endswith("ish") or t.endswith("ive"):
        return t
    if t.endswith("e"):
        return t[:-1] + "y"
    return t + "y"


def adverb(text: str, **_globals) -> str:
    if not text:
        return text
    t = text
    if t.endswith("ly"):
        return t
    if t.endswith("ic"):
        return t + "ally"
    return t + "ly"


def verb(text: str, **_globals) -> str:
    if not text:
        return text
    t = text
    if t.endswith("ize") or t.endswith("ate") or t.endswith("en"):
        return t
    if t.endswith("y"):
        return t[:-1] + "ify"
    return t + "ize"


def noun(text: str, **_globals) -> str:
    if not text:
        return text
    t = text
    if t.endswith("tion") or t.endswith("ness") or t.endswith("ment"):
        return t
    if t.endswith("e"):
        return t + "tion"
    return t + "ness"


# Registry of modifiers
MODIFIERS: Dict[str, Dict[str, Any]] = {
    "titleCase": {"func": titleCase, "description": "Transform the text into Title Case"},
    "camelCase": {"func": camelCase, "description": "Transform the text into camel case"},
    "capitalize": {"func": capitalize, "description": "Capitalize the first character of the text"},
    "kebabCase": {"func": kebabCase, "description": "Transform the text into kebab-case"},
    "lowerCase": {"func": lowerCase, "description": "Transform the text into lowercase"},
    "snakeCase": {"func": snakeCase, "description": "Transform the text into snake_case"},
    "startCase": {"func": startCase, "description": "Transform the text into Start Case"},
    "upperCase": {"func": upperCase, "description": "Transform the text into UPPERCASE"},
    "pascalCase": {"func": pascalCase, "description": "Transform the text into PascalCase"},
    "adjective": {"func": adjective, "description": "Transform the word into an adjective form (heuristic)"},
    "adverb": {"func": adverb, "description": "Transform the word into an adverb form (heuristic)"},
    "verb": {"func": verb, "description": "Transform the word into a verb form (heuristic)"},
    "noun": {"func": noun, "description": "Transform the word into a noun form (heuristic)"},
}


def list_modifiers() -> List[Dict[str, str]]:
    return [{"name": name, "description": info["description"]} for name, info in MODIFIERS.items()]


def apply_modifier(name: str, text: str, globals_dict: Dict[str, Any] | None = None) -> str:
    """
    Apply modifier by name to given text. Must not raise; on error return original text.
    globals_dict is provided to allow modifiers to inspect global parameters if needed.
    """
    if globals_dict is None:
        globals_dict = {}
    try:
        info = MODIFIERS.get(name)
        if info is None:
            return text
        func: Callable = info["func"]
        result = func(text, **globals_dict)
        return result if isinstance(result, str) else text
    except Exception:
        return text
