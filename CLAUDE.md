# CLAUDE.md - AI Assistant Guide for Awesome-Hacking

## Repository Overview

**Awesome-Hacking** is a curated meta-repository that aggregates and organizes high-quality security and hacking resources from across GitHub. It serves as a centralized index linking to other "awesome" lists, tools, and resources for hackers, penetration testers, and security researchers.

**Repository Type**: Curated List (Awesome List)
**Primary Language**: Markdown
**Maintenance Status**: Active (community-maintained)
**Original Repository**: https://github.com/Hack-with-Github/Awesome-Hacking

## Core Philosophy

This repository follows the "awesome list" philosophy:
- **Quality over quantity**: Only include well-maintained, valuable resources
- **Community-driven**: Contributions from the security community
- **Organization**: Resources categorized by security domain
- **Accessibility**: Easy to navigate and discover resources

## Repository Structure

```
Awesome-Hacking/
├── README.md              # Main content file with curated lists
├── contributing.md        # Contribution guidelines
├── LICENSE               # MIT License
├── awesome_hacking.jpg   # Repository banner image
└── .github/
    └── workflows/
        └── lock-threads.yml  # Auto-locks inactive issues/PRs after 7 days
```

### Key Files

#### README.md
- **Purpose**: Main content file containing all curated lists
- **Structure**:
  - Header with banner image and description
  - Two main sections:
    1. **Awesome Repositories**: Security-focused awesome lists
    2. **Other Useful Repositories**: Complementary security resources
  - Each section uses markdown tables with two columns: Repository (with link) | Description
- **Ordering**: All entries MUST be in alphabetical order by repository name
- **Format**: Consistent markdown table format with repository links and descriptions

#### contributing.md
- Defines the contribution process
- Lists historical contributors
- Specifies alphabetical ordering requirement

## Content Categories

### Awesome Repositories Section
Primary security-focused awesome lists covering:
- Platform-specific security (Android, iOS, Windows, etc.)
- Security domains (AppSec, DevSecOps, OSINT, etc.)
- Attack techniques (Fuzzing, Exploit Development, Social Engineering)
- Specialized fields (IoT Security, Vehicle Security, Industrial Control Systems)

### Other Useful Repositories Section
Supporting resources including:
- Tools and frameworks (CyberChef, GTFOBins, DetectionLab)
- Learning resources (Hacker101, Infosec Reference)
- Collections (Payloads, SecLists, CVE PoCs)
- Cheatsheets and references

## Development Workflow

### Branch Strategy
- **Main branch**: Production-ready content
- **Feature branches**: For adding/updating content
  - Branch naming: Typically descriptive (e.g., `add-new-resource`, `update-links`)
  - PRs are merged into main after review

### Contribution Process

1. **Adding a new resource**:
   - Verify the resource is high-quality and actively maintained
   - Determine correct section (Awesome Repositories vs Other Useful Repositories)
   - Add entry maintaining alphabetical order
   - Follow exact table format
   - Submit pull request

2. **Format requirements**:
   ```markdown
   [Repository Name](GitHub URL) | Description without period at end
   ```

3. **Alphabetical ordering**:
   - Sort by repository name (left column)
   - Case-insensitive alphabetical order
   - Numbers come before letters

4. **Pull request guidelines**:
   - Clear title describing what's being added/changed
   - PRs should be focused (one addition/change preferred)
   - Community review before merge

### Quality Standards

#### Resource Inclusion Criteria
- **Activity**: Repository should be actively maintained (check recent commits)
- **Quality**: High-quality content with clear documentation
- **Relevance**: Directly related to hacking, pentesting, or security research
- **Uniqueness**: Not duplicate of existing entry
- **Scope**: Substantial collection/tool, not individual scripts

#### Description Guidelines
- Concise (typically 5-15 words)
- Clear about what the resource provides
- No marketing language or hype
- No period at the end
- Start with capital letter

## AI Assistant Guidelines

### When Adding New Entries

1. **Research first**:
   - Verify the resource exists and is accessible
   - Check repository activity (recent commits, issues, stars)
   - Ensure it's not already listed

2. **Determine correct section**:
   - "Awesome Repositories": If it's itself an awesome list
   - "Other Useful Repositories": If it's a tool, collection, or single-purpose resource

3. **Maintain alphabetical order**:
   - Read existing entries to find correct insertion point
   - Remember: Case-insensitive alphabetical sort
   - Use Edit tool to insert in the right location

4. **Format precisely**:
   ```markdown
   [Repository Name](https://github.com/user/repo) | Brief description
   ```

### When Updating Entries

1. **Verify changes are needed**:
   - Check if link is broken
   - Confirm new description is more accurate
   - Ensure repository hasn't been moved/renamed

2. **Maintain consistency**:
   - Keep same formatting style
   - Don't alter unrelated entries
   - Preserve alphabetical order

### When Removing Entries

1. **Valid reasons for removal**:
   - Repository deleted or no longer accessible
   - Repository archived with no maintenance
   - Resource is malicious or compromised
   - Duplicate entry

2. **Document in PR**:
   - Explain why removal is needed
   - Provide evidence (404 error, last commit date, etc.)

### Common Tasks

#### Task: Add a new awesome list

```markdown
Example: Adding "Awesome Kubernetes Security"

1. Verify: Check https://github.com/user/awesome-k8s-security exists and is active
2. Section: "Awesome Repositories" (it's an awesome list)
3. Find position: Between "InfoSec" and "IoT Hacks" alphabetically
4. Format: [Kubernetes Security](https://github.com/user/awesome-k8s-security) | List of Kubernetes security tools and resources
5. Edit README.md maintaining exact table format
6. Commit with clear message: "Add Awesome Kubernetes Security"
```

#### Task: Fix a broken link

```markdown
1. Verify link is broken (404 or redirect)
2. Research if repository moved or was renamed
3. Update URL if found, or remove if permanently gone
4. Commit: "Fix broken link for [Repository Name]" or "Remove defunct [Repository Name]"
```

#### Task: Update description for clarity

```markdown
1. Read current description
2. Verify repository to understand its actual purpose
3. Craft clearer, more accurate description
4. Maintain same brevity and style
5. Commit: "Update description for [Repository Name]"
```

## Git Workflow

### Commits
- **Style**: Imperative mood ("Add", "Update", "Fix", "Remove")
- **Examples**:
  - ✅ "Add Awesome Blockchain Security"
  - ✅ "Update description for Malware Analysis"
  - ✅ "Fix broken link for SecLists"
  - ✅ "Remove archived repository Foo"
  - ❌ "Added new repo"
  - ❌ "fixed stuff"

### Pull Requests
- **Title**: Descriptive, following commit message style
- **Description**:
  - What is being added/changed/removed
  - Why (if not obvious)
  - Link verification (for additions)

### Branch Naming
- Descriptive of change: `add-awesome-kubernetes-security`
- Or issue-based: `fix-broken-link-123`
- Current session uses: `claude/claude-md-mid1ur30uc7sts5t-01GVy8o3TzMwCCKUHpxxjnEw`

## Automation

### GitHub Actions

**lock-threads.yml**:
- Runs hourly (cron: '0 * * * *')
- Auto-locks issues and PRs after 7 days of inactivity
- Keeps repository clean and reduces noise

## Common Patterns

### Pattern: Repository Entry
```markdown
[Display Name](https://github.com/owner/repo) | Description text here
```

### Pattern: Table Structure
```markdown
Repository | Description
---- | ----
[Name 1](url1) | Description 1
[Name 2](url2) | Description 2
```

### Pattern: Alphabetical Insertion
When adding "Kubernetes Security" between "InfoSec" and "IoT Hacks":
```markdown
[InfoSec](url) | Description
[Kubernetes Security](url) | New description here
[IoT Hacks](url) | Description
```

## Validation Checklist

Before submitting changes, verify:

- [ ] All links are functional and point to correct repositories
- [ ] Entries are in strict alphabetical order within their section
- [ ] Table formatting is consistent (spacing, pipes, etc.)
- [ ] Descriptions are concise and clear
- [ ] No duplicate entries exist
- [ ] Repository being added is actively maintained
- [ ] Changes are in the correct section
- [ ] No periods at end of descriptions
- [ ] Links use HTTPS (not HTTP)
- [ ] No trailing whitespace

## Error Prevention

### Common Mistakes to Avoid

1. **Wrong section**: Don't add tools to "Awesome Repositories" section
2. **Broken alphabetical order**: Always verify sort order
3. **Inconsistent formatting**: Match existing table format exactly
4. **Verbose descriptions**: Keep descriptions brief and focused
5. **Dead links**: Always verify repository exists before adding
6. **Duplicate entries**: Search existing content first
7. **Marketing language**: Avoid "best", "amazing", "incredible"

### Quality Checks

Run these checks before committing:
1. Can you access every link you modified?
2. Is alphabetical order preserved?
3. Do table columns align properly?
4. Are descriptions objective and informative?
5. Is the resource actively maintained (commits in last 6-12 months)?

## Context for AI Assistants

### Repository Purpose
This is NOT:
- A code repository with build systems
- A project requiring tests or linting
- A repository with dependencies to manage
- A repository requiring code review for logic

This IS:
- A curated list of links (meta-repository)
- Maintained through careful curation
- Focused on organization and discoverability
- Quality-gated by community review

### Interaction Style

**When asked to add a resource**:
1. Validate the resource exists and is quality
2. Find correct section and alphabetical position
3. Make surgical edit maintaining all formatting
4. Commit with clear message

**When asked to update content**:
1. Locate exact entry
2. Make minimal necessary changes
3. Preserve surrounding context
4. Explain what was changed and why

**When asked to analyze**:
1. Can suggest resources that fit the repository's theme
2. Can identify broken links or outdated entries
3. Can reorganize if structure has become inconsistent
4. Can improve descriptions for clarity

### Best Practices for AI Assistants

1. **Always read before editing**: Use Read tool on README.md before any modifications
2. **Verify links**: Don't add resources without confirming they exist
3. **Respect alphabetical order**: This is critical for usability
4. **Match existing style**: Consistency is key in curated lists
5. **Be conservative**: Only add genuinely valuable resources
6. **Test links**: Verify URLs are accessible before adding
7. **Consider context**: Does this resource fit the repository's security focus?

## Maintenance Notes

### Regular Maintenance Tasks
- Check for broken links (repositories deleted, moved, or renamed)
- Verify repositories are still actively maintained
- Update descriptions if repository scope has changed
- Remove archived or abandoned projects
- Identify potential new resources from community

### Link Rot Prevention
- When adding, prefer repositories with:
  - Regular commit activity
  - Active issue/PR engagement
  - Clear documentation
  - Established community

## External References

- Main repository: https://github.com/Hack-with-Github/Awesome-Hacking
- Twitter: @HackwithGithub
- Facebook: HackwithGithub
- Related: Other "awesome" lists in the awesome-* namespace

## Summary for AI Assistants

**Key Takeaway**: This is a carefully curated index of security resources. Changes should be precise, well-researched, and maintain strict alphabetical ordering. Quality and organization are paramount. When in doubt, verify the resource quality and ask for clarification before making additions.

**Most Important Rules**:
1. Maintain alphabetical order (case-insensitive)
2. Verify all links before adding
3. Use consistent table formatting
4. Keep descriptions brief and objective
5. Choose correct section (Awesome Repositories vs Other Useful Repositories)
6. Only add actively maintained, high-quality resources

**Workflow Summary**:
1. Research → 2. Locate correct position → 3. Edit precisely → 4. Verify formatting → 5. Commit clearly

---

*Last Updated: 2025-11-24*
*Repository Structure: Simple (single main content file)*
*Maintenance Style: Community-driven curation*
