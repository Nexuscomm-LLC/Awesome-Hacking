#!/usr/bin/env python3
"""
Awesome-Hacking Explorer - a browser GUI for the Awesome-Hacking knowledge base.

Serves gui/app.html on top of the existing KnowledgeExtractor, adding live link
checks, GitHub repository stats and exports. Uses only the standard library.

Views:
- Browse: search, domain / skill level / section filters, resource details
- Learning paths: resources in a domain grouped beginner -> advanced
- Domain matrix: how often each pair of security domains shares a resource
- Coverage: per-domain counts, skill level split and gaps

Usage:
    python gui_server.py                       # http://127.0.0.1:8765
    python gui_server.py --port 9000 --open    # pick a port and open a browser
    python gui_server.py --build explorer.html # standalone offline copy (no live checks)

Set GITHUB_TOKEN to raise the GitHub API rate limit for the stats lookup.
"""

import argparse
import json
import os
import sys
import tempfile
import threading
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

from hacking_knowledge import KnowledgeExtractor, SECURITY_DOMAINS

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "gui" / "app.html"
USER_AGENT = "awesome-hacking-explorer/1.0"
RESOURCE_FIELDS = (
    "name", "url", "description", "section", "categories",
    "skill_level", "github_owner", "github_repo",
)
EXPORTS = {
    "json": ("application/json", "hacking_resources.json"),
    "csv": ("text/csv", "hacking_resources.csv"),
    "markdown": ("text/markdown", "hacking_resources_categorized.md"),
}


# =============================================================================
# Page building
# =============================================================================

def build_payload(extractor: KnowledgeExtractor) -> dict:
    """Data embedded into the page: every resource plus the domain taxonomy."""
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "domains": list(SECURITY_DOMAINS.keys()),
        "resources": [
            {field: getattr(r, field) for field in RESOURCE_FIELDS}
            for r in extractor.resources
        ],
    }


def render_page(payload: dict, fragment: bool = False) -> str:
    """Inject the payload into the template; wrap it in a document unless fragment=True."""
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    body = TEMPLATE.read_text(encoding="utf-8").replace("__KB_DATA__", data)
    if fragment:
        return body
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        "</head>\n<body>\n" + body + "\n</body>\n</html>\n"
    )


# =============================================================================
# Live lookups
# =============================================================================

def check_url(url: str, timeout: int = 10) -> dict:
    """HEAD the URL (falling back to GET when HEAD is refused) and report the result."""
    for method in ("HEAD", "GET"):
        try:
            req = Request(url, method=method, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=timeout) as resp:
                return {"ok": resp.status < 400, "status": resp.status, "final_url": resp.geturl()}
        except HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue
            return {"ok": False, "status": e.code, "error": str(e.reason)}
        except (URLError, TimeoutError, OSError) as e:
            return {"ok": False, "status": None, "error": str(getattr(e, "reason", e))}
    return {"ok": False, "status": None, "error": "No response"}


def github_metadata(owner: str, repo: str, timeout: int = 10) -> dict:
    """Fetch repository stats from the GitHub REST API."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
    with urlopen(req, timeout=timeout) as resp:
        data = json.load(resp)
    return {
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "open_issues": data.get("open_issues_count"),
        "pushed_at": data.get("pushed_at"),
        "archived": data.get("archived", False),
        "license": (data.get("license") or {}).get("spdx_id"),
        "default_branch": data.get("default_branch"),
    }


# =============================================================================
# HTTP server
# =============================================================================

class ExplorerServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, extractor: KnowledgeExtractor):
        super().__init__(address, ExplorerHandler)
        self.extractor = extractor
        self.payload = build_payload(extractor)
        self.by_name = {r.name.lower(): r for r in extractor.resources}
        self._github_cache = {}
        self._lock = threading.Lock()

    def page(self) -> bytes:
        # Re-read the template on each request so edits show up on refresh
        return render_page(self.payload).encode("utf-8")

    def github(self, resource) -> dict:
        key = f"{resource.github_owner}/{resource.github_repo}".lower()
        with self._lock:
            if key in self._github_cache:
                return self._github_cache[key]
        result = github_metadata(resource.github_owner, resource.github_repo)
        with self._lock:
            self._github_cache[key] = result
        return result

    def export(self, fmt: str) -> bytes:
        if fmt == "json":
            return self.extractor.export_json().encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / EXPORTS[fmt][1]
            if fmt == "csv":
                self.extractor.export_csv(str(path))
            else:
                self.extractor.export_markdown(str(path))
            return path.read_bytes()


class ExplorerHandler(BaseHTTPRequestHandler):
    server_version = "AwesomeHackingExplorer/1.0"

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            return self._send(200, self.server.page(), "text/html; charset=utf-8")
        if path == "/api/health":
            return self._json({"ok": True, "resources": len(self.server.extractor.resources)})
        if path == "/api/resources":
            return self._json(self.server.payload)

        if path in ("/api/check", "/api/github"):
            name = query.get("name", [""])[0]
            # Only names from the README resolve, so lookups never reach arbitrary URLs
            resource = self.server.by_name.get(name.lower())
            if not resource:
                return self._json({"error": f"No resource named '{name}'."}, 404)
            if path == "/api/check":
                return self._json(check_url(resource.url))
            if not resource.is_github:
                return self._json({"error": f"{resource.name} is not hosted on GitHub."}, 400)
            try:
                return self._json(self.server.github(resource))
            except HTTPError as e:
                hint = " Set GITHUB_TOKEN to raise the rate limit." if e.code in (403, 429) else ""
                return self._json({"error": f"GitHub answered HTTP {e.code}.{hint}"}, 502)
            except (URLError, TimeoutError, OSError) as e:
                return self._json({"error": f"Could not reach GitHub: {getattr(e, 'reason', e)}"}, 502)

        if path == "/api/export":
            fmt = query.get("format", ["json"])[0]
            if fmt not in EXPORTS:
                return self._json({"error": f"Unknown format '{fmt}'. Use json, csv or markdown."}, 400)
            content_type, filename = EXPORTS[fmt]
            return self._send(
                200, self.server.export(fmt), f"{content_type}; charset=utf-8",
                {"Content-Disposition": f'attachment; filename="{filename}"'},
            )

        return self._json({"error": "Not found"}, 404)

    def _json(self, data, status: int = 200):
        self._send(status, json.dumps(data, indent=2).encode("utf-8"), "application/json; charset=utf-8")

    def _send(self, status: int, body: bytes, content_type: str, headers: dict = None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)


# =============================================================================
# Entry point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Awesome-Hacking Explorer - browser GUI for the knowledge base",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Address to bind (default: 127.0.0.1)")
    parser.add_argument("--port", "-p", type=int, default=8765, help="Port to listen on (default: 8765)")
    parser.add_argument("--open", action="store_true", help="Open the GUI in a web browser")
    parser.add_argument("--build", metavar="PATH", help="Write a standalone HTML file instead of serving")
    parser.add_argument("--fragment", action="store_true", help="With --build, omit the <html>/<head> wrapper")
    args = parser.parse_args()

    try:
        extractor = KnowledgeExtractor()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.build:
        out = Path(args.build)
        out.write_text(render_page(build_payload(extractor), fragment=args.fragment), encoding="utf-8")
        print(f"Wrote {out} ({len(extractor.resources)} resources)")
        return

    server = ExplorerServer((args.host, args.port), extractor)
    url = f"http://{args.host}:{args.port}/"
    print(f"Awesome-Hacking Explorer: {url}  ({len(extractor.resources)} resources, Ctrl+C to stop)")
    if args.open:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
