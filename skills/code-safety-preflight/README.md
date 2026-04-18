# /code-safety-preflight

A triage aid that sweeps a repository for hardcoded secrets, credentials embedded in connection strings, committed sensitive files, and a short list of unsafe coding patterns. It is a checklist Claude Code works through, not a security control.

## What it will not catch

v0.1. A stopgap until deterministic secret scanners are in place (Semgrep, Nosey Parker, TruffleHog, Gitleaks). It does not:

- Inspect git history. Secrets committed and then deleted stay invisible to this audit.
- Detect high-entropy strings with no known prefix. There is no Shannon entropy check.
- Verify that any detected key is live.
- Recognise custom or firm-specific secret formats beyond the regex list in Step 2.
- Decode binary blobs, container images, encrypted archives, or dependency contents.

Run a proper scanner before relying on this for anything that matters.

## How it works

Seven steps. Every command output is pasted verbatim, empty output is reported as "no matches", and any step that cannot run is marked NOT RUN with a reason.

1. Confirm environment and tool versions.
2. Grep for known API-key shapes, JWTs, private-key headers, credentials in URLs, and assignment patterns that look like hardcoded secrets.
3. List tracked files whose names suggest credentials, plus `.env` variants that are not clearly examples.
4. Check `.gitignore` for common sensitive patterns.
5. Classify each hit as LIKELY REAL, LIKELY PLACEHOLDER, or UNCERTAIN, with evidence quoted before the classification.
6. Review any code in the current conversation for unparameterised SQL, `shell=True`, unsafe deserialisation, and a handful of other patterns.
7. Produce a structured report with a "What to do next" section and an explicit "Not checked" list.

Full specification: [`SKILL.md`](SKILL.md).

## Install

Requires [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Copy the skill into your repo:

```
cp -r skills/code-safety-preflight/ your-repo/.claude/skills/code-safety-preflight/
```

Then invoke:

```
/code-safety-preflight
```

It also auto-triggers on requests like "check the repo for leaked secrets", "scan for hardcoded API keys", or "pre-commit safety check".

## Adding firm-specific patterns

Step 2 has a placeholder for internal secret formats. Add regexes there before distributing the skill across a team:

```bash
# Firm-specific patterns -- add your own here before distributing internally.
grep -rnE $EXCLUDES -e '<internal-pattern>' .
```

Common candidates: internal token prefixes, staff SSO identifiers, bespoke licence keys, or any secret shape your organisation mints that is not covered by the public patterns in Step 2.
