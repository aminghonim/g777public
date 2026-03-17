import json
from typing import Any, Dict, List, Union


class ToonConverter:
    """
    ToonConverter - Token-Oriented Object Notation (TOON) Utility.
    Converts standard Python Dict/List structures into token-efficient TOON format.
    Ref: https://medium.com/google-cloud/save-tokens-with-toon-using-google-antigravity-...
    """

    @staticmethod
    def to_toon(obj: Any, indent: int = 0) -> str:
        """
        Recursively converts an object to TOON string.
        """
        spacing = "  " * indent

        if isinstance(obj, dict):
            lines = []
            for key, value in obj.items():
                if value is None:
                    continue

                # Simple value
                if not isinstance(value, (dict, list)):
                    lines.append(
                        f"{spacing}{key}: {ToonConverter._escape_value(value)}"
                    )
                else:
                    # Nested structure
                    lines.append(f"{spacing}{key}")
                    lines.append(ToonConverter.to_toon(value, indent + 1))
            return "\n".join(lines)

        elif isinstance(obj, list):
            lines = []
            for item in obj:
                if not isinstance(item, (dict, list)):
                    lines.append(f"{spacing}- {ToonConverter._escape_value(item)}")
                else:
                    # Nested object in list
                    # We use a leading dash followed by the first key or inner content
                    inner = ToonConverter.to_toon(item, indent + 1).lstrip()
                    lines.append(f"{spacing}- {inner}")
            return "\n".join(lines)

        else:
            return f"{spacing}{ToonConverter._escape_value(obj)}"

    @staticmethod
    def _escape_value(val: Any) -> str:
        """
        Sanitize value for TOON format.
        Removes quotes unless necessary for special characters.
        """
        if isinstance(val, bool):
            return str(val).lower()
        if isinstance(val, (int, float)):
            return str(val)

        # String sanitization
        s = str(val).strip()
        # If contains colons or newlines, we keep it simple for now or
        # could add more advanced quoting if the AI gets confused.
        # TOON favors raw text.
        return s


def json_to_toon(json_str: str) -> str:
    """Helper to convert JSON string to TOON"""
    data = json.loads(json_str)
    return ToonConverter.to_toon(data)
