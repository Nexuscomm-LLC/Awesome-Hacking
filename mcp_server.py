#!/usr/bin/env python3
"""
Awesome-Hacking MCP Server

Exposes the Awesome-Hacking security knowledge base via the Model Context Protocol (MCP),
enabling AI assistants to search, filter, and explore 83+ curated security resources.

Features:
- 10 tools for searching, filtering, and discovering resources
- 5 resources for direct data access
- 3 prompts for guided exploration

Usage:
    python mcp_server.py                    # stdio transport (default)
    mcp dev mcp_server.py                   # MCP Inspector for testing

Configuration for Claude Desktop (claude_desktop_config.json):
    {
      "mcpServers": {
        "awesome-hacking": {
          "command": "python3",
          "args": ["/path/to/Awesome-Hacking/mcp_server.py"]
        }
      }
    }
"""

import contextlib
import io
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# Import the existing knowledge extractor
from hacking_knowledge import KnowledgeExtractor, Resource, SECURITY_DOMAINS

# Configure logging to stderr (CRITICAL for stdio MCP servers - never use stdout)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("awesome-hacking-mcp")

# Initialize FastMCP server
mcp = FastMCP(
    name="Awesome-Hacking",
    instructions="Security knowledge base with 83+ curated hacking and security resources. Use tools to search, filter, and discover resources by category, skill level, or domain.",
)

# Initialize the knowledge extractor at module level
# (parsed once at startup, reused across all tool/resource calls)
_extractor = KnowledgeExtractor()
logger.info("Knowledge base loaded: %d resources", len(_extractor.resources))


# =============================================================================
# Helper Functions
# =============================================================================

@contextlib.contextmanager
def _suppress_stdout():
    """Context manager to suppress stdout (safety for stdio MCP transport)."""
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = old_stdout


def _format_resource(resource: Resource) -> dict:
    """Format a Resource dataclass into a clean dictionary for JSON output."""
    return {
        "name": resource.name,
        "url": resource.url,
        "description": resource.description,
        "section": resource.section,
        "categories": resource.categories,
        "skill_level": resource.skill_level,
        "github_owner": resource.github_owner,
        "github_repo": resource.github_repo,
    }


# =============================================================================
# Tools (10 total)
# =============================================================================

@mcp.tool()
def search_resources(
    query: str,
    fuzzy: bool = True,
    limit: int = 10,
) -> str:
    """Search the Awesome-Hacking knowledge base for security resources.

    Performs full-text search across resource names and descriptions.
    Supports fuzzy matching when the fuzzywuzzy library is available.

    Args:
        query: Search terms (e.g., "malware analysis", "web security", "CTF")
        fuzzy: Enable fuzzy matching for approximate results (default: True)
        limit: Maximum number of results to return (default: 10)
    """
    results = _extractor.search(query, fuzzy=fuzzy)[:limit]
    if not results:
        return json.dumps({
            "message": f"No resources found for '{query}'",
            "results": []
        })
    return json.dumps({
        "query": query,
        "count": len(results),
        "results": [_format_resource(r) for r in results],
    }, indent=2)


@mcp.tool()
def list_by_category(
    category: str,
    limit: int = 20,
) -> str:
    """List security resources filtered by security domain category.

    Available categories: web, mobile, network, malware, forensics,
    exploitation, osint, red_team, blue_team, cryptography, cloud,
    iot, social, ctf, ai_ml, blockchain.

    Args:
        category: Security domain to filter by (e.g., "web", "red_team", "malware")
        limit: Maximum number of results to return (default: 20)
    """
    results = _extractor.filter_by_category(category)[:limit]
    if not results:
        available = ", ".join(SECURITY_DOMAINS.keys())
        return json.dumps({
            "message": f"No resources found in category '{category}'",
            "available_categories": available,
            "results": []
        })
    return json.dumps({
        "category": category,
        "count": len(results),
        "results": [_format_resource(r) for r in results],
    }, indent=2)


@mcp.tool()
def list_by_section(
    section: str,
    limit: int = 20,
) -> str:
    """List resources filtered by repository section.

    Args:
        section: Either "awesome" (curated awesome lists) or "other" (useful tools and collections)
        limit: Maximum number of results to return (default: 20)
    """
    results = _extractor.filter_by_section(section)[:limit]
    if not results:
        return json.dumps({
            "message": f"No resources found in section '{section}'",
            "hint": "Use 'awesome' or 'other' as section names",
            "results": []
        })
    return json.dumps({
        "section": section,
        "count": len(results),
        "results": [_format_resource(r) for r in results],
    }, indent=2)


@mcp.tool()
def list_by_skill_level(
    level: str,
    limit: int = 20,
) -> str:
    """List resources filtered by skill level.

    Args:
        level: One of "beginner", "intermediate", or "advanced"
        limit: Maximum number of results to return (default: 20)
    """
    results = _extractor.filter_by_skill_level(level)[:limit]
    if not results:
        return json.dumps({
            "message": f"No resources found for level '{level}'",
            "available_levels": ["beginner", "intermediate", "advanced"],
            "results": []
        })
    return json.dumps({
        "level": level,
        "count": len(results),
        "results": [_format_resource(r) for r in results],
    }, indent=2)


@mcp.tool()
def discover_random(
    count: int = 3,
    category: Optional[str] = None,
) -> str:
    """Discover random security resources for exploration and learning.

    Returns a random selection of resources, optionally filtered by category.
    Great for broadening security knowledge or finding new areas to explore.

    Args:
        count: Number of random resources to return (default: 3, max: 10)
        category: Optional category filter (e.g., "web", "malware")
    """
    count = min(count, 10)
    results = _extractor.get_random(count, category)
    return json.dumps({
        "count": len(results),
        "category": category,
        "results": [_format_resource(r) for r in results],
    }, indent=2)


@mcp.tool()
def get_statistics() -> str:
    """Get comprehensive statistics about the Awesome-Hacking knowledge base.

    Returns total resource counts, category distribution, skill level
    breakdown, section counts, and GitHub metadata statistics.
    """
    stats = _extractor.get_statistics()
    return json.dumps(stats, indent=2, default=str)


@mcp.tool()
def get_resource_detail(name: str) -> str:
    """Get detailed information about a specific security resource by name.

    Performs an exact name match first, then falls back to fuzzy search.

    Args:
        name: The resource name (e.g., "SecLists", "OSINT", "Malware Analysis")
    """
    # Exact match first
    for r in _extractor.resources:
        if r.name.lower() == name.lower():
            return json.dumps(_format_resource(r), indent=2)

    # Fallback to search
    results = _extractor.search(name, fuzzy=True)
    if results:
        return json.dumps({
            "note": f"No exact match for '{name}', showing closest match",
            "resource": _format_resource(results[0]),
        }, indent=2)

    return json.dumps({"error": f"Resource '{name}' not found"})


@mcp.tool()
def check_link(name: str) -> str:
    """Check if a specific resource's URL is still valid and accessible.

    Requires the 'requests' library to be installed.

    Args:
        name: The resource name to check (e.g., "SecLists")
    """
    resource = None
    for r in _extractor.resources:
        if r.name.lower() == name.lower():
            resource = r
            break

    if not resource:
        return json.dumps({"error": f"Resource '{name}' not found"})

    with _suppress_stdout():
        result = _extractor.check_link(resource)

    return json.dumps({
        "name": resource.name,
        "url": resource.url,
        "is_valid": result,
        "note": "requires 'requests' library" if result is None else None,
    }, indent=2)


@mcp.tool()
def build_learning_path(
    domain: str,
    include_related: bool = True,
) -> str:
    """Build a structured learning path for a security domain.

    Creates a progression from beginner to advanced resources within
    a security domain, optionally including related cross-domain resources.

    Args:
        domain: Security domain (e.g., "web", "malware", "red_team", "forensics")
        include_related: Include resources from related domains (default: True)
    """
    primary = _extractor.filter_by_category(domain)

    if not primary:
        available = ", ".join(SECURITY_DOMAINS.keys())
        return json.dumps({
            "error": f"No resources found in domain '{domain}'",
            "available_domains": available,
        })

    path = {
        "domain": domain,
        "total_resources": len(primary),
        "beginner": [],
        "intermediate": [],
        "advanced": [],
    }

    for r in primary:
        path[r.skill_level].append(_format_resource(r))

    if include_related:
        # Find resources that share categories with primary resources
        related_categories = set()
        for r in primary:
            related_categories.update(r.categories)
        related_categories.discard(domain)

        related = []
        seen_names = {r.name for r in primary}
        for cat in related_categories:
            for r in _extractor.filter_by_category(cat):
                if r.name not in seen_names:
                    related.append(_format_resource(r))
                    seen_names.add(r.name)
        path["related_domains"] = list(related_categories)
        path["related_resources"] = related[:10]

    return json.dumps(path, indent=2)


@mcp.tool()
def find_cross_domain(
    categories: list[str],
    require_all: bool = False,
) -> str:
    """Find resources that span multiple security domains.

    Useful for finding interdisciplinary resources that cover multiple
    areas of security.

    Args:
        categories: List of categories to match (e.g., ["web", "exploitation"])
        require_all: If True, resource must match ALL categories; if False, matches ANY (default: False)
    """
    results = []
    target_cats = set(c.lower() for c in categories)

    for r in _extractor.resources:
        resource_cats = set(r.categories)
        if require_all:
            if target_cats.issubset(resource_cats):
                results.append(r)
        else:
            if target_cats.intersection(resource_cats):
                results.append(r)

    return json.dumps({
        "categories": categories,
        "require_all": require_all,
        "count": len(results),
        "results": [_format_resource(r) for r in results],
    }, indent=2)


# =============================================================================
# Resources (5 total)
# =============================================================================

@mcp.resource("hacking://resources/all")
def get_all_resources() -> str:
    """Complete list of all curated security resources in the Awesome-Hacking knowledge base."""
    return json.dumps({
        "total": len(_extractor.resources),
        "resources": [_format_resource(r) for r in _extractor.resources],
    }, indent=2)


@mcp.resource("hacking://resources/category/{category}")
def get_category_resources(category: str) -> str:
    """Resources filtered by security domain category.

    Available categories: web, mobile, network, malware, forensics,
    exploitation, osint, red_team, blue_team, cryptography, cloud,
    iot, social, ctf, ai_ml, blockchain.
    """
    results = _extractor.filter_by_category(category)
    return json.dumps({
        "category": category,
        "count": len(results),
        "resources": [_format_resource(r) for r in results],
    }, indent=2)


@mcp.resource("hacking://statistics")
def get_stats_resource() -> str:
    """Statistics and analytics about the Awesome-Hacking knowledge base."""
    stats = _extractor.get_statistics()
    return json.dumps(stats, indent=2, default=str)


@mcp.resource("hacking://categories")
def get_categories_resource() -> str:
    """List of all security domain categories with their keyword definitions."""
    return json.dumps({
        "categories": list(SECURITY_DOMAINS.keys()),
        "category_keywords": {k: v for k, v in SECURITY_DOMAINS.items()},
    }, indent=2)


@mcp.resource("hacking://readme")
def get_readme() -> str:
    """The raw README.md content from the Awesome-Hacking repository."""
    readme_path = Path(__file__).parent / "README.md"
    return readme_path.read_text(encoding="utf-8")


# =============================================================================
# Prompts (3 total)
# =============================================================================

@mcp.prompt()
def security_learning_path(
    domain: str,
    experience: str = "beginner",
) -> str:
    """Generate a personalized security learning path.

    Args:
        domain: Security domain of interest (e.g., "web", "malware", "network")
        experience: Current experience level ("beginner", "intermediate", "advanced")
    """
    return f"""You are a cybersecurity education advisor. Using the Awesome-Hacking knowledge base,
create a structured learning path for someone interested in {domain} security
who is currently at the {experience} level.

Please:
1. Use the build_learning_path tool with domain="{domain}" to get available resources
2. Use get_statistics to understand the breadth of the knowledge base
3. Organize resources into a progressive curriculum:
   - Foundation: Start with beginner resources for core concepts
   - Core Skills: Intermediate resources for hands-on practice
   - Advanced Topics: Advanced resources for deep specialization
   - Cross-Domain: Related resources from adjacent security domains
4. For each resource, explain WHY it fits at that stage
5. Suggest a rough timeline and order of study
6. Highlight any prerequisite knowledge needed

Focus on practical, hands-on learning where possible."""


@mcp.prompt()
def resource_recommendation(
    interests: str,
    goal: str = "general learning",
) -> str:
    """Recommend security resources based on user interests and goals.

    Args:
        interests: Comma-separated security interests (e.g., "web hacking, bug bounty, API security")
        goal: What the user wants to achieve (e.g., "prepare for bug bounty", "career in pentesting")
    """
    return f"""You are a cybersecurity resource curator. Based on the user's interests and goals,
recommend the most relevant resources from the Awesome-Hacking knowledge base.

User interests: {interests}
User goal: {goal}

Please:
1. Search for resources matching each interest using search_resources
2. Use find_cross_domain to find resources spanning multiple interest areas
3. For each recommendation:
   - Explain what the resource contains
   - Why it is relevant to the user's goal
   - What skill level it targets
   - How it complements other recommended resources
4. Organize recommendations by priority (most relevant first)
5. Suggest a starting point and progression order
6. Note any gaps where the knowledge base might not have coverage"""


@mcp.prompt()
def domain_overview(domain: str) -> str:
    """Generate a comprehensive overview of a security domain.

    Args:
        domain: Security domain to explore (e.g., "web", "forensics", "cloud")
    """
    return f"""You are a cybersecurity domain expert. Provide a comprehensive overview of the
"{domain}" security domain using resources from the Awesome-Hacking knowledge base.

Please:
1. Use list_by_category with category="{domain}" to find all resources in this domain
2. Use get_statistics to understand how this domain compares to others
3. Use find_cross_domain to see how it connects to other security areas
4. Provide:
   - A brief introduction to the domain (2-3 sentences)
   - Key sub-topics and specializations within this domain
   - Overview of each resource in this domain with what it offers
   - How this domain connects to other security domains
   - Current trends and importance of this domain
   - Recommended starting resources for newcomers
5. Be factual and grounded in the actual resources available"""


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    logger.info("Starting Awesome-Hacking MCP Server")
    mcp.run(transport="stdio")
