# Privacy Review Template

Complete this checklist when adding a feature that reads page content, sends context to a model, stores results, or executes browser actions.

## Feature
- Name:
- Owner:
- Related contracts or files:
- Intended user benefit:

## Data inventory
- Data fields read:
- Potentially sensitive fields:
- Data retained locally:
- Data sent outside the browser:
- Logs or telemetry produced:

## Boundary analysis
- What is the minimum data required?
- Which component performs sanitization?
- How is successful sanitization independently verified?
- Can raw values or placeholder mappings enter model context?
- What happens when verification fails?

## Action and abuse analysis
- Can untrusted page content influence the task?
- Which actions can the feature trigger?
- What risk classification and confirmation rules apply?
- How are stale elements and uncertain outcomes handled?

## Evidence
- Tests added:
- Negative cases covered:
- Manual QA performed:
- Known limitations:
- Reviewer and review date:
