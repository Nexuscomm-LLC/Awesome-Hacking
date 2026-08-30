# Security Policy

## Scope

This repository is a **curated list of links**. It ships no executable code,
no packages, and no binaries. Its security surface is therefore:

1. The outbound links in `README.md` that point to third-party repositories.
2. The GitHub Actions workflows under `.github/workflows/`.

## Reporting a problem

Please open an issue, or use GitHub's private vulnerability reporting
(**Security → Report a vulnerability**) for anything that should not be
disclosed publicly straight away.

We are especially interested in reports of:

- **A listed link that no longer points where it used to.** A repository that
  was deleted, renamed, or transferred frees its old namespace. Anyone can then
  claim that namespace and serve different content from a URL this list still
  endorses. This is the highest-impact issue this repository can have, because
  readers clone what they find here and run it.
- **A listed project that has been compromised, taken over, or turned
  malicious**, even though the URL is unchanged.
- **Typosquatting** — an entry that points at a lookalike of the intended
  project.
- Any issue in the workflows in `.github/workflows/`.

When reporting a link problem, please include the entry as it appears in
`README.md`, what the URL resolves to now, and what it should point to.

## What we will do

Confirmed bad or hijacked links are removed or corrected promptly. Because
inclusion in this list is an implicit endorsement, we would rather drop an
entry than leave a questionable one in place.

## A note for readers

Inclusion here is a pointer, not an audit. Nothing in this list has been
reviewed for safety by this project. Evaluate any tool before you run it, and
prefer pinned commits over moving branches when you clone.
