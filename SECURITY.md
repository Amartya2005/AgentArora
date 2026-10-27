# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in AgentArora, please avoid opening a public issue with exploit details.

Instead, contact the repository maintainers privately through the contact method available on the repository owner’s GitHub profile. Include:

- A clear description of the vulnerability
- The affected component or file
- Steps to reproduce the issue
- The potential security impact
- Any suggested mitigation, if available

Please allow maintainers reasonable time to investigate and prepare a fix before publicly disclosing the vulnerability.

## Scope

Security reports are especially useful for issues involving:

- Privacy-boundary bypasses
- Leakage of raw sensitive data into agent-facing state
- Authentication or authorization weaknesses
- Unsafe browser actions or policy bypasses
- Injection paths that can influence agent execution
- Browser-extension security issues
- Local transport security issues

AgentArora is currently a prototype, so reports should distinguish between prototype limitations and vulnerabilities that can cross an intended security boundary.

## Safe Testing

Do not test against systems, accounts, or data that you do not own or have explicit permission to test. Use local fixtures and isolated environments whenever possible.
