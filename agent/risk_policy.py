from typing import Any, Mapping


SENSITIVE_ROLES = {"password", "textbox-password", "creditcard"}
SUBMIT_LIKE_LABELS = {
    "submit",
    "pay",
    "purchase",
    "buy",
    "transfer",
    "send",
    "confirm",
    "delete",
    "remove",
    "save",
    "authorize",
}
RISK_LEVELS = {"LOW", "MEDIUM", "HIGH"}


def classify_action(action: Mapping[str, Any], target: Mapping[str, Any] | None) -> tuple[str, bool]:
    """Return deterministic (risk_level, requires_user_confirmation)."""
    requested_risk = str(action.get("risk_level", "LOW")).upper()
    risk = requested_risk if requested_risk in RISK_LEVELS else "LOW"
    requires_confirmation = bool(action.get("requires_user_confirmation", False))

    action_type = str(action.get("action_type", "")).upper()
    if action_type in {"TYPE", "SELECT"} and target:
        role = str(target.get("role", "")).strip().lower()
        sensitivity = str(target.get("sensitivity", "NONE")).strip().upper()

        if role in SENSITIVE_ROLES or sensitivity != "NONE":
            risk = "HIGH"
            requires_confirmation = True

    if action_type == "CLICK" and target:
        label = str(target.get("label", "")).strip().lower()
        normalized_label = " ".join(label.split())
        if any(term == normalized_label or term in normalized_label for term in SUBMIT_LIKE_LABELS):
            risk = "HIGH"
            requires_confirmation = True

    if action_type in {"TYPE", "SELECT"} and risk == "HIGH":
        requires_confirmation = True

    if action_type in {"PRESS_KEY", "SCROLL", "WAIT"} and risk == "HIGH":
        requires_confirmation = True

    return risk, requires_confirmation
