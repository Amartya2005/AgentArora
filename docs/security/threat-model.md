# Threat Model

Assets: raw page content, sensitive values, placeholder mappings, browser session state, action plans, and results.

Trust boundaries: webpage content is untrusted; raw PageState is observation data, not instructions; local sanitization precedes reasoning; deterministic policy governs actions; targets are revalidated before execution.

Threats include prompt injection, sensitive-value leakage, stale targets, arbitrary-code requests, and risk misclassification. Controls include schema validation, local redaction, independent verification, bounded recovery, opaque IDs, and confirmation gates.

Residual risk remains from unknown sensitive formats, compromised local runtimes, and semantic attacks. This prototype does not claim complete prompt-injection immunity.