# Security Policy

## Reporting a Vulnerability

If you discover a potential security vulnerability in ATLAS-EO, please report it immediately by contacting security@atlas-eo.org or opening a security issue.

## Security Practices

- No hardcoded credentials, API keys, or tokens in source code.
- All secrets load via environment variables (`.env`).
- Container services run as non-root users.
- Automated vulnerability scanning enforced via CI pipelines.
