# Security Issue Reporting

Please report suspected vulnerabilities responsibly and avoid publishing exploit details or private data in a public issue before maintainers can assess the risk.

## Useful report details
- A concise description of the suspected boundary or policy failure.
- The affected component and commit or release, if known.
- Minimal reproduction steps using synthetic data.
- Expected behavior and observed behavior.
- Sanitized logs and relevant test output.
- A realistic impact statement, including what information or action could be exposed.

## Do not include
- Real credentials, session cookies, OTPs, private messages, or customer records.
- Unredacted screenshots of personal or financial pages.
- Live exploit payloads targeting third-party systems.

## Triage priorities
Prioritize raw-data leakage across the privacy boundary, policy bypass, unauthorized high-impact actions, unsafe stale-element recovery, and secret exposure in logs. If a report involves live data, remove or redact it from shared artifacts as soon as possible.
