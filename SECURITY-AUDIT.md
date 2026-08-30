# Security Audit — Awesome-Hacking

**Date:** 2026-08-30
**Commit audited:** 5a02f84
**Auditor:** automated review (Claude Code)

---

## 1. What this repository actually is

A curated list. Two tracked content files (`README.md`, `contributing.md`), one
image, one licence, and one GitHub Actions workflow. **No executable code, no
package manifests, no dependencies, no build.**

That shapes the whole audit. There is no injection, deserialisation, or memory
safety surface to look for. The real surface is only two things:

1. **What the list points at.** 88 links, of which 83 are unique GitHub
   repositories spread across **77 distinct owner namespaces**. Readers clone
   and run what they find here, so an entry is an implicit endorsement.
2. **What runs with write access.** One workflow, one third-party action.

---

## 2. Findings

| ID | Finding | Severity | Status |
|----|---------|----------|--------|
| F-01 | Third-party action pinned to a mutable tag | Medium | Open — needs a SHA |
| F-02 | `discussions: write` granted but likely unused | Low | Open — verify |
| F-03 | No security policy / disclosure path | Low | **Fixed** |
| F-04 | No monitoring of action dependencies | Low | **Fixed** |
| F-05 | No link-integrity checking in CI | Medium | Open — recommended |

---

### F-01 — Third-party action pinned to a mutable tag (Medium)

`.github/workflows/lock-threads.yml:20`

```yaml
- uses: dessant/lock-threads@v5
```

`v5` is a **mutable Git tag**, not an immutable reference. Whoever controls the
upstream repository — or anyone who compromises that account — can repoint `v5`
at different code at any time. The change requires no commit to this repository
and is invisible from here. On the next scheduled run (hourly, per the cron)
that code executes in a runner holding `GITHUB_TOKEN` with the permissions this
workflow grants:

```yaml
issues: write
pull-requests: write
discussions: write
```

This is not theoretical. It is the exact mechanism of the March 2025
`tj-actions/changed-files` compromise, in which tags across many released
versions were repointed to malicious code and consumers were affected without
changing anything on their side. GitHub's own hardening guidance is to pin
third-party actions to a full-length commit SHA.

**Remediation.** Replace the tag with the full 40-character commit SHA, keeping
the readable version in a trailing comment:

```yaml
- uses: dessant/lock-threads@<40-char-commit-sha>  # v5.x.y
```

Resolve the SHA with:

```sh
git ls-remote https://github.com/dessant/lock-threads refs/tags/v5
# or, for the exact release tag the v5 alias currently points at:
gh api repos/dessant/lock-threads/git/ref/tags/v5 --jq .object.sha
```

> The SHA is **deliberately not filled in here.** Outbound access to
> `github.com` and `api.github.com` is blocked by this environment's egress
> policy (HTTP 403), so it could not be resolved and verified. Guessing a commit
> hash would either break CI or, worse, look authoritative while being wrong.
> This one line is the only thing standing between this finding and closed.

The Dependabot config added under F-04 keeps that SHA current once it is set.

---

### F-02 — `discussions: write` granted but likely unused (Low)

The step configures only:

```yaml
issue-inactive-days: '7'
pr-inactive-days: '7'
```

No discussion-locking option is set, yet the workflow grants `discussions:
write`. If the action does not process discussions under this configuration,
the scope is unnecessary and simply widens what a compromised action (F-01)
could reach.

**Remediation.** Confirm against the docs for the version you pin, and if
discussions are not being locked, drop the line.

*Not changed in this pass:* verifying the action's behaviour requires reading
its documentation, which is on the blocked host. Removing a permission that
turns out to be required would break the workflow quietly, so this is reported
rather than applied.

---

### F-03 — No security policy (Low) — **Fixed**

There was no `SECURITY.md`, so there was no stated way to report a bad link and
no private disclosure path. For a repository whose main risk is a hijacked
outbound link, the reporting path *is* a control: it is how the maintainers
find out.

**Added `SECURITY.md`**, which defines the scope, names link hijacking and
takeover as the priority report types, points at GitHub private vulnerability
reporting, and tells readers plainly that inclusion here is not an audit.

---

### F-04 — No monitoring of action dependencies (Low) — **Fixed**

Actions were the only dependency in the repository and nothing was watching
them.

**Added `.github/dependabot.yml`** for the `github-actions` ecosystem, weekly.
This also makes F-01 sustainable: with an action pinned to a SHA, Dependabot
updates the SHA and keeps the trailing version comment accurate, so pinning does
not mean going stale.

---

### F-05 — No link-integrity checking (Medium, systemic)

This is the finding that matters most for a list, and it is a gap in process
rather than a single bad line.

83 repository links across 77 third-party namespaces are carried indefinitely
with nothing checking that they still resolve. The failure mode is specific and
serious:

> A listed repository is deleted, renamed, or transferred. Its old
> `owner/name` becomes free. Anyone may then claim that namespace and serve
> whatever they like from a URL that this list — read by people specifically
> looking for security tools to run — still endorses.

The endorsement is what makes it dangerous. A 404 is a broken link; a 404 that
someone *re-registers* is a supply-chain delivery channel with a trusted
referrer.

**Remediation.** Add a scheduled link-check workflow (for example `lychee`, or
a `curl` loop over the extracted URLs) that opens an issue on non-200
responses. Treat a redirect to a *different* `owner/name` as a finding too, not
just a hard 404 — a silent rename is the case most likely to be missed, because
the link still "works".

---

## 3. What was checked and found clean

An audit that lists only problems misstates the result. These were tested and
passed:

**Workflow**

- An explicit `permissions:` block is declared, so every scope not listed —
  `contents` included — is `none`. That is the correct least-privilege
  baseline and it is already right.
- No `actions/checkout`, so there is no `persist-credentials` token-exposure
  concern.
- No `${{ github.event.* }}` (or other attacker-controllable context)
  interpolated into a `run:` block — no script-injection vector.
- A `concurrency` group is set, so scheduled runs cannot pile up.
- No `pull_request_target`, no self-hosted runners, no secrets referenced.

**Links**

- **No plain `http://` links.** All 88 are HTTPS.
- **No URL shorteners or opaque redirectors** (`bit.ly`, `t.co`, `goo.gl`, …).
- **No `raw.githubusercontent`, gist, or direct binary/installer links**
  (`.exe`, `.msi`, `.jar`, `.sh`) — nothing that hands a reader an executable
  in one click.
- **No duplicate entries**, comparing GitHub links case-insensitively.
- All 6 non-GitHub links verified live (HTTP 200): `gchq.github.io/CyberChef`,
  `gtfobins.github.io`, `img.shields.io`, both `twitter.com` links, and
  `www.facebook.com/HackwithGithub`.

**Repository**

- No credentials, private keys, or tokens in the working tree or across all
  68 commits of history.

---

## 4. Scope and limitations

Read this section before treating anything above as a clean bill of health.

- **The 83 GitHub links were not verified.** This environment's egress policy
  blocks `github.com` and `api.github.com` (HTTP 403 from the proxy), and the
  proxy documentation is explicit that policy denials must be reported rather
  than routed around. The available GitHub API tooling is scoped to this
  repository alone, so it cannot resolve third-party links either.
  **No liveness, redirect, or namespace-reclaim testing was performed on them.**
  That is untested, not clean — and given F-05 it is precisely the area most
  likely to hold a real finding. It should be re-run from an environment with
  general egress.
- **GitHub Advanced Security secret scanning is not enabled** on this
  repository, so the API-based scan returned an error. Credential detection
  fell back to pattern matching over the tree and full history, which is
  weaker than GHAS.
- Link *content* was not assessed. Whether a live, correctly-named repository
  is trustworthy is out of scope for an automated pass.

---

## 5. Recommended order of work

1. **F-01** — pin the action to a SHA. One line; closes the only finding where
   third-party code executes with write access here.
2. **F-05** — add the scheduled link check, including the redirect-to-a-
   different-owner case.
3. **Re-run the link audit with general egress** and fold the results in.
4. **F-02** — confirm and drop `discussions: write` if unused.

---

## 6. Minor, non-security

`contributing.md` has a broken table-of-contents anchor: the entry
`#to-remove-from-the-list` does not match its heading, *Removing from the
List* (anchor `#removing-from-the-list`). Cosmetic only; noted so it is not
rediscovered as a finding later.
