from src.detector import PrivacyDetector, evaluate_item


def test_phone_detection_accepts_common_indian_formats():
    detector = PrivacyDetector()
    assert detector.detect_phone("9876543210")
    assert detector.detect_phone("+91 98765 43210")
    assert detector.detect_phone("91-98765-43210")


def test_phone_detection_rejects_order_and_product_identifiers():
    detector = PrivacyDetector()
    assert not detector.detect_phone("Order 9876543210")
    assert not detector.detect_phone("Product 9876543210")


def test_payment_detection_handles_currency_and_negative_context():
    assert evaluate_item("payment", "₹1,250.00")
    assert evaluate_item("payment", "INR 500")
    assert not evaluate_item("payment", "Score: 500")


def test_sensitive_context_matching_is_case_insensitive():
    assert evaluate_item("financial", "CREDIT CARD information")
    assert evaluate_item("authentication", "API KEY")
    assert evaluate_item("confidential", "INTERNAL USE ONLY")
