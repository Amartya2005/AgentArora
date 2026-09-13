import re
from typing import Dict, Tuple, List
from .detector import PrivacyDetector


class PrivacyTokenizer:
    """
    Tokenizes sensitive values into safe, structural placeholders while maintaining
    a secure local temporary memory map for reverse resolution.
    """

    def __init__(self):
        self.detector = PrivacyDetector()
        # Local, in-memory token mapping: token -> raw value
        self.token_map: Dict[str, str] = {}
        # Reverse lookup for idempotency: raw value -> token
        self.raw_to_token_map: Dict[str, str] = {}
        # Category counters for generating sequential token IDs
        self.category_counters: Dict[str, int] = {}

    def _generate_token(self, category: str, raw_value: str) -> str:
        """
        Generates or reuses a unique structural token placeholder for a given raw value.
        Example: 'PERSON_01', 'ACCOUNT_02', 'MONEY_01'
        """
        raw_key = raw_value.strip()
        if raw_key in self.raw_to_token_map:
            return self.raw_to_token_map[raw_key]

        category_upper = category.upper()
        # Map taxonomy categories to visual token prefixes
        token_prefix_map = {
            "EMAIL": "EMAIL",
            "PHONE": "PHONE",
            "NAME": "PERSON",
            "ADDRESS": "ADDRESS",
            "PASSWORD": "PASSWORD",
            "PAYMENT": "MONEY",
            "ACCOUNT": "ACCOUNT",
            "MESSAGE": "MESSAGE",
        }

        prefix = token_prefix_map.get(category_upper, "DATA")
        count = self.category_counters.get(prefix, 0) + 1
        self.category_counters[prefix] = count

        token = f"[{prefix}_{count:02d}]"

        # Store in local bidirectional maps
        self.token_map[token] = raw_key
        self.raw_to_token_map[raw_key] = token

        return token

    def sanitize_node(self, text: str, category_hint: str = None) -> Tuple[str, bool]:
        """
        Sanitizes a single text node string. Returns a tuple of (sanitized_text, is_modified).
        """
        if not text or not text.strip():
            return text, False

        clean_text = text.strip()

        # If an explicit category hint is provided, test directly
        categories_to_check = (
            [category_hint]
            if category_hint
            else [
                "email",
                "phone",
                "name",
                "address",
                "password",
                "payment",
                "account",
                "message",
            ]
        )

        for category in categories_to_check:
            detector_method = getattr(
                self.detector, f"detect_{category}", None
            )
            if detector_method and detector_method(clean_text):
                token = self._generate_token(category, clean_text)
                return token, True

        return text, False

    def restore_tokens(self, sanitized_text: str) -> str:
        """
        Resolves tokens back to their original sensitive values for local browser operations.
        """
        restored_text = sanitized_text
        for token, raw_value in self.token_map.items():
            restored_text = restored_text.replace(token, raw_value)
        return restored_text

    def clear_local_memory(self):
        """
        Wipes the local temporary token mapping.
        """
        self.token_map.clear()
        self.raw_to_token_map.clear()
        self.category_counters.clear()


def sanitize_text(text: str, category_hint: str = None) -> str:
    """
    Helper function to quickly sanitize a string payload.
    """
    tokenizer = PrivacyTokenizer()
    sanitized, _ = tokenizer.sanitize_node(text, category_hint)
    return sanitized