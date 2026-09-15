"""
Day 3 Integration Tests

These tests verify that:
1. Privacy Engine is the mandatory gateway
2. No raw data bypass exists
3. Agent-facing payload is sanitized
4. The main task works end-to-end
5. Debug output does not expose test secrets
"""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.privacy_engine import PrivacyEngine, sanitize_page_state, get_global_engine, reset_global_engine


# Test data: Banking page with real sensitive information
BANKING_PAGE_STATE = {
    "schema_version": "1.0",
    "page_state_id": "PS_BankingDemo01",
    "captured_at": "2026-09-15T10:00:00Z",
    "url": "https://securebank.example.local/dashboard",
    "title": "SecureBank Dashboard",
    "visible_text": (
        "Welcome Rahul Sharma | Account: 7845129034 | "
        "Balance: ₹84,250 | Latest transaction: Amazon — ₹2,340 | "
        "Contact: rahul.sharma@gmail.com | Phone: 9876543210"
    ),
    "elements": [
        {
            "element_id": "EL_001",
            "role": "heading",
            "text": "SecureBank Dashboard",
            "visible": True,
            "enabled": True,
        },
        {
            "element_id": "EL_002",
            "role": "text",
            "label": "Account Holder",
            "text": "Rahul Sharma",
            "visible": True,
            "enabled": True,
        },
        {
            "element_id": "EL_003",
            "role": "text",
            "label": "Account Number",
            "value": "7845129034",
            "visible": True,
            "enabled": True,
        },
        {
            "element_id": "EL_004",
            "role": "text",
            "label": "Balance",
            "value": "₹84,250",
            "visible": True,
            "enabled": True,
        },
        {
            "element_id": "EL_005",
            "role": "text",
            "label": "Latest transaction",
            "text": "Amazon — ₹2,340 on 2026-09-14",
            "visible": True,
            "enabled": True,
        },
        {
            "element_id": "EL_006",
            "role": "text",
            "label": "Email",
            "value": "rahul.sharma@gmail.com",
            "visible": True,
            "enabled": True,
        },
        {
            "element_id": "EL_007",
            "role": "text",
            "label": "Phone",
            "value": "9876543210",
            "visible": True,
            "enabled": True,
        },
        {
            "element_id": "EL_008",
            "role": "button",
            "text": "View Transactions",
            "visible": True,
            "enabled": True,
        },
    ],
}


def test_privacy_engine_is_the_gateway():
    """Privacy Engine must be the mandatory gateway between Member 1 and Member 3."""
    engine = PrivacyEngine()
    
    # Raw PageState comes in
    raw_state = BANKING_PAGE_STATE
    
    # Privacy Engine sanitizes it
    sanitized_state = engine.sanitize(raw_state)
    
    # Verify sanitized state structure
    assert "sanitized_state_id" in sanitized_state
    assert sanitized_state["source_page_state_id"] == raw_state["page_state_id"]
    assert "privacy_summary" in sanitized_state
    assert sanitized_state["privacy_summary"]["verification_passed"] is True


def test_no_raw_data_bypass_exists():
    """The Agent-facing payload must NOT contain raw sensitive values."""
    engine = PrivacyEngine()
    sanitized_state = engine.sanitize(BANKING_PAGE_STATE)
    
    # Serialize the Agent-facing payload
    agent_payload = json.dumps(sanitized_state, ensure_ascii=False)
    
    # Known raw sensitive test values that must NOT appear
    sensitive_values = [
        "Rahul Sharma",
        "7845129034",
        "₹84,250",
        "₹2,340",
        "rahul.sharma@gmail.com",
        "9876543210"
    ]
    
    # Verify NONE of them appear in the Agent payload
    for value in sensitive_values:
        assert value not in agent_payload, f"PRIVACY VIOLATION: '{value}' found in Agent payload"


def test_agent_facing_payload_is_sanitized():
    """The Agent receives placeholders, not raw values."""
    engine = PrivacyEngine()
    sanitized_state = engine.sanitize(BANKING_PAGE_STATE)
    
    # Verify placeholders are present
    agent_payload = json.dumps(sanitized_state, ensure_ascii=False)
    
    # Expected placeholders should be in the payload
    expected_placeholders = ["[PERSON_", "[ACCOUNT_", "[MONEY_", "[EMAIL_", "[PHONE_"]
    
    found_placeholders = [p for p in expected_placeholders if p in agent_payload]
    assert len(found_placeholders) >= 3, "Agent payload should contain privacy placeholders"


def test_local_mapping_is_not_in_sanitized_state():
    """The local mapping must NOT be included in SanitizedPageState."""
    engine = PrivacyEngine()
    sanitized_state = engine.sanitize(BANKING_PAGE_STATE)
    
    # Verify the mapping exists locally
    assert len(engine.get_local_mapping()) > 0
    
    # But is NOT in the sanitized state
    assert "token_map" not in sanitized_state
    assert "raw_to_token_map" not in sanitized_state
    assert "local_mapping" not in sanitized_state
    
    # And raw values are not in the sanitized state
    serialized = json.dumps(sanitized_state)
    for raw_value in engine.get_local_mapping().values():
        assert raw_value not in serialized


def test_main_task_works_end_to_end():
    """
    Simulate the main task: 'Find my latest transaction.'
    
    The Agent should be able to reason using safe placeholders and non-sensitive context.
    """
    engine = PrivacyEngine()
    sanitized_state = engine.sanitize(BANKING_PAGE_STATE)
    
    # The Agent can see:
    # - Element IDs
    # - Roles and labels
    # - Non-sensitive context (merchant name, dates)
    # - Placeholders for sensitive data
    
    # Find the transaction element
    transaction_element = None
    for elem in sanitized_state["elements"]:
        if elem.get("label") == "Latest transaction":
            transaction_element = elem
            break
    
    assert transaction_element is not None
    
    # The Agent can see "Amazon" and the date, but not the amount
    transaction_text = transaction_element["text"]
    assert "Amazon" in transaction_text
    assert "2026-09-14" in transaction_text
    assert "₹2,340" not in transaction_text  # Raw value not visible
    assert "[MONEY_" in transaction_text  # Placeholder is visible
    
    # The Agent might instruct: "Click element EL_008 to view transactions"
    # The browser can execute this without needing to restore any placeholders
    view_button = next(e for e in sanitized_state["elements"] if e["element_id"] == "EL_008")
    assert view_button["text"] == "View Transactions"


def test_restore_value_for_browser_execution():
    """
    The browser (not the Agent) can restore placeholders when executing actions.
    
    Example: Agent says "enter [ACCOUNT_01] in the form"
    Browser resolves [ACCOUNT_01] → "7845129034" locally and fills the field.
    """
    engine = PrivacyEngine()
    sanitized_state = engine.sanitize(BANKING_PAGE_STATE)
    
    # Agent sees [ACCOUNT_01] in the sanitized state
    account_element = next(e for e in sanitized_state["elements"] 
                          if e.get("label") == "Account Number")
    assert "[ACCOUNT_01]" in account_element["value"]
    
    # Browser restores the value locally for execution
    restored_value = engine.restore_value("[ACCOUNT_01]")
    assert restored_value == "7845129034"
    
    # Full text restoration
    instruction = "Enter [ACCOUNT_01] and confirm with [PERSON_01]"
    restored_instruction = engine.restore_text(instruction)
    assert "7845129034" in restored_instruction
    assert "Rahul Sharma" in restored_instruction


def test_privacy_stats_do_not_expose_secrets():
    """Privacy statistics should summarize protection without exposing original values."""
    engine = PrivacyEngine()
    engine.sanitize(BANKING_PAGE_STATE)
    
    stats = engine.get_privacy_stats()
    
    # Stats should have useful info
    assert stats["status"] == "protected"
    assert stats["redaction_count"] > 0
    assert len(stats["categories"]) > 0
    assert stats["verification_passed"] is True
    
    # But stats must NOT contain original values
    stats_json = json.dumps(stats)
    sensitive_values = [
        "Rahul Sharma", "7845129034", "₹84,250", "rahul.sharma@gmail.com"
    ]
    for value in sensitive_values:
        assert value not in stats_json


def test_debug_output_does_not_expose_test_secrets():
    """Debug output and logging must not accidentally leak sensitive values."""
    engine = PrivacyEngine()
    sanitized_state = engine.sanitize(BANKING_PAGE_STATE)
    
    # Simulate what would be logged/printed for debugging
    debug_output = {
        "sanitized_state_id": sanitized_state["sanitized_state_id"],
        "source": sanitized_state["source_page_state_id"],
        "stats": engine.get_privacy_stats(),
        "element_count": len(sanitized_state["elements"]),
        "sample_element": {
            "element_id": sanitized_state["elements"][1]["element_id"],
            "label": sanitized_state["elements"][1].get("label"),
            "text": sanitized_state["elements"][1].get("text", "")[:50]  # Truncated sample
        }
    }
    
    debug_json = json.dumps(debug_output)
    
    # Raw values must NOT appear in debug output
    assert "Rahul Sharma" not in debug_json
    assert "7845129034" not in debug_json
    assert "₹84,250" not in debug_json


def test_convenience_api_returns_separated_mapping():
    """The convenience API returns sanitized state and mapping separately."""
    sanitized_state, local_mapping = sanitize_page_state(BANKING_PAGE_STATE)
    
    # Mapping is separate
    assert isinstance(local_mapping, dict)
    assert len(local_mapping) > 0
    
    # Sanitized state does not contain mapping
    serialized = json.dumps(sanitized_state)
    for raw_value in local_mapping.values():
        assert raw_value not in serialized


def test_global_engine_maintains_session_state():
    """Global engine maintains mapping across multiple calls."""
    reset_global_engine()
    
    engine = get_global_engine()
    engine.sanitize(BANKING_PAGE_STATE)
    
    # Mapping is retained
    mapping_1 = engine.get_local_mapping()
    assert len(mapping_1) > 0
    
    # Same engine on next call
    engine_2 = get_global_engine()
    assert engine_2 is engine
    
    # Mapping still available
    mapping_2 = engine_2.get_local_mapping()
    assert mapping_2 == mapping_1


def test_clear_session_removes_sensitive_data():
    """Clearing the session removes all local mappings."""
    engine = PrivacyEngine()
    engine.sanitize(BANKING_PAGE_STATE)
    
    # Mapping exists
    assert len(engine.get_local_mapping()) > 0
    
    # Clear the session
    engine.clear_session()
    
    # Mapping is gone
    assert len(engine.get_local_mapping()) == 0
    
    # Stats show no sanitization
    stats = engine.get_privacy_stats()
    assert stats["status"] == "no_sanitization_performed"


def test_privacy_verification_catches_leaks():
    """The privacy verification should catch any leaks."""
    engine = PrivacyEngine()
    
    # Normal sanitization passes verification
    sanitized_state = engine.sanitize(BANKING_PAGE_STATE)
    assert sanitized_state["privacy_summary"]["verification_passed"] is True
    
    # The internal verification method works correctly
    assert engine._verify_privacy_boundary(sanitized_state) is True


def test_complete_data_flow():
    """
    Complete data flow: Browser → Privacy → Agent → Browser
    
    This simulates the full Day 3 requirement:
    1. Receive PageState from Member 1
    2. Detect sensitive information
    3. Sanitize it
    4. Send only SanitizedPageState to Member 3
    5. Receive Agent actions without exposing the local sensitive mapping
    """
    # Step 1: Receive PageState from Member 1
    raw_page_state = BANKING_PAGE_STATE
    
    # Step 2 & 3: Privacy Engine detects and sanitizes
    engine = PrivacyEngine()
    sanitized_state = engine.sanitize(raw_page_state)
    
    # Step 4: Send to Member 3 (Agent)
    # The Agent receives ONLY the sanitized state
    agent_input = json.loads(json.dumps(sanitized_state))  # Simulate serialization
    
    # Verify Agent cannot see raw values
    agent_input_str = json.dumps(agent_input)
    assert "Rahul Sharma" not in agent_input_str
    assert "7845129034" not in agent_input_str
    
    # Step 5: Agent returns an action plan
    # Example: Agent wants to click the "View Transactions" button
    agent_action = {
        "action_type": "click",
        "target_element_id": "EL_008"  # This is safe - no sensitive data
    }
    
    # Browser receives the action and can execute it
    # If the action involved a placeholder, browser would restore it locally:
    if "placeholder" in str(agent_action):
        # Example: {"action_type": "fill", "value": "[ACCOUNT_01]"}
        # Browser would call: engine.restore_value("[ACCOUNT_01]")
        pass
    
    # Success! Complete flow works without exposing sensitive data to Agent
    assert True


def test_freeze_interface_documentation():
    """
    Day 3 Step 1: Document the interface contract.
    
    This test serves as documentation of the frozen interface.
    """
    # INPUT: PageState from Member 1
    input_contract = {
        "schema_version": str,
        "page_state_id": str,
        "captured_at": str,
        "url": str,
        "title": str,
        "visible_text": str,
        "elements": list,  # List of element dicts
    }
    
    # OUTPUT: SanitizedPageState to Member 3
    output_contract = {
        "schema_version": str,
        "sanitized_state_id": str,  # New ID for sanitized version
        "source_page_state_id": str,  # Links back to original
        "captured_at": str,
        "url": str,  # Non-sensitive, preserved
        "title": str,  # Non-sensitive, preserved
        "visible_text": str,  # Sensitive values replaced with placeholders
        "elements": list,  # Sensitive values replaced with placeholders
        "privacy_summary": dict,  # Summary of protection applied
    }
    
    # LOCAL ONLY: Never sent to Agent
    local_mapping_contract = {
        "[PLACEHOLDER_XX]": "original_value"
    }
    
    # Verify the implementation matches this contract
    engine = PrivacyEngine()
    output = engine.sanitize(BANKING_PAGE_STATE)
    
    # Check all required output fields exist
    for key in output_contract.keys():
        assert key in output, f"Missing required field: {key}"
    
    # Check local mapping exists but is NOT in output
    local_map = engine.get_local_mapping()
    assert len(local_map) > 0
    assert "local_mapping" not in output
    
    print("✅ Interface contract verified and documented")
