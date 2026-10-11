# Privacy Review Checklist

- [ ] Raw sensitive values stay inside the local privacy boundary.
- [ ] Placeholder mappings never enter agent-facing payloads.
- [ ] URLs are sanitized before reasoning.
- [ ] Authentication inputs are excluded from ordinary extraction.
- [ ] Nested structures and malformed inputs are tested.
- [ ] Sanitization failures fail closed.
- [ ] Logs and errors do not echo protected values.
- [ ] Transport uses only documented contracts.
- [ ] Benchmark claims are scoped to measured datasets.