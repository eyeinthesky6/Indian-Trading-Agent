# Security policy

## Scope

Please report vulnerabilities that could cause unsafe calculations, malformed Trade Packets, secret leakage, dependency compromise or a path that unexpectedly enables execution.

## Hard boundary

This repository must not contain live broker credentials or an order-placement path. A change that makes `execution.allowed` true is a security/safety regression unless the repository boundary is explicitly redesigned first.

## Secrets

Never commit API keys, broker tokens, session cookies, private certificates or user portfolio data.

For sensitive reports, contact the repository owner privately rather than posting exploitable details in a public issue.
