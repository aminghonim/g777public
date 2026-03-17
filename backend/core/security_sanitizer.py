import re
import magic
from typing import Optional


class SecuritySanitizer:
    # ASVS V5: Input Sanitization (strip payloads, bound restrictions against ReDoS)
    _DANGEROUS_TAGS_RE = re.compile(
        r"<(script|object|embed|iframe|frame|applet|meta).*?>.*?</\1>",
        re.IGNORECASE | re.DOTALL,
    )

    @classmethod
    def sanitize_input(cls, text: str) -> str:
        """
        Safely sanitize text input by capping its length (to prevent ReDoS during processing),
        stripping null bytes, and removing common malicious HTML payload structures.
        """
        if not text:
            return ""

        # Cap length to avoid massive regex processing loads (ReDoS protection)
        if len(text) > 10_000:
            text = text[:10_000]

        # Strip null bytes (often used in C-based injection / path truncation)
        text = text.replace("\x00", "")

        # Strip overt dangerous HTML elements
        sanitized = cls._DANGEROUS_TAGS_RE.sub("", text)

        return sanitized.strip()


class SecureFileValidator:
    # ASVS V1 & V5: Whitelisted Magic Bytes and File Size Enforcement
    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "application/pdf",
        "text/csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "text/plain",
    }

    # Example maximum size quota: 5 MB
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

    @classmethod
    def validate_file(cls, file_content: bytes, filename: str) -> Optional[str]:
        """
        Validates the file via explicit quota checks and magic bytes analysis.
        Returns an error message string if invalid, None if safe.
        """
        # Quota limits checked strictly
        if len(file_content) > cls.MAX_FILE_SIZE_BYTES:
            return f"Validation Error: File '{filename}' exceeds {cls.MAX_FILE_SIZE_BYTES} bytes."

        # Magic Bytes Analysis
        detected_type = None
        try:
            # Standard python-magic behavior
            mime = magic.Magic(mime=True)
            detected_type = mime.from_buffer(file_content)
        except AttributeError:
            # Fallback for alternative python-magic distributions
            try:
                detected_type = magic.from_buffer(file_content, mime=True)
            except Exception as e:
                return f"Validation Error: fallback magic parsing failed: {str(e)}"
        except Exception as e:
            return f"Validation Error: Unable to extract file magic bytes: {str(e)}"

        # Whitelist enforcement
        if detected_type not in cls.ALLOWED_MIME_TYPES:
            return f"Validation Error: Upload denied. Magic bytes identify as '{detected_type}', which is forbidden."

        return None
