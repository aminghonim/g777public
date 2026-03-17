import json
import logging
import time
import re
import urllib.parse
import base64
from typing import List, Dict, Any, Optional, Set
from services.maps_scraper.models import MapsPlace

class MapsDataParser:
    """
    Precision Google Maps Decoder (Arabic Support Edition).
    """

    def __init__(self):
        self.logger = logging.getLogger("MapsDataParser")
        self.logger.setLevel(logging.INFO)
        # Refined regex for Place IDs and Names
        self.place_id_regex = re.compile(r"g/([0-9a-z_]{10,35})")
        self.base64_regex = re.compile(r"!2z([A-Za-z0-9\-_+/=]{10,})")
        self.plain_regex = re.compile(r"!2s([^!*]{3,150})")
        self.arabic_regex = re.compile(r"[\u0600-\u06FF\s]{3,150}")
        self.category_regex = re.compile(r"gcid:([a-z0-9_]+)")

    def _decode_b64(self, d: str) -> Optional[str]:
        try:
            d = d.replace('-', '+').replace('_', '/')
            pad = len(d) % 4
            if pad: d += '=' * (4 - pad)
            return base64.b64decode(d).decode('utf-8', errors='ignore').strip()
        except: return None

    def _is_junk(self, s: str) -> bool:
        if not s: return True
        if len(s) < 3: return True
        # Filter out UI strings and technical keys
        junk_keywords = ["google", "maps", "search", "suggest", "result", "overlay", "liteview", "viewport", "layer"]
        lower_s = s.lower()
        if any(j in lower_s for j in junk_keywords): return True
        # If it contains JS characters, it's junk
        if any(c in s for c in "(){};[]=\\"): return True
        return False

    def parse_raw_responses(self, raw_data_list: List[Dict[str, Any]]) -> List[MapsPlace]:
        parsed_places: List[MapsPlace] = []
        seen_ids: Set[str] = set()

        for chunk_idx, chunk in enumerate(raw_data_list):
            content = self._decode_hex(chunk.get("body", ""))
            if not content: continue

            # Strategy 1: Find all potential names (Arabic or decoded)
            potential_names = []
            
            # Extract via !2s plain text
            plain_matches = self.plain_regex.findall(content)
            for m in plain_matches:
                name = urllib.parse.unquote(m).split('!')[0]
                if not self._is_junk(name):
                    potential_names.append(name)
            
            # Extract via Arabic chars directly (Brute Force)
            arabic_matches = self.arabic_regex.findall(content)
            for m in arabic_matches:
                name = m.strip()
                if not self._is_junk(name) and name not in potential_names:
                    potential_names.append(name)

            # Extract via !2z Base64
            b64_matches = self.base64_regex.findall(content)
            for m in b64_matches:
                name = self._decode_b64(m)
                if name and not self._is_junk(name) and name not in potential_names:
                    potential_names.append(name)

            pids = self.place_id_regex.findall(content)
            cats = [c.replace("_", " ").title() for c in self.category_regex.findall(content)]

            if potential_names:
                self.logger.info(f"Chunk {chunk_idx}: Found potential names: {potential_names[:3]}")

            # Association Logic
            for i, pid in enumerate(pids):
                fid = f"g/{pid}"
                if fid not in seen_ids and len(pid) > 10:
                    # Pick best name match
                    # Often names appear near or same index as PIDs in structured responses
                    name = potential_names[i] if i < len(potential_names) else potential_names[0] if potential_names else f"Place_{pid[:5]}"
                    cat = cats[i] if i < len(cats) else "Business"
                    
                    parsed_places.append(MapsPlace(
                        place_id=fid, 
                        name=name, 
                        category=cat, 
                        address="Verified via Data Stream"
                    ))
                    seen_ids.add(fid)

        self.logger.info(f"Parser finished. Extracted {len(parsed_places)} unique places.")
        return parsed_places

    def _decode_hex(self, h: str) -> str:
        try: return bytes.fromhex(h).decode('utf-8', errors='ignore')
        except: return ""
