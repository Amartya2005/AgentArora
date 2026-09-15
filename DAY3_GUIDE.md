# Day 3 Implementation Guide - Privacy Engine Integration

## ✅ Day 2 Completion Status

**Your Day 2 work is COMPLETE!** All acceptance criteria met:
- ✅ Raw values are replaced correctly
- ✅ Placeholders are consistent ([PERSON_01], [ACCOUNT_01], etc.)
- ✅ Useful non-sensitive context survives
- ✅ Original-value mapping remains local
- ✅ SanitizedPageState can be understood without seeing original values
- ✅ All 8 Day 2 tests passing

---

## 🚀 Day 3 Goal

**By tonight, the Privacy Engine must be the mandatory gateway between Member 1 and Member 3.**

### Key Objective

Ensure that:
1. Privacy Engine is the ONLY path for data flow
2. No raw-data bypass exists
3. Agent-facing payload is sanitized
4. The main task works end-to-end
5. Debug output does not expose test secrets

---

## 📁 New Files Created for Day 3

### 1. `src/privacy_engine.py` - The Gateway Module

This is the **mandatory gateway** between Member 1 (Browser) and Member 3 (Agent).

**Key Classes and Functions:**

```python
# Main class
class PrivacyEngine:
    def sanitize(page_state) -> sanitized_state
    def restore_value(placeholder) -> original_value  # Browser-side only
    def restore_text(sanitized_text) -> restored_text  # Browser-side only
    def get_local_mapping() -> mapping_dict  # Never send to Agent!
    def clear_session()  # Clear mappings when task ends
    def get_privacy_stats() -> stats_dict  # Safe statistics

# Convenience functions
sanitize_page_state(page_state) -> (sanitized_state, local_mapping)
get_global_engine() -> engine  # Maintains state across calls
reset_global_engine()  # Start new session
```

**Critical Privacy Verification:**

The `sanitize()` method includes automatic verification that NO raw sensitive values appear in the Agent-facing payload. If any leak is detected, it raises a `RuntimeError`.

---

## 🔒 Privacy Boundary Enforcement

### RAW DATA MUST STOP HERE

```
┌─────────────────┐
│   Member 1      │
│   (Browser)     │
│                 │
│  Raw PageState  │
└────────┬────────┘
         │
         │ Contains:
         │ - Rahul Sharma
         │ - 7845129034
         │ - ₹84,250
         │ - rahul.sharma@gmail.com
         │
         ▼
┌─────────────────────────────┐
│    PRIVACY ENGINE           │
│    THE GATEWAY              │
│                             │
│  ✓ Detect sensitive info    │
│  ✓ Replace with placeholders│
│  ✓ Keep mapping locally     │
│  ✓ Verify no leaks          │
└────────┬────────────────────┘
         │
         │ Contains:
         │ - [PERSON_01]
         │ - [ACCOUNT_01]
         │ - [MONEY_01]
         │ - [EMAIL_01]
         │
         ▼
┌─────────────────┐
│   Member 3      │
│   (Agent)       │
│                 │
│  SanitizedState │
└─────────────────┘
```

### What the Agent CANNOT See

- ❌ Real names
- ❌ Account numbers
- ❌ Money amounts
- ❌ Email addresses
- ❌ Phone numbers
- ❌ Any PII

### What the Agent CAN See

- ✅ Placeholders ([PERSON_01], [ACCOUNT_01])
- ✅ Element IDs (EL_001, EL_002)
- ✅ Non-sensitive context (merchant names, dates)
- ✅ Page structure and button labels
- ✅ Action possibilities

---

## 📊 Day 3 Testing

### Test Coverage

**14 comprehensive integration tests** covering:

1. ✅ Privacy Engine is the gateway
2. ✅ No raw data bypass exists
3. ✅ Agent-facing payload is sanitized
4. ✅ Local mapping is not in sanitized state
5. ✅ Main task works end-to-end
6. ✅ Restore value for browser execution
7. ✅ Privacy stats do not expose secrets
8. ✅ Debug output does not expose test secrets
9. ✅ Convenience API returns separated mapping
10. ✅ Global engine maintains session state
11. ✅ Clear session removes sensitive data
12. ✅ Privacy verification catches leaks
13. ✅ Complete data flow works
14. ✅ Interface contract is documented

### Run Tests

```bash
# Day 3 integration tests
python -m pytest tests/test_day3_integration.py -v

# Day 2 sanitization tests (regression check)
python -m pytest tests/test_day2_sanitization.py -v

# All tests
python -m pytest tests/ -v
```

**Current Status:** ✅ All 22 tests passing (8 Day 2 + 14 Day 3)

---

## 🔧 Usage Examples

### Example 1: Basic Sanitization

```python
from src.privacy_engine import PrivacyEngine

# Create engine
engine = PrivacyEngine()

# Raw PageState from Member 1
raw_page_state = {
    "schema_version": "1.0",
    "page_state_id": "PS_001",
    "captured_at": "2026-09-15T10:00:00Z",
    "url": "https://bank.example.com",
    "title": "Dashboard",
    "visible_text": "Welcome Rahul Sharma",
    "elements": [
        {
            "element_id": "EL_001",
            "role": "text",
            "label": "Name",
            "text": "Rahul Sharma",
            "visible": True,
            "enabled": True
        }
    ]
}

# Sanitize for Agent
sanitized_state = engine.sanitize(raw_page_state)

# Agent receives:
# sanitized_state["visible_text"] = "Welcome [PERSON_01]"
# sanitized_state["elements"][0]["text"] = "[PERSON_01]"

# The mapping stays local:
local_mapping = engine.get_local_mapping()
# {"[PERSON_01]": "Rahul Sharma"}
```

### Example 2: Complete Data Flow

```python
from src.privacy_engine import PrivacyEngine

# Step 1: Browser captures page
raw_state = capture_page()  # Member 1's job

# Step 2: Privacy Engine sanitizes
engine = PrivacyEngine()
sanitized_state = engine.sanitize(raw_state)

# Step 3: Agent receives sanitized state ONLY
agent_response = send_to_agent(sanitized_state)  # Member 3's job

# Step 4: Agent returns action
# Example: {"action_type": "fill", "element_id": "EL_005", "value": "[ACCOUNT_01]"}

# Step 5: Browser restores placeholder locally for execution
if "[ACCOUNT_01]" in agent_response["value"]:
    actual_value = engine.restore_value("[ACCOUNT_01]")
    execute_action(element_id, actual_value)  # Browser fills "7845129034"

# Step 6: Clear session when done
engine.clear_session()
```

### Example 3: Using Global Engine (Session Management)

```python
from src.privacy_engine import get_global_engine, reset_global_engine

# Start new task
reset_global_engine()
engine = get_global_engine()

# Process multiple pages in same session
for page in pages:
    sanitized = engine.sanitize(page)
    process(sanitized)

# Mapping persists across pages
print(f"Total placeholders: {len(engine.get_local_mapping())}")

# End session
engine.clear_session()
```

---

## 🎯 Day 3 Step-by-Step Completion

### ✅ Step 1 — Freeze the Interface

**Done!** Created `src/privacy_engine.py` with clear API:

**Input Contract (from Member 1):**
```python
PageState = {
    "schema_version": str,
    "page_state_id": str,
    "captured_at": str,
    "url": str,
    "title": str,
    "visible_text": str,
    "elements": List[Element]
}
```

**Output Contract (to Member 3):**
```python
SanitizedPageState = {
    "schema_version": str,
    "sanitized_state_id": str,  # New ID
    "source_page_state_id": str,  # Links to original
    "captured_at": str,
    "url": str,
    "title": str,
    "visible_text": str,  # Sanitized
    "elements": List[SanitizedElement],  # Sanitized
    "privacy_summary": {
        "sensitive_context_detected": bool,
        "redaction_count": int,
        "categories": List[str],
        "verification_passed": bool
    }
}
```

**Local Only (NEVER sent to Agent):**
```python
local_mapping = {
    "[PERSON_01]": "Rahul Sharma",
    "[ACCOUNT_01]": "7845129034",
    # ... etc
}
```

### ✅ Step 2 — Run the Complete Data Flow

**Done!** Tests verify:
- ✅ PageState received from Member 1
- ✅ Sensitive information detected
- ✅ Sanitized correctly
- ✅ Only SanitizedPageState sent to Member 3
- ✅ Agent actions handled without exposing mapping

### ✅ Step 3 — Verify the Privacy Boundary

**Done!** Implemented automatic verification:
- ✅ Captures exact Agent-facing payload
- ✅ Searches for raw sensitive values
- ✅ Raises error if any leak detected
- ✅ No alternate path around Privacy Engine

### ✅ Step 4 — Complete One Real Task

**Done!** Test simulates: "Find my latest transaction"
- ✅ Agent can see: Element IDs, roles, labels, "Amazon", date
- ✅ Agent cannot see: Actual transaction amount
- ✅ Agent sees placeholder: [MONEY_02]
- ✅ Task completes successfully

---

## 🔍 Privacy Verification

The Privacy Engine includes automatic leak detection:

```python
def _verify_privacy_boundary(self, sanitized_state):
    """Verify NO raw values appear in Agent payload."""
    serialized = json.dumps(sanitized_state)
    
    for raw_value in self.tokenizer.local_mapping.values():
        if raw_value in serialized:
            print("⚠️ PRIVACY VIOLATION: Raw value found")
            return False
    
    return True
```

This runs **automatically** on every `sanitize()` call!

---

## 📈 Privacy Statistics

Get safe statistics without exposing secrets:

```python
stats = engine.get_privacy_stats()

# Example output:
{
    "status": "protected",
    "redaction_count": 5,
    "categories": ["PERSON", "ACCOUNT", "MONEY", "EMAIL", "PHONE"],
    "placeholder_count": 6,
    "sensitive_context_detected": False,
    "verification_passed": True
}
```

---

## 🐛 Debugging Without Leaks

**BAD - Exposes Secrets:**
```python
# ❌ DON'T DO THIS
print(f"Processing account {account_number}")
log(f"User: {user_name}, Balance: {balance}")
```

**GOOD - Safe Debugging:**
```python
# ✅ DO THIS
print(f"Processing element {element_id}")
print(f"Redacted {stats['redaction_count']} values")
print(f"Categories: {stats['categories']}")
```

---

## ⚠️ Critical Rules for Day 3

1. **RAW DATA MUST STOP AT THE PRIVACY ENGINE**
   - No shortcuts from Member 1 to Member 3
   - Always use `engine.sanitize()` as the gateway

2. **LOCAL MAPPING IS LOCAL ONLY**
   - Never serialize the mapping
   - Never send it to the Agent
   - Never log raw values from the mapping

3. **AGENT SEES PLACEHOLDERS ONLY**
   - Agent input must pass verification
   - Any leak should raise an error immediately

4. **BROWSER RESTORES LOCALLY**
   - Only the browser calls `restore_value()` or `restore_text()`
   - Agent never needs to restore placeholders

5. **CLEAR SESSION WHEN DONE**
   - Call `engine.clear_session()` after task completes
   - Don't keep sensitive data in memory longer than needed

---

## 📝 Day 3 End-of-Day Acceptance Criteria

### Required Deliverables

✅ **No raw-data bypass exists**
   - Privacy Engine is the only gateway
   - No direct path from Member 1 to Member 3

✅ **Agent-facing payload is sanitized**
   - All sensitive values replaced with placeholders
   - Verification passes automatically

✅ **The main task works end-to-end**
   - Browser → Privacy → Agent → Browser flow complete
   - Agent can reason with placeholders
   - Browser can execute actions

✅ **Debug output does not expose test secrets**
   - Statistics are safe
   - Logs don't contain raw values
   - Error messages don't leak secrets

---

## 🎓 Key Learnings from Day 3

### 1. Consistent Tokenization

The Privacy Engine now tracks already-seen values in `raw_to_token_map` and reuses tokens when the same value appears again. This ensures "Rahul Sharma" gets the same `[PERSON_01]` token everywhere it appears.

### 2. Automatic Verification

Every `sanitize()` call includes automatic verification to catch leaks immediately. This is a **critical safety feature** that prevents accidental exposure.

### 3. Separation of Concerns

- **Member 1 (Browser)**: Captures raw page data
- **Privacy Engine**: Sanitizes and protects
- **Member 3 (Agent)**: Reasons with safe placeholders
- **Browser**: Restores locally for execution

### 4. Privacy-Aware Debugging

Statistics and logs must never expose raw values. Use placeholders and counts instead.

---

## 🚀 Next Steps for Day 4

Tomorrow's focus:
1. **Improve detection** - Handle more PII patterns
2. **Test failure cases** - Adversarial inputs, edge cases
3. **Measure performance** - Precision, recall, latency
4. **Add sensitive context** - Financial, medical, authentication domains

---

## 📞 Need Help?

If you get stuck on Day 3:

1. **Run the tests** - They show exactly what's expected
   ```bash
   python -m pytest tests/test_day3_integration.py -v
   ```

2. **Check privacy verification** - If tests fail, look for leaks
   ```python
   stats = engine.get_privacy_stats()
   print(f"Verification: {stats['verification_passed']}")
   ```

3. **Review test examples** - The test file has complete working examples

4. **Check this guide** - All patterns and examples are here

---

## ✅ Day 3 Status: COMPLETE

All acceptance criteria met:
- ✅ Interface frozen and documented
- ✅ Complete data flow working
- ✅ Privacy boundary verified
- ✅ Real task demonstrated
- ✅ All 14 integration tests passing
- ✅ All 8 Day 2 tests still passing
- ✅ No raw data leaks detected

**You're ready for Day 4!** 🎉

