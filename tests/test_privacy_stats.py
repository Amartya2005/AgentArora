from src.privacy_engine import PrivacyEngine


def _state(text):
    return {
        "schema_version": "1.0",
        "page_state_id": "PS_stats",
        "captured_at": "2026-09-25T00:00:00Z",
        "url": "https://example.test/profile",
        "title": "Profile",
        "visible_text": text,
        "elements": [],
    }


def test_stats_before_sanitization_are_empty():
    stats = PrivacyEngine().get_privacy_stats()
    assert stats["status"] == "no_sanitization_performed"
    assert stats["redaction_count"] == 0
    assert stats["placeholder_count"] == 0


def test_stats_report_protected_state_after_sanitization():
    engine = PrivacyEngine()
    sanitized = engine.sanitize(_state("Contact rahul.sharma@example.com"))
    stats = engine.get_privacy_stats()

    assert stats["status"] == "protected"
    assert stats["verification_passed"] is True
    assert stats["redaction_count"] >= 1
    assert stats["placeholder_count"] >= 1
    assert sanitized["privacy_summary"]["verification_passed"] is True


def test_clear_session_resets_mapping_and_last_state():
    engine = PrivacyEngine()
    engine.sanitize(_state("Contact rahul.sharma@example.com"))
    assert engine.get_privacy_stats()["status"] == "protected"

    engine.clear_session()

    assert engine.get_privacy_stats()["status"] == "no_sanitization_performed"
    assert engine.get_local_mapping() == {}
