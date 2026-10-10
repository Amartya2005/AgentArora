# Local Development Setup

This guide describes a cautious workflow for developing AgentArora locally. Check the repository's current scripts and dependency files before running commands; this prototype may evolve faster than documentation.

## Before you start
- Use a supported, up-to-date Chromium-based browser for extension testing.
- Install the project's declared dependencies using the package manager indicated by its lockfile.
- Keep API keys, cookies, real account data, and other secrets out of source control.
- Use synthetic pages and test values during development.

## Suggested workflow
1. Clone the repository and create a short-lived feature branch.
2. Read the root and extension READMEs, schemas, and existing tests.
3. Install dependencies using the existing lockfile rather than upgrading packages opportunistically.
4. Run the checks already defined by the project.
5. Load the extension locally using the browser's extension developer mode, following the extension-specific instructions.
6. Exercise the flow on a controlled test page before trying ordinary websites.
7. Review the diff for accidental secrets, captured personal data, and unrelated changes.

## Debugging
Prefer reproducible fixtures over debugging against live personal accounts. When reporting a bug, record the browser version, relevant steps, expected behavior, actual behavior, and sanitized console output.

## Safety note
Do not use real passwords, OTPs, payment details, or private messages as test fixtures. A privacy tool should not require exposing the very data it is meant to protect.
