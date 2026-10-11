# Test Strategy

Test in layers: contract schemas, detector/tokenizer/policy unit tests, privacy-boundary tests, browser execution tests, orchestration-loop tests, and regression tests.

For security-sensitive rules, include accepted, rejected, and malformed cases. Prefer deterministic synthetic fixtures over live websites. Version benchmark datasets and record exact commands and runtime versions.

A privacy-verification, contract-validation, or policy failure blocks release until investigated.