# CLAUDE.md - AI Assistant Guide for Awesome-Hacking

## Repository Overview

**Awesome-Hacking** is a curated meta-collection of awesome lists for hackers, pentesters, and security researchers. It serves as a central hub linking to specialized security-focused "awesome" repositories across GitHub.

- **License**: CC0 1.0 Universal (Public Domain)
- **Repository**: https://github.com/Hack-with-Github/Awesome-Hacking
- **Purpose**: Aggregate and organize security-related awesome lists

## Repository Structure

```
Awesome-Hacking/
├── README.md              # Main content - curated links in markdown tables
├── contributing.md        # Contribution guidelines
├── LICENSE                # CC0 1.0 Universal license
├── awesome_hacking.jpg    # Header banner image
├── CLAUDE.md              # This file - AI assistant guidance
└── .github/
    └── workflows/
        └── lock-threads.yml  # Auto-locks inactive issues/PRs after 7 days
```

## Content Organization

The README.md contains two main sections with markdown tables:

### 1. Awesome Repositories
Primary security-focused awesome lists covering:
- Application/Web Security
- Penetration Testing
- Malware Analysis
- CTF Resources
- Red Teaming
- IoT/Embedded Security
- OSINT
- And more specialized topics

### 2. Other Useful Repositories
Supplementary resources including:
- Cheatsheets and references
- Learning resources
- Tools and wordlists
- CVE databases
- Forensics resources

## Formatting Conventions

### Markdown Table Format
```markdown
Repository | Description
---- | ----
[Repository Name](URL) | Brief description of the resource
```

### Key Rules
1. **Alphabetical Order**: All entries MUST be sorted alphabetically within their section
2. **Link Format**: `[Display Name](GitHub URL)` followed by pipe `|` and description
3. **Descriptions**: Keep concise, explain what the resource offers
4. **Spacing**: Maintain consistent table alignment for readability

## Contribution Workflow

### Adding a Resource
1. Edit `README.md`
2. Add entry to the appropriate section (Awesome Repositories or Other Useful)
3. **Ensure alphabetical ordering** - this is critical
4. Submit a pull request

### Removing a Resource
- Report via issue if a link is broken or resource is no longer maintained
- The maintainers will review and remove if necessary

### Automated Processes
- **Lock Threads**: GitHub Action runs hourly to lock issues and PRs inactive for 7+ days
- Uses `dessant/lock-threads@v5`

## AI Assistant Guidelines

### When Modifying README.md
1. **Always verify alphabetical order** after any addition
2. **Check link validity** before adding new resources
3. **Match existing formatting** exactly (table structure, spacing)
4. **Categorize correctly** - determine if it belongs in "Awesome Repositories" or "Other Useful"

### Quality Criteria for New Entries
- Must be a legitimate security/hacking resource
- Should be actively maintained (check last commit date)
- Must provide value to the security community
- Avoid duplicates - check if similar resource already listed

### What NOT to Do
- Do not add malicious resources or tools designed solely for illegal activities
- Do not add personal/promotional links without community value
- Do not break alphabetical ordering
- Do not modify the header image or license

### Common Tasks

**Adding a new awesome list:**
```markdown
[New Resource Name](https://github.com/user/repo) | Description of the resource
```
Insert in alphabetically correct position within the appropriate table.

**Updating a description:**
Find the existing entry and modify only the description text after the `|`.

**Fixing a broken link:**
Update the URL in parentheses while keeping the display name consistent.

## Build/Test Commands

This is a documentation-only repository with no build system. Validation is manual:
- Verify markdown renders correctly
- Verify all links are functional
- Verify alphabetical ordering

## Social Media

The project maintains presence on:
- Twitter: [@HackwithGithub](https://twitter.com/HackwithGithub)
- Facebook: [HackwithGithub](https://www.facebook.com/HackwithGithub)

## Contributors

See `contributing.md` for the list of contributors and detailed contribution instructions.
