"""
Evolution API Messaging Handler Module.
"""

import base64
import mimetypes
import os
from typing import Any, Tuple, Union

import requests

from ..core.i18n import t
from .base import EvolutionBase


class MessagingHandler(EvolutionBase):
    """
    Handles internal message sending logic (Text & Media).
    """

    def _send_evolution_text(
        self, evolution_url: str, instance: str, headers: dict, phone: str, text: str
    ) -> Tuple[bool, Any]:
        """Send Text via Evolution API."""
        url = f"{evolution_url}/message/sendText/{instance}"
        phone = self._normalize_phone(phone)

        payload = {"number": phone, "text": text}
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=30)
            return res.status_code in [200, 201], res.json()
        except requests.RequestException as e:
            return False, t("cloud.errors.net_error", "Network Error: {msg}").format(
                msg=str(e)
            )
        except Exception as e:
            return False, t("cloud.errors.server_error", "Server Error: {msg}").format(
                msg=str(e)
            )

    def _normalize_phone(self, phone: str) -> str:
        phone = str(phone).replace("+", "").strip()
        if "@" not in phone:
            phone = f"{phone}@s.whatsapp.net"
        return phone

    def _send_evolution_media(
        self,
        evolution_url: str,
        instance: str,
        headers: dict,
        phone: str,
        caption: str,
        file_path_or_bytes: Union[str, bytes],
        media_type: str = "image",
    ) -> Tuple[bool, Any]:
        """Send Media via Evolution API."""
        try:
            b64_data, mime_type = self._prepare_media(file_path_or_bytes)
            if not b64_data:
                return False, t(
                    "cloud.errors.media_prep_failed", "Media preparation failed"
                )

            phone = self._normalize_phone(phone)
            url = f"{evolution_url}/message/sendMedia/{instance}"

            # Auto-detect media type if generic 'image' was passed but mime says otherwise
            if media_type == "image":
                if "video" in mime_type:
                    media_type = "video"
                elif "application" in mime_type or "text" in mime_type:
                    media_type = "document"

            ext = self._get_extension(mime_type)
            payload = {
                "number": phone,
                "mediatype": media_type,
                "mimetype": mime_type,
                "caption": caption,
                "media": b64_data,
                "fileName": ext,
                "options": {"delay": 1200, "presence": "composing"},
            }

            res = requests.post(url, json=payload, headers=headers, timeout=60)
            return res.status_code in [200, 201], res.json()
        except requests.RequestException as e:
            return False, t("cloud.errors.net_error", "Network Error: {msg}").format(
                msg=str(e)
            )
        except Exception as e:
            return False, t("cloud.errors.server_error", "Server Error: {msg}").format(
                msg=str(e)
            )

    def _prepare_media(self, media: Union[str, bytes]) -> Tuple[str, str]:
        if isinstance(media, bytes):
            return base64.b64encode(media).decode("utf-8"), "image/jpeg"
        if isinstance(media, str) and os.path.exists(media):
            mime_type, _ = mimetypes.guess_type(media)
            with open(media, "rb") as f:
                return (
                    base64.b64encode(f.read()).decode("utf-8"),
                    mime_type or "image/jpeg",
                )
        return "", ""

    def _get_extension(self, mime: str) -> str:
        if "image" in mime:
            return "image.jpeg"
        if "video" in mime:
            return "video.mp4"
        if "pdf" in mime:
            return "doc.pdf"
        return "file"
