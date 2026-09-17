def _is_digit(c: str) -> bool:
    return "0" <= c <= "9"


def _is_lower(c: str) -> bool:
    return "a" <= c <= "z"


def _is_upper(c: str) -> bool:
    return "A" <= c <= "Z"


def _is_alnum_us(c: str) -> bool:
    return _is_lower(c) or _is_upper(c) or _is_digit(c) or c == "_"
