# Security Audit — Awesome-Hacking

**Date:** 2026-08-30 (revised 2026-09-03 — egress restored, all gaps closed)
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
| F-01 | Third-party action pinned to a mutable tag | Medium | **Fixed** — pinned to SHA |
| F-02 | `discussions: write` granted but likely unused | Low | **Closed — not a finding** (verified required) |
| F-03 | No security policy / disclosure path | Low | **Fixed** |
| F-04 | No monitoring of action dependencies | Low | **Fixed** |
| F-05 | No link-integrity checking in CI | Low | Open — recommended (all 82 links verified clean) |

> **Revision note (2026-09-03).** The original pass was blocked by an egress
> policy that denied `github.com` and `api.github.com`. That policy has since
> changed: git read access now works. Everything the first pass had to leave
> untested has now been tested. F-01 is fixed with a verified SHA, F-02 turned
> out not to be a defect, and the 83-link gap in §4 is closed.

---

### F-01 — Third-party action pinned to a mutable tag (Medium) — **Fixed**

`.github/workflows/lock-threads.yml:20` used `dessant/lock-threads@v5`. A tag is
**mutable**: it can be repointed upstream at any time, with no commit here and no
visible change, and the new code then runs hourly holding `issues: write`,
`pull-requests: write`, `discussions: write`. This is the mechanism of the March
2025 `tj-actions/changed-files` compromise.

**Fixed.** The step is now:

```yaml
- uses: dessant/lock-threads@1bf7ec25051fe7c00bdd17e6a7cf3d7bfb7dc771 # v5.0.1
```

How that SHA was established (not guessed):

- `git ls-remote https://github.com/dessant/lock-threads 'refs/tags/v5*'` reports
  `refs/tags/v5` → `1bf7ec25…`. There is **no** `refs/tags/v5^{}` entry, so `v5`
  is a lightweight tag pointing straight at a commit rather than an annotated
  tag object.
- The same SHA is what the annotated `refs/tags/v5.0.1^{}` dereferences to,
  which is where the `# v5.0.1` comment comes from.
- Fetched and confirmed with `git cat-file -t` → **`commit`**, message
  `chore(release): 5.0.1`. A tag-object SHA would not work in `uses:`; this is
  the commit.

Dependabot (F-04) now keeps this SHA and its version comment current, so pinning
does not mean going stale.

### F-02 — `discussions: write` — **Closed, not a finding**

The original pass flagged this as *probably* unnecessary, because the step
configures only `issue-inactive-days` and `pr-inactive-days`, and deliberately
did **not** remove it without checking. Checking now shows the caution was
warranted: the permission is **required**, and removing it would have silently
broken discussion locking.

From the action at the pinned commit:

- `process-only` defaults to `''` (empty). Its own description: *"Only lock
  issues, pull requests or discussions… list items must be one of `issues`,
  `prs` or `discussions`."* Empty means **no restriction — all three are
  processed.**
- `discussion-inactive-days` defaults to `'365'`, so discussions are locked on a
  default schedule whether or not the workflow names them.
- The upstream README's own recommended permissions block is exactly the three
  this repository already grants.

So the workflow's permissions are correct as written. No change made, and none
should be.

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

### F-05 — No link-integrity checking (Low; was Medium) — **verified clean, prevention still recommended**

This is the finding that matters most for a list. The failure mode is specific:

> A listed repository is deleted, renamed, or transferred. Its old `owner/name`
> becomes free. Anyone may then claim that namespace and serve whatever they
> like from a URL that this list — read by people specifically looking for
> security tools to run — still endorses.

**All 82 links have now been tested, and all 82 are clean.** Two passes:

1. **Liveness** — `git ls-remote <url> HEAD` against every link: **82/82
   resolved.** (An 83rd "link" in the first pass was an artifact of the
   extraction regex catching a URL inside the Twitter-intent query string, not a
   real entry.)
2. **Silent rename / owner change** — `git ls-remote` *follows* redirects, so a
   pass there does not by itself prove the owner is unchanged. Each link was
   therefore also probed at
   `https://github.com/<owner>/<repo>.git/info/refs?service=git-upload-pack`
   and the redirect target compared against the stated path: **0 redirects, 0
   renames.** Every link resolves to exactly the `owner/repo` the README claims.

So there is no dead link and no reclaimed namespace in the list today. The
severity drops to Low accordingly — what remains is a *prevention* gap, not a
live exposure.

**Still recommended.** Nothing keeps this true tomorrow. A scheduled workflow
should re-run both passes, because the second one is the case most likely to be
missed: a renamed repo still "works" when you click it. The two commands above
are the whole check.

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
- **All 82 GitHub repository links verified live, and verified to resolve to
  their stated `owner/repo`** — 0 dead, 0 renamed, 0 redirected (see F-05).

**Repository**

- No credentials, private keys, or tokens in the working tree or across all
  68 commits of history.

---

## 4. Scope and limitations

The original pass carried a large caveat here: `github.com` and
`api.github.com` were blocked by egress policy (HTTP 403), so the 83 GitHub
links could not be liveness-checked and the F-01 SHA could not be resolved. That
caveat is **now retired** — the policy changed, git read access works, and both
gaps were closed as described above.

What still limits this audit:

- **The GitHub REST API remains scope-gated.** `api.github.com` is reachable,
  but per-repository endpoints return 403 for repositories outside this
  session's grant. Link verification therefore used git's own transport
  (`ls-remote` and the `info/refs` endpoint), which is the right tool for the
  question anyway — it answers "does this resolve, and to whom" without reading
  repository contents.
- **GitHub Advanced Security secret scanning is not enabled** on this
  repository, so credential detection fell back to pattern matching over the
  tree and all 68 commits. That is weaker than GHAS.
- **Link *content* was not assessed.** Whether a live, correctly-named
  repository is trustworthy is out of scope for an automated pass. Inclusion in
  this list remains a pointer, not an endorsement of safety — which is why
  `SECURITY.md` says so to readers directly.

## 5. Recommended order of work

Everything actionable from the first pass is done. What remains:

1. **F-05** — add the scheduled link check (both passes: liveness *and*
   redirect-to-a-different-owner). This is the only open item, and it is
   prevention rather than remediation: the list is verified clean as of
   2026-09-03.
2. Optionally enable GHAS secret scanning to replace the pattern-matching
   fallback noted in §4.

## 6. Minor, non-security

`contributing.md` has a broken table-of-contents anchor: the entry
`#to-remove-from-the-list` does not match its heading, *Removing from the
List* (anchor `#removing-from-the-list`). Cosmetic only; noted so it is not
rediscovered as a finding later.
