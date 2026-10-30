#!/usr/bin/env python3
"""
Hacking Knowledge Extractor - A powerful tool to extract, search, and operationalize
security resources from the Awesome-Hacking repository.

Features:
- Parse and extract all curated security resources
- Smart categorization by security domain
- Full-text search with fuzzy matching
- Link health validation
- Export to JSON, CSV, HTML, Markdown
- GitHub API integration for live metadata (stars, forks, activity)
- Random resource discovery for learning
- Interactive browsing mode
- Statistics and analytics

Usage:
    python hacking_knowledge.py --help
    python hacking_knowledge.py search "malware"
    python hacking_knowledge.py list --category web
    python hacking_knowledge.py check-links
    python hacking_knowledge.py export --format json
    python hacking_knowledge.py stats
    python hacking_knowledge.py discover
    python hacking_knowledge.py interactive
"""

import argparse
import csv
import json
import os
import random
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# Optional imports for enhanced features
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from fuzzywuzzy import fuzz
    HAS_FUZZY = True
except ImportError:
    HAS_FUZZY = False


# Security domain categories for smart classification
SECURITY_DOMAINS = {
    "web": ["web", "appsec", "xss", "sql", "injection", "owasp", "api", "http", "php", "csrf"],
    "mobile": ["android", "ios", "mobile", "apk", "ipa"],
    "network": ["network", "wifi", "wireless", "802.11", "packet", "pcap", "voip", "rtc"],
    "malware": ["malware", "virus", "trojan", "ransomware", "reverse", "binary"],
    "forensics": ["forensic", "incident", "response", "ioc", "threat", "apt", "dfir"],
    "exploitation": ["exploit", "vulnerability", "cve", "poc", "fuzzing", "buffer", "overflow"],
    "osint": ["osint", "recon", "asset", "discovery", "intelligence"],
    "red_team": ["red team", "pentest", "penetration", "offensive", "attack"],
    "blue_team": ["blue team", "defensive", "detection", "siem", "hunting", "yara"],
    "cryptography": ["crypto", "encrypt", "cipher", "hash", "ssl", "tls"],
    "cloud": ["cloud", "aws", "azure", "gcp", "kubernetes", "k8s", "serverless", "container"],
    "iot": ["iot", "embedded", "hardware", "firmware", "scada", "ics", "vehicle", "automotive"],
    "social": ["social", "phishing", "human", "awareness"],
    "ctf": ["ctf", "capture", "flag", "wargame", "challenge"],
    "ai_ml": ["machine learning", "ml", "ai", "adversarial", "neural"],
    "blockchain": ["web3", "blockchain", "smart contract", "solidity", "defi"],
}

# Skill level indicators
SKILL_LEVELS = {
    "beginner": ["getting started", "introduction", "basics", "101", "beginner", "learning", "tutorial"],
    "intermediate": ["tools", "techniques", "resources", "collection", "list"],
    "advanced": ["advanced", "exploitation", "research", "development", "kernel"],
}


@dataclass
class Resource:
    """Represents a single security resource."""
    name: str
    url: str
    description: str
    section: str
    categories: list = field(default_factory=list)
    skill_level: str = "intermediate"
    github_owner: Optional[str] = None
    github_repo: Optional[str] = None
    stars: Optional[int] = None
    forks: Optional[int] = None
    last_updated: Optional[str] = None
    is_valid: Optional[bool] = None

    def __post_init__(self):
        # Extract GitHub info from URL
        if "github.com" in self.url:
            match = re.search(r"github\.com/([^/]+)/([^/\s\)]+)", self.url)
            if match:
                self.github_owner = match.group(1)
                self.github_repo = match.group(2).rstrip("/")

        # Auto-categorize
        if not self.categories:
            self.categories = self._detect_categories()

        # Detect skill level
        self.skill_level = self._detect_skill_level()

    def _detect_categories(self) -> list:
        """Auto-detect categories based on name and description."""
        categories = set()
        text = f"{self.name} {self.description}".lower()

        for category, keywords in SECURITY_DOMAINS.items():
            for keyword in keywords:
                if keyword in text:
                    categories.add(category)
                    break

        return list(categories) if categories else ["general"]

    def _detect_skill_level(self) -> str:
        """Detect skill level based on description."""
        text = f"{self.name} {self.description}".lower()

        for level, keywords in SKILL_LEVELS.items():
            for keyword in keywords:
                if keyword in text:
                    return level

        return "intermediate"

    @property
    def is_github(self) -> bool:
        return self.github_owner is not None and self.github_repo is not None

    def to_dict(self) -> dict:
        return asdict(self)


class KnowledgeExtractor:
    """Main class for extracting and managing security knowledge."""

    def __init__(self, readme_path: str = None):
        self.readme_path = readme_path or self._find_readme()
        self.resources: list[Resource] = []
        self._parse_readme()

    def _find_readme(self) -> str:
        """Find README.md in current or parent directories."""
        current = Path(__file__).parent
        for path in [current, current.parent]:
            readme = path / "README.md"
            if readme.exists():
                return str(readme)
        raise FileNotFoundError("README.md not found")

    def _parse_readme(self):
        """Parse README.md and extract all resources."""
        with open(self.readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split into sections
        sections = {
            "Awesome Repositories": [],
            "Other Useful Repositories": []
        }

        current_section = None
        in_table = False

        for line in content.split("\n"):
            # Detect section headers
            if "## Awesome Repositories" in line:
                current_section = "Awesome Repositories"
                continue
            elif "## Other Useful Repositories" in line:
                current_section = "Other Useful Repositories"
                continue
            elif line.startswith("## ") and current_section:
                current_section = None
                continue

            # Skip table headers
            if "Repository | Description" in line or "---- | ----" in line:
                in_table = True
                continue

            # Parse table rows
            if current_section and in_table and "|" in line:
                match = re.match(r"\[([^\]]+)\]\(([^)]+)\)\s*\|\s*(.+)", line.strip())
                if match:
                    name, url, description = match.groups()
                    resource = Resource(
                        name=name.strip(),
                        url=url.strip(),
                        description=description.strip(),
                        section=current_section
                    )
                    self.resources.append(resource)

    def search(self, query: str, fuzzy: bool = True, min_score: int = 60) -> list[Resource]:
        """Search resources by query string."""
        query = query.lower()
        results = []

        for resource in self.resources:
            text = f"{resource.name} {resource.description}".lower()

            # Exact match
            if query in text:
                results.append((resource, 100))
                continue

            # Fuzzy match
            if fuzzy and HAS_FUZZY:
                score = max(
                    fuzz.partial_ratio(query, resource.name.lower()),
                    fuzz.partial_ratio(query, resource.description.lower())
                )
                if score >= min_score:
                    results.append((resource, score))

        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results]

    def filter_by_category(self, category: str) -> list[Resource]:
        """Filter resources by security domain category."""
        category = category.lower()
        return [r for r in self.resources if category in r.categories]

    def filter_by_section(self, section: str) -> list[Resource]:
        """Filter resources by section (awesome/other)."""
        section = section.lower()
        return [r for r in self.resources if section in r.section.lower()]

    def filter_by_skill_level(self, level: str) -> list[Resource]:
        """Filter resources by skill level."""
        return [r for r in self.resources if r.skill_level == level.lower()]

    def get_random(self, count: int = 1, category: str = None) -> list[Resource]:
        """Get random resources for discovery."""
        pool = self.filter_by_category(category) if category else self.resources
        return random.sample(pool, min(count, len(pool)))

    def check_link(self, resource: Resource, timeout: int = 10) -> bool:
        """Check if a resource link is valid."""
        if not HAS_REQUESTS:
            print("Warning: requests library not installed. Install with: pip install requests")
            return None

        try:
            response = requests.head(resource.url, timeout=timeout, allow_redirects=True)
            resource.is_valid = response.status_code < 400
            return resource.is_valid
        except Exception:
            resource.is_valid = False
            return False

    def check_all_links(self, timeout: int = 10) -> dict:
        """Check all links and return results."""
        if not HAS_REQUESTS:
            return {"error": "requests library not installed"}

        results = {"valid": [], "invalid": [], "errors": []}
        total = len(self.resources)

        for i, resource in enumerate(self.resources, 1):
            print(f"\rChecking links: {i}/{total}", end="", flush=True)
            try:
                if self.check_link(resource, timeout):
                    results["valid"].append(resource.name)
                else:
                    results["invalid"].append({"name": resource.name, "url": resource.url})
            except Exception as e:
                results["errors"].append({"name": resource.name, "error": str(e)})

        print()  # New line after progress
        return results

    def fetch_github_metadata(self, resource: Resource) -> bool:
        """Fetch GitHub metadata for a resource."""
        if not HAS_REQUESTS or not resource.is_github:
            return False

        try:
            api_url = f"https://api.github.com/repos/{resource.github_owner}/{resource.github_repo}"
            response = requests.get(api_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                resource.stars = data.get("stargazers_count")
                resource.forks = data.get("forks_count")
                resource.last_updated = data.get("pushed_at")
                return True
        except Exception:
            pass

        return False

    def get_statistics(self) -> dict:
        """Generate statistics about the knowledge base."""
        stats = {
            "total_resources": len(self.resources),
            "sections": defaultdict(int),
            "categories": defaultdict(int),
            "skill_levels": defaultdict(int),
            "github_resources": 0,
            "non_github_resources": 0,
            "unique_github_owners": set(),
        }

        for resource in self.resources:
            stats["sections"][resource.section] += 1
            stats["skill_levels"][resource.skill_level] += 1

            for category in resource.categories:
                stats["categories"][category] += 1

            if resource.is_github:
                stats["github_resources"] += 1
                stats["unique_github_owners"].add(resource.github_owner)
            else:
                stats["non_github_resources"] += 1

        stats["unique_github_owners"] = len(stats["unique_github_owners"])
        stats["sections"] = dict(stats["sections"])
        stats["categories"] = dict(sorted(stats["categories"].items(), key=lambda x: x[1], reverse=True))
        stats["skill_levels"] = dict(stats["skill_levels"])

        return stats

    def export_json(self, filepath: str = None) -> str:
        """Export resources to JSON."""
        data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_resources": len(self.resources),
                "source": "Awesome-Hacking Repository"
            },
            "resources": [r.to_dict() for r in self.resources]
        }

        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return filepath

        return json.dumps(data, indent=2, ensure_ascii=False)

    def export_csv(self, filepath: str = None) -> str:
        """Export resources to CSV."""
        if not filepath:
            filepath = "hacking_resources.csv"

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "URL", "Description", "Section", "Categories", "Skill Level"])

            for r in self.resources:
                writer.writerow([
                    r.name,
                    r.url,
                    r.description,
                    r.section,
                    ", ".join(r.categories),
                    r.skill_level
                ])

        return filepath

    def export_html(self, filepath: str = None) -> str:
        """Export resources to interactive HTML."""
        if not filepath:
            filepath = "hacking_resources.html"

        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hacking Knowledge Base</title>
    <style>
        :root {
            --bg: #0d1117;
            --card-bg: #161b22;
            --border: #30363d;
            --text: #c9d1d9;
            --text-secondary: #8b949e;
            --accent: #58a6ff;
            --success: #3fb950;
            --warning: #d29922;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: var(--accent); margin-bottom: 1rem; }
        .stats { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 2rem; }
        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem 1.5rem;
            min-width: 150px;
        }
        .stat-value { font-size: 2rem; font-weight: bold; color: var(--accent); }
        .stat-label { color: var(--text-secondary); font-size: 0.9rem; }
        .filters {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-bottom: 2rem;
        }
        input, select {
            background: var(--card-bg);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 0.75rem 1rem;
            border-radius: 6px;
            font-size: 1rem;
        }
        input:focus, select:focus { outline: none; border-color: var(--accent); }
        #search { flex: 1; min-width: 300px; }
        .resources { display: grid; gap: 1rem; }
        .resource {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.25rem;
            transition: border-color 0.2s;
        }
        .resource:hover { border-color: var(--accent); }
        .resource-header { display: flex; justify-content: space-between; align-items: start; }
        .resource-name { color: var(--accent); font-weight: 600; font-size: 1.1rem; text-decoration: none; }
        .resource-name:hover { text-decoration: underline; }
        .resource-section {
            font-size: 0.75rem;
            background: var(--border);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            color: var(--text-secondary);
        }
        .resource-desc { margin: 0.75rem 0; color: var(--text-secondary); }
        .tags { display: flex; gap: 0.5rem; flex-wrap: wrap; }
        .tag {
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            background: #1f6feb22;
            color: var(--accent);
            border: 1px solid #1f6feb44;
        }
        .skill-tag { background: #3fb95022; color: var(--success); border-color: #3fb95044; }
        .hidden { display: none; }
        .count { color: var(--text-secondary); margin-bottom: 1rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Hacking Knowledge Base</h1>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="total-count">0</div>
                <div class="stat-label">Total Resources</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="category-count">0</div>
                <div class="stat-label">Categories</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="visible-count">0</div>
                <div class="stat-label">Showing</div>
            </div>
        </div>
        <div class="filters">
            <input type="text" id="search" placeholder="Search resources...">
            <select id="category-filter">
                <option value="">All Categories</option>
            </select>
            <select id="section-filter">
                <option value="">All Sections</option>
                <option value="Awesome Repositories">Awesome Repositories</option>
                <option value="Other Useful Repositories">Other Useful Repositories</option>
            </select>
            <select id="skill-filter">
                <option value="">All Skill Levels</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
            </select>
        </div>
        <div class="count"><span id="showing">0</span> resources</div>
        <div class="resources" id="resources"></div>
    </div>
    <script>
        const resources = RESOURCES_DATA;
        const categories = [...new Set(resources.flatMap(r => r.categories))].sort();

        document.getElementById('total-count').textContent = resources.length;
        document.getElementById('category-count').textContent = categories.length;

        const categoryFilter = document.getElementById('category-filter');
        categories.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat;
            opt.textContent = cat.charAt(0).toUpperCase() + cat.slice(1).replace('_', ' ');
            categoryFilter.appendChild(opt);
        });

        function renderResources(filtered) {
            const container = document.getElementById('resources');
            document.getElementById('visible-count').textContent = filtered.length;
            document.getElementById('showing').textContent = filtered.length;

            container.innerHTML = filtered.map(r => `
                <div class="resource">
                    <div class="resource-header">
                        <a href="${r.url}" target="_blank" class="resource-name">${r.name}</a>
                        <span class="resource-section">${r.section.includes('Awesome') ? 'Awesome' : 'Useful'}</span>
                    </div>
                    <p class="resource-desc">${r.description}</p>
                    <div class="tags">
                        ${r.categories.map(c => `<span class="tag">${c}</span>`).join('')}
                        <span class="tag skill-tag">${r.skill_level}</span>
                    </div>
                </div>
            `).join('');
        }

        function filterResources() {
            const search = document.getElementById('search').value.toLowerCase();
            const category = document.getElementById('category-filter').value;
            const section = document.getElementById('section-filter').value;
            const skill = document.getElementById('skill-filter').value;

            const filtered = resources.filter(r => {
                const matchSearch = !search ||
                    r.name.toLowerCase().includes(search) ||
                    r.description.toLowerCase().includes(search);
                const matchCategory = !category || r.categories.includes(category);
                const matchSection = !section || r.section === section;
                const matchSkill = !skill || r.skill_level === skill;
                return matchSearch && matchCategory && matchSection && matchSkill;
            });

            renderResources(filtered);
        }

        document.getElementById('search').addEventListener('input', filterResources);
        document.getElementById('category-filter').addEventListener('change', filterResources);
        document.getElementById('section-filter').addEventListener('change', filterResources);
        document.getElementById('skill-filter').addEventListener('change', filterResources);

        renderResources(resources);
    </script>
</body>
</html>"""

        # Inject resources data
        resources_json = json.dumps([r.to_dict() for r in self.resources])
        html = html.replace("RESOURCES_DATA", resources_json)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        return filepath

    def export_markdown(self, filepath: str = None) -> str:
        """Export resources to enhanced Markdown with categories."""
        if not filepath:
            filepath = "hacking_resources_categorized.md"

        lines = ["# Hacking Knowledge Base - Categorized", ""]
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        lines.append(f"*Total Resources: {len(self.resources)}*")
        lines.append("")

        # Group by category
        categorized = defaultdict(list)
        for r in self.resources:
            for cat in r.categories:
                categorized[cat].append(r)

        # Table of contents
        lines.append("## Table of Contents")
        for cat in sorted(categorized.keys()):
            display_name = cat.replace("_", " ").title()
            lines.append(f"- [{display_name}](#{cat}) ({len(categorized[cat])})")
        lines.append("")

        # Each category
        for cat in sorted(categorized.keys()):
            display_name = cat.replace("_", " ").title()
            lines.append(f"## {display_name} {{{cat}}}")
            lines.append("")
            lines.append("| Resource | Description | Level |")
            lines.append("|----------|-------------|-------|")

            for r in sorted(categorized[cat], key=lambda x: x.name.lower()):
                level_emoji = {"beginner": "Beginner", "intermediate": "Intermediate", "advanced": "Advanced"}.get(r.skill_level, "Intermediate")
                lines.append(f"| [{r.name}]({r.url}) | {r.description} | {level_emoji} |")

            lines.append("")

        content = "\n".join(lines)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath


def print_resource(resource: Resource, verbose: bool = False):
    """Pretty print a resource."""
    print(f"\n  {resource.name}")
    print(f"  {resource.url}")
    print(f"  {resource.description}")
    print(f"  Categories: {', '.join(resource.categories)} | Level: {resource.skill_level}")

    if verbose and resource.stars is not None:
        print(f"  Stars: {resource.stars} | Forks: {resource.forks}")


def interactive_mode(extractor: KnowledgeExtractor):
    """Run interactive browsing mode."""
    print("\n  Hacking Knowledge Base - Interactive Mode")
    print("  " + "=" * 45)
    print("  Commands: search <query> | category <name> | random | stats | quit")
    print()

    while True:
        try:
            cmd = input("  > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n  Goodbye!")
            break

        if not cmd:
            continue

        parts = cmd.split(maxsplit=1)
        action = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if action in ("quit", "exit", "q"):
            print("  Goodbye!")
            break
        elif action == "search":
            if not arg:
                print("  Usage: search <query>")
                continue
            results = extractor.search(arg)
            print(f"\n  Found {len(results)} results for '{arg}':")
            for r in results[:10]:
                print_resource(r)
        elif action in ("category", "cat"):
            if not arg:
                stats = extractor.get_statistics()
                print("\n  Available categories:")
                for cat, count in stats["categories"].items():
                    print(f"    {cat}: {count}")
                continue
            results = extractor.filter_by_category(arg)
            print(f"\n  Found {len(results)} resources in '{arg}':")
            for r in results[:10]:
                print_resource(r)
        elif action == "random":
            count = int(arg) if arg.isdigit() else 3
            results = extractor.get_random(count)
            print(f"\n  Random {len(results)} resources:")
            for r in results:
                print_resource(r)
        elif action == "stats":
            stats = extractor.get_statistics()
            print(f"\n  Total Resources: {stats['total_resources']}")
            print(f"  GitHub Resources: {stats['github_resources']}")
            print(f"  Unique Owners: {stats['unique_github_owners']}")
            print("\n  Top Categories:")
            for cat, count in list(stats["categories"].items())[:5]:
                print(f"    {cat}: {count}")
        else:
            print(f"  Unknown command: {action}")


def main():
    parser = argparse.ArgumentParser(
        description="Hacking Knowledge Extractor - Extract and operationalize security resources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search "malware analysis"     Search for malware analysis resources
  %(prog)s list --category web           List all web security resources
  %(prog)s list --level beginner         List beginner-friendly resources
  %(prog)s discover                      Get random resources for learning
  %(prog)s discover --count 5            Get 5 random resources
  %(prog)s stats                         Show statistics about the knowledge base
  %(prog)s check-links                   Validate all resource links
  %(prog)s export --format json          Export to JSON
  %(prog)s export --format html          Generate interactive HTML page
  %(prog)s interactive                   Start interactive browsing mode
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search resources")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--no-fuzzy", action="store_true", help="Disable fuzzy matching")

    # List command
    list_parser = subparsers.add_parser("list", help="List resources with filters")
    list_parser.add_argument("--category", "-c", help="Filter by category")
    list_parser.add_argument("--section", "-s", help="Filter by section (awesome/other)")
    list_parser.add_argument("--level", "-l", choices=["beginner", "intermediate", "advanced"])
    list_parser.add_argument("--limit", "-n", type=int, default=20, help="Limit results")

    # Discover command
    discover_parser = subparsers.add_parser("discover", help="Random resource discovery")
    discover_parser.add_argument("--count", "-n", type=int, default=3, help="Number of resources")
    discover_parser.add_argument("--category", "-c", help="Filter by category")

    # Stats command
    subparsers.add_parser("stats", help="Show statistics")

    # Check links command
    check_parser = subparsers.add_parser("check-links", help="Validate resource links")
    check_parser.add_argument("--timeout", "-t", type=int, default=10, help="Request timeout")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export resources")
    export_parser.add_argument("--format", "-f", choices=["json", "csv", "html", "markdown"], default="json")
    export_parser.add_argument("--output", "-o", help="Output file path")

    # Interactive command
    subparsers.add_parser("interactive", help="Interactive browsing mode")

    # Categories command
    subparsers.add_parser("categories", help="List all categories")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize extractor
    try:
        extractor = KnowledgeExtractor()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Execute command
    if args.command == "search":
        results = extractor.search(args.query, fuzzy=not args.no_fuzzy)
        print(f"\nFound {len(results)} results for '{args.query}':\n")
        for r in results:
            print_resource(r)

    elif args.command == "list":
        results = extractor.resources

        if args.category:
            results = [r for r in results if args.category.lower() in r.categories]
        if args.section:
            results = [r for r in results if args.section.lower() in r.section.lower()]
        if args.level:
            results = [r for r in results if r.skill_level == args.level]

        print(f"\nShowing {min(len(results), args.limit)} of {len(results)} resources:\n")
        for r in results[:args.limit]:
            print_resource(r)

    elif args.command == "discover":
        results = extractor.get_random(args.count, args.category)
        print(f"\nDiscover {len(results)} security resources:\n")
        for r in results:
            print_resource(r)

    elif args.command == "stats":
        stats = extractor.get_statistics()
        print("\n  Hacking Knowledge Base Statistics")
        print("  " + "=" * 40)
        print(f"  Total Resources:     {stats['total_resources']}")
        print(f"  GitHub Resources:    {stats['github_resources']}")
        print(f"  Non-GitHub:          {stats['non_github_resources']}")
        print(f"  Unique Owners:       {stats['unique_github_owners']}")
        print()
        print("  By Section:")
        for section, count in stats["sections"].items():
            print(f"    {section}: {count}")
        print()
        print("  By Skill Level:")
        for level, count in stats["skill_levels"].items():
            print(f"    {level.capitalize()}: {count}")
        print()
        print("  Top Categories:")
        for cat, count in list(stats["categories"].items())[:10]:
            display = cat.replace("_", " ").title()
            print(f"    {display}: {count}")

    elif args.command == "check-links":
        if not HAS_REQUESTS:
            print("Error: requests library required. Install with: pip install requests")
            sys.exit(1)
        print("\nChecking all resource links...")
        results = extractor.check_all_links(args.timeout)
        print(f"\nValid links:   {len(results['valid'])}")
        print(f"Invalid links: {len(results['invalid'])}")
        print(f"Errors:        {len(results['errors'])}")
        if results["invalid"]:
            print("\nInvalid links:")
            for item in results["invalid"]:
                print(f"  - {item['name']}: {item['url']}")

    elif args.command == "export":
        output = args.output

        if args.format == "json":
            filepath = extractor.export_json(output or "hacking_resources.json")
        elif args.format == "csv":
            filepath = extractor.export_csv(output or "hacking_resources.csv")
        elif args.format == "html":
            filepath = extractor.export_html(output or "hacking_resources.html")
        elif args.format == "markdown":
            filepath = extractor.export_markdown(output or "hacking_resources_categorized.md")

        print(f"\nExported to: {filepath}")

    elif args.command == "interactive":
        interactive_mode(extractor)

    elif args.command == "categories":
        stats = extractor.get_statistics()
        print("\n  Available Categories:")
        print("  " + "=" * 30)
        for cat, count in stats["categories"].items():
            display = cat.replace("_", " ").title()
            print(f"  {display:20} {count:3} resources")


if __name__ == "__main__":
    main()
