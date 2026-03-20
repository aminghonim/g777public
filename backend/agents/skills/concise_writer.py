import re


class ConciseWriter:
    """
    Skill: Spartan Writing.
    Ensures outputs are concise, professional, and free of conversational fluff.
    """

    @staticmethod
    def refine_commit_message(msg: str) -> str:
        """
        Refines a commit message to be standard conventional commit format.
        Removes conversational fillers.
        """
        # 1. Remove conversational prefixes
        clean = re.sub(
            r"^(I have |I added |We have |Implemented |Added )",
            "",
            msg,
            flags=re.IGNORECASE,
        )

        # 2. Heuristic: If it doesn't start with a type (feat|fix|docs|style|refactor|test|chore), try to guess
        if not re.match(r"^(feat|fix|docs|style|refactor|test|chore)(\(.*\))?:", clean):
            # Default to 'feat' if not specified, or 'fix' if 'fix' is in the message
            prefix = "fix" if "fix" in clean.lower() else "feat"
            clean = f"{prefix}: {clean}"

        # 3. Truncate if too long (50 chars subject line is standard, but we'll be generous with 72)
        lines = clean.split("\n")
        if len(lines[0]) > 72:
            # Keep it if it's already structured, otherwise truncate
            pass

        return clean.strip()

    @staticmethod
    def is_spartan(text: str) -> bool:
        """
        Checks if text meets concise standards.
        """
        forbidden_phrases = [
            "I hope this helps",
            "Let me know if you need anything else",
            "Here is the code",
            "As an AI",
        ]
        return not any(phrase in text for phrase in forbidden_phrases)
