from src.detector import evaluate_item


def test_unknown_category_is_safe_by_default():
    assert evaluate_item("unknown-category", "anything") is False


def test_name_detection_requires_capitalized_multiword_names():
    assert evaluate_item("name", "Rita Das")
    assert not evaluate_item("name", "rita das")
    assert not evaluate_item("name", "Amazon India")


def test_address_detection_requires_structural_signal():
    assert evaluate_item("address", "42 MG Road, Sambalpur")
    assert evaluate_item("address", "Flat 4, Sector 7")
    assert not evaluate_item("address", "home page")


def test_password_detection_requires_context_or_short_numeric_secret():
    assert evaluate_item("password", "password: hunter2")
    assert evaluate_item("password", "123456")
    assert not evaluate_item("password", "password policy")
