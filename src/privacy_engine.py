"""
Privacy Engine - Day 3 Integration Module

This is the MANDATORY gateway between Member 1 (Browser) and Member 3 (Agent).
All PageState must flow through this module for sanitization.

Contract:
    Input:  PageState (from Member 1)
    Output: SanitizedPageState (to Member 3)
    
The local mapping (placeholder → original value) is kept in-memory and 
NEVER sent to the Agent.
"""

from typing import Dict, Any, Tuple, Optional
from .tokenizer import PrivacyTokenizer
import json


class PrivacyEngine:
    """
    The Privacy Engine is the mandatory gateway that ensures no raw sensitive
    data reaches the Agent.
    
    RAW DATA MUST STOP HERE.
    """
    
    def __init__(self):
        self.tokenizer = PrivacyTokenizer()
        self._last_sanitized_state: Optional[Dict[str, Any]] = None
        
    def sanitize(self, page_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Primary entry point: Convert raw PageState to SanitizedPageState.
        
        Args:
            page_state: Raw PageState from Member 1's browser extension
            
        Returns:
            SanitizedPageState safe for Member 3's Agent
            
        The local mapping remains in self.tokenizer.local_mapping and is
        NEVER included in the returned object.
        """
        if not isinstance(page_state, dict):
            raise TypeError("page_state must be a dictionary")
            
        # Sanitize the page state
        sanitized_state = self.tokenizer.sanitize_page_state(page_state)
        
        # Store for verification purposes
        self._last_sanitized_state = sanitized_state
        
        # Verify privacy boundary - this is critical!
        if not self._verify_privacy_boundary(sanitized_state):
            raise RuntimeError(
                "PRIVACY VIOLATION: Raw sensitive values detected in Agent-facing payload"
            )
        
        return sanitized_state
    
    def _verify_privacy_boundary(self, sanitized_state: Dict[str, Any]) -> bool:
        """
        Verify that NONE of the original sensitive values appear in the
        Agent-facing payload.
        
        This is the core privacy guarantee.
        """
        if not self.tokenizer.local_mapping:
            return True
            
        # Serialize the entire sanitized state
        serialized = json.dumps(sanitized_state, ensure_ascii=False)
        
        # Check that no raw value appears in the serialized output
        for raw_value in self.tokenizer.local_mapping.values():
            if raw_value in serialized:
                # Log the violation (without exposing the value)
                print(f"⚠️  PRIVACY VIOLATION: Raw value found in sanitized output")
                return False
                
        return True
    
    def restore_value(self, placeholder: str) -> Optional[str]:
        """
        Restore a placeholder to its original value.
        
        This should ONLY be used by the browser for executing actions,
        NEVER by the Agent.
        
        Args:
            placeholder: Token like [PERSON_01] or [ACCOUNT_01]
            
        Returns:
            Original value, or None if placeholder not found
        """
        return self.tokenizer.local_mapping.get(placeholder)
    
    def restore_text(self, sanitized_text: str) -> str:
        """
        Restore all placeholders in text to original values.
        
        Use case: Browser needs to fill form fields based on Agent instructions.
        The Agent says "enter [ACCOUNT_01]" and the browser resolves it locally.
        """
        return self.tokenizer.restore_tokens(sanitized_text)
    
    def get_local_mapping(self) -> Dict[str, str]:
        """
        Access the local placeholder mapping.
        
        WARNING: This mapping contains original sensitive values.
        Use ONLY for local browser operations, NEVER send to Agent or external services.
        """
        return self.tokenizer.local_mapping.copy()
    
    def clear_session(self):
        """
        Clear all local mappings when a task/session ends.
        
        This removes the original sensitive values from memory.
        """
        self.tokenizer.clear_local_memory()
        self._last_sanitized_state = None
    
    def get_privacy_stats(self) -> Dict[str, Any]:
        """
        Get privacy protection statistics for the last sanitization.
        
        Returns a summary that does NOT contain the original values.
        """
        if not self._last_sanitized_state:
            return {
                "status": "no_sanitization_performed",
                "redaction_count": 0,
                "categories": [],
                "placeholder_count": 0
            }
        
        summary = self._last_sanitized_state.get("privacy_summary", {})
        
        return {
            "status": "protected",
            "redaction_count": summary.get("redaction_count", 0),
            "categories": summary.get("categories", []),
            "placeholder_count": len(self.tokenizer.local_mapping),
            "sensitive_context_detected": summary.get("sensitive_context_detected", False),
            "verification_passed": summary.get("verification_passed", False)
        }


# Convenience function for simple use cases
def sanitize_page_state(page_state: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Convenience function that returns both the sanitized state and the local mapping.
    
    WARNING: Callers MUST keep the mapping local. Do not send it to the Agent.
    
    Returns:
        (sanitized_state, local_mapping)
    """
    engine = PrivacyEngine()
    sanitized_state = engine.sanitize(page_state)
    local_mapping = engine.get_local_mapping()
    return sanitized_state, local_mapping


# Global singleton for maintaining session state across calls
_global_engine: Optional[PrivacyEngine] = None


def get_global_engine() -> PrivacyEngine:
    """
    Get or create the global Privacy Engine instance.
    
    Use this when you need to maintain the local mapping across multiple calls.
    """
    global _global_engine
    if _global_engine is None:
        _global_engine = PrivacyEngine()
    return _global_engine


def reset_global_engine():
    """
    Reset the global Privacy Engine instance.
    
    Call this when starting a new task/session.
    """
    global _global_engine
    _global_engine = None
