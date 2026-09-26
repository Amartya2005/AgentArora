# Testing Commands

Use the standard library test runner for the main suite:

```bash
python -m unittest discover -s tests -v
```

Use pytest for the pytest-based regression coverage:

```bash
pytest -q
```

For privacy detection regressions only:

```bash
pytest tests/test_day4_detection.py -q
```
