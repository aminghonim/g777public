import json
import yaml
import logging

# Configure logger for Telemetry
logger = logging.getLogger("TOON_Telemetry")


class ToonConverter:
    def __init__(self, config_path="backend/config/toon_config.yaml"):
        self.config = self._load_config(config_path)
        self.enabled = self.config.get("enabled", True)
        self.excluded_keys = set(self.config.get("excluded_keys", []))

    def _load_config(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f).get("toon_settings", {})
        except FileNotFoundError:
            logger.warning("TOON config not found. Using defaults.")
            return {"enabled": True, "excluded_keys": []}

    def _dict_to_toon_recursive(self, data, indent=0):
        # Basic TOON representation logic (Indentation instead of brackets)
        result = []
        spacer = "  " * indent

        if isinstance(data, dict):
            for k, v in data.items():
                if k in self.excluded_keys:
                    result.append(f"{spacer}{k}: {json.dumps(v, ensure_ascii=False)}")
                elif isinstance(v, (dict, list)):
                    result.append(f"{spacer}{k}:")
                    result.append(self._dict_to_toon_recursive(v, indent + 1))
                else:
                    result.append(f"{spacer}{k}: {v}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    # For a dict inside a list, print the dash, then the dict content indented
                    first = True
                    for k, v in item.items():
                        if k in self.excluded_keys:
                            val_str = json.dumps(v, ensure_ascii=False)
                        elif isinstance(v, (dict, list)):
                            val_str = "\n" + self._dict_to_toon_recursive(v, indent + 2)
                        else:
                            val_str = str(v)

                        if first:
                            result.append(f"{spacer}- {k}: {val_str}")
                            first = False
                        else:
                            result.append(f"{spacer}  {k}: {val_str}")
                elif isinstance(item, list):
                    result.append(f"{spacer}-")
                    result.append(self._dict_to_toon_recursive(item, indent + 1))
                else:
                    result.append(f"{spacer}- {item}")
        else:
            return f"{spacer}{data}"

        return "\n".join(result)

    def to_toon(self, data: dict) -> str:
        if not self.enabled:
            return json.dumps(data, ensure_ascii=False)

        original_size = len(json.dumps(data, ensure_ascii=False))

        try:
            # Attempt TOON Conversion
            toon_output = self._dict_to_toon_recursive(data)
            optimized_size = len(toon_output)

            # Telemetry Tracking
            if self.config.get("telemetry", {}).get("log_savings", True):
                savings = (
                    ((original_size - optimized_size) / original_size) * 100
                    if original_size > 0
                    else 0
                )
                logger.info(
                    f"[TOON Telemetry] Original: {original_size} chars | Optimized: {optimized_size} chars | Saved: {savings:.2f}%"
                )

            return toon_output

        except Exception as e:
            # Fallback Mechanism (Zero-Regression)
            logger.error(
                f"[TOON Error] Conversion failed: {str(e)}. Falling back to standard JSON."
            )
            return json.dumps(data, ensure_ascii=False)
