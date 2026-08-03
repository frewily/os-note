#!/usr/bin/env python3
"""
Sync Obsidian notes marked `publish: true` to a WordPress blog via the REST API.

Design overview:
  - Scans the whole vault every run (idempotent, self-healing). Unchanged notes are
    skipped by comparing a content md5 stored in .blog-sync-state.json.
  - A note is published only when its YAML frontmatter contains `publish: true`.
  - Wiki-links [[Target]] become links to the published target post (plain text when
    the target is not published).
  - Local images referenced from notes are uploaded to the WordPress media library.
  - Two rendering passes: Pass 1 creates/updates posts; Pass 2 re-renders every
    published note with the now-complete link map so cross-links converge.

Usage:
  python3 scripts/blog_sync.py --vault . --base-url URL --user USER --password PASS
  python3 scripts/blog_sync.py --vault . --dry-run        # plan only, no network
  python3 scripts/blog_sync.py --vault . --check-auth     # verify credentials
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import sys
import time
import urllib.parse
from datetime import date
from typing import Any, Callable, Optional

import frontmatter  # python-frontmatter
import markdown as markdown_lib  # markdown
import requests

STATE_FILE = ".blog-sync-state.json"
SKIP_DIRS = {".git", ".obsidian", ".claude", ".claudian", ".trae", "node_modules"}
MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
OBS_EMBED_RE = re.compile(r"!\[\[([^\[\]]+)\]\]")
WIKILINK_RE = re.compile(r"\[\[([^\[\]]+)\]\]")


class BlogSyncError(Exception):
    """Fatal or per-note error."""


def log(msg: str) -> None:
    print(msg, flush=True)


def warn(msg: str) -> None:
    print(f"WARN: {msg}", flush=True)


# ---------------------------------------------------------------------------
# CLI / state
# ---------------------------------------------------------------------------

def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Publish Obsidian notes to WordPress.")
    p.add_argument("--vault", default=".", help="Path to the Obsidian vault (repo root).")
    p.add_argument("--base-url", default=os.environ.get("WP_BASE_URL", ""),
                   help="Blog base URL, e.g. http://freblog.frewily.top")
    p.add_argument("--user", default=os.environ.get("WP_USER", ""))
    p.add_argument("--password", default=os.environ.get("WP_APP_PASSWORD", ""))
    p.add_argument("--dry-run", action="store_true", help="Print the plan, no network calls.")
    p.add_argument("--check-auth", action="store_true", help="Verify REST API auth and exit.")
    p.add_argument("--verbose", action="store_true", help="Print rendered HTML previews.")
    return p.parse_args(argv)


def load_state(path: str) -> dict:
    if not os.path.exists(path):
        return {"version": 1, "notes": {}, "tags": {}, "cats": {}, "media": {}}
    try:
        with open(path, encoding="utf-8") as fh:
            st = json.load(fh)
        st.setdefault("notes", {})
        st.setdefault("tags", {})
        st.setdefault("cats", {})
        st.setdefault("media", {})
        return st
    except (json.JSONDecodeError, OSError) as exc:
        warn(f"state file {path} unreadable ({exc}); starting fresh")
        return {"version": 1, "notes": {}, "tags": {}, "cats": {}, "media": {}}


def save_state(path: str, state: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Vault reading
# ---------------------------------------------------------------------------

def iter_markdown_files(vault_root: str):
    for root, dirs, files in os.walk(vault_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                full = os.path.join(root, f)
                yield os.path.relpath(full, vault_root)


def iter_asset_files(vault_root: str):
    for root, dirs, files in os.walk(vault_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for f in files:
            if not f.endswith(".md"):
                yield os.path.relpath(os.path.join(root, f), vault_root)


def read_note(vault_root: str, rel: str) -> Optional[str]:
    path = os.path.join(vault_root, rel)
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        warn(f"cannot read {rel}: {exc}")
        return None


def compute_md5(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.md5(data).hexdigest()


def parse_frontmatter(raw: str) -> tuple[dict, str]:
    try:
        post = frontmatter.loads(raw)
        meta = dict(post.metadata or {})
        body = post.content or ""
        return meta, body
    except Exception as exc:
        warn(f"frontmatter parse failed ({exc}); treating whole file as body")
        return {}, raw


def should_publish(meta: dict) -> bool:
    return meta.get("publish") is True


def extract_title(meta: dict, body: str, rel: str) -> str:
    t = meta.get("title")
    if isinstance(t, str) and t.strip():
        return t.strip()
    m = re.search(r"^\s*#\s+(.+?)\s*$", body, re.MULTILINE)
    if m:
        t = re.sub(r"[*_`<>]", "", m.group(1)).strip()
        if t:
            return t
    return os.path.basename(rel)[:-3]


def slugify(rel_path: str) -> str:
    """Deterministic, collision-free slug from the note's relative path."""
    s = rel_path[:-3] if rel_path.endswith(".md") else rel_path
    s = s.replace("\\", "/")
    # Keep word characters (incl. CJK), everything else -> single dash.
    s = re.sub(r"[^\w-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    s = s.lower()
    return s or "post"


def extract_tags(meta: dict) -> list[str]:
    tags = meta.get("tags")
    if isinstance(tags, str):
        return [t.strip() for t in tags.split(",") if t.strip()]
    if isinstance(tags, list):
        return [t.strip() for t in tags if isinstance(t, str) and t.strip()]
    return []


def derive_categories(rel: str) -> list[str]:
    """Module-level category derived from the note's relative path.

    A note is categorized by the first folder under the top-level content
    directory. Examples (vault root = repo root):
      JAVA-AI成长路线/Docker/1-镜像与容器.md  -> ["Docker"]
      JAVA-AI成长路线/JavaSE/并发/3-线程池.md -> ["JavaSE"]
      JAVA-AI成长路线/00-知识地图.md          -> ["JAVA-AI成长路线"]
      README.md                               -> []   (vault root, no category)
    """
    parts = rel.replace("\\", "/").split("/")
    if len(parts) <= 1:
        return []                       # file at vault root -> no category
    if len(parts) == 2:
        return [parts[0]]               # directly under a folder -> that folder
    return [parts[1]]                   # nested -> first-level module folder


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def build_basename_index(vault_root: str) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for rel in iter_markdown_files(vault_root):
        base = os.path.basename(rel)[:-3]
        index.setdefault(base, []).append(rel)
    return index


def predicted_link(base_url: str, slug: str) -> str:
    today = date.today()
    return f"{base_url}/{today.year}/{today.month:02d}/{today.day:02d}/{slug}/"


def resolve_target_rel(target: str, note_dir: str, basename_index: dict) -> Optional[str]:
    """Resolve a wiki-link target to a vault relative path."""
    target = target.strip()
    base = os.path.basename(target)
    if base.endswith(".md"):
        base = base[:-3]
    if not base:
        return None
    cands = basename_index.get(base, [])
    if not cands:
        return None
    if len(cands) == 1:
        return cands[0]
    same_dir = [c for c in cands if os.path.dirname(c) == note_dir]
    if len(same_dir) == 1:
        return same_dir[0]
    warn(f"ambiguous wiki-link '{target}' -> {cands}; using first")
    return cands[0]


def render_markdown(body: str) -> str:
    return markdown_lib.markdown(body, extensions=["extra", "sane_lists"])


class Renderer:
    """Applies wiki-link / image rewriting, then converts MD -> HTML."""

    def __init__(self, vault_root: str, basename_index: dict,
                 on_image: Callable[[str, str], str]):
        self.vault_root = vault_root
        self.basename_index = basename_index
        self.on_image = on_image  # callback(rel_path, src) -> final url (uploads as needed)
        self._asset_cache: Optional[list[str]] = None

    def _asset_rels(self) -> list[str]:
        if self._asset_cache is None:
            self._asset_cache = list(iter_asset_files(self.vault_root))
        return self._asset_cache

    def resolve_image_file(self, note_rel: str, src: str) -> Optional[str]:
        """Map an image reference to a vault-relative path, or None."""
        src = src.strip()
        if "|" in src:  # Obsidian size suffix ![[img.png|100]]
            src = src.split("|", 1)[0]
        note_dir = os.path.dirname(note_rel)
        if "/" in src:
            cand = os.path.normpath(os.path.join(note_dir, src))
            if os.path.exists(os.path.join(self.vault_root, cand)):
                return cand
        base = os.path.basename(src)
        if base:
            for rel in self._asset_rels():
                if os.path.basename(rel) == base:
                    return rel
        return None

    def _rewrite_images(self, note_rel: str, body: str, media_map: dict) -> str:
        def resolve(src: str) -> str:
            rel = self.resolve_image_file(note_rel, src)
            if not rel:
                warn(f"{note_rel}: image not found '{src}', dropping it")
                return ""
            url = media_map.get(rel, {}).get("url")
            if url is None:
                url = self.on_image(rel, src)
            return url

        def md_sub(m: re.Match) -> str:
            alt, src = m.group(1), m.group(2).strip()
            if re.match(r"^(https?://|data:|//)", src):
                return m.group(0)
            url = resolve(src)
            return f"![{alt}]({url})" if url else ""

        def obs_sub(m: re.Match) -> str:
            src = m.group(1).strip().split("|", 1)[0].strip()
            if re.match(r"^(https?://|data:|//)", src):
                return m.group(0)
            url = resolve(src)
            return f"![]({url})" if url else ""

        body = MD_IMAGE_RE.sub(md_sub, body)
        body = OBS_EMBED_RE.sub(obs_sub, body)
        return body

    def _rewrite_wikilinks(self, note_rel: str, body: str, link_map: dict) -> str:
        note_dir = os.path.dirname(note_rel)

        def sub(m: re.Match) -> str:
            raw = m.group(1)
            # [[Target|alias]], [[Target#heading]], [[Target#heading|alias]]
            target_part, _, alias_part = raw.partition("|")
            target_part = target_part.split("#", 1)[0].strip()
            text = alias_part.strip() if alias_part else target_part
            target_rel = resolve_target_rel(target_part, note_dir, self.basename_index)
            if target_rel and link_map.get(target_rel):
                return f"[{text}]({link_map[target_rel]})"
            return text  # unpublished -> plain text

        return WIKILINK_RE.sub(sub, body)

    def render(self, note_rel: str, body: str, link_map: dict, media_map: dict) -> str:
        body = self._rewrite_images(note_rel, body, media_map)
        body = self._rewrite_wikilinks(note_rel, body, link_map)
        return render_markdown(body)


# ---------------------------------------------------------------------------
# WordPress API client
# ---------------------------------------------------------------------------

class BlogClient:
    def __init__(self, base_url: str, user: str, password: str, dry_run: bool = False):
        self.base_url = base_url.rstrip("/")
        self.user = user
        self.password = password
        self.dry_run = dry_run
        self.session = requests.Session()
        if user and password:
            self.session.auth = (user, password)

    def request(self, method: str, path: str, **kw) -> requests.Response:
        if self.dry_run:
            raise BlogSyncError(f"network call attempted in dry-run: {method} {path}")
        url = self.base_url + path
        kw.setdefault("timeout", 30)
        last: Optional[Exception] = None
        for attempt in range(4):
            try:
                resp = self.session.request(method, url, **kw)
            except requests.RequestException as exc:
                last = exc
                time.sleep(2 ** attempt)
                continue
            if resp.status_code == 429 or resp.status_code >= 500:
                last = BlogSyncError(f"HTTP {resp.status_code}: {resp.text[:200]}")
                time.sleep(2 ** attempt)
                continue
            return resp
        raise BlogSyncError(f"{method} {url} failed after retries: {last}")

    @staticmethod
    def _json_or_raise(resp: requests.Response, what: str) -> dict:
        if resp.status_code not in (200, 201):
            raise BlogSyncError(f"{what}: HTTP {resp.status_code} {resp.text[:300]}")
        return resp.json()

    def check_auth(self) -> dict:
        resp = self.request("GET", "/wp-json/wp/v2/users/me")
        if resp.status_code == 401:
            raise BlogSyncError(
                "authentication failed (401). Check WP_USER / WP_APP_PASSWORD and that "
                "Application Passwords are enabled over http "
                "(add_filter('wp_is_application_passwords_available', '__return_true')).")
        return self._json_or_raise(resp, "check_auth")

    def ensure_tag(self, name: str, tag_cache: dict) -> int:
        if name in tag_cache:
            return int(tag_cache[name])
        if self.dry_run:
            return 0
        resp = self.request("GET", "/wp-json/wp/v2/tags",
                            params={"search": name, "per_page": 100})
        data = resp.json() if resp.status_code == 200 else []
        for tag in data:
            if str(tag.get("name", "")).lower() == name.lower():
                tid = int(tag["id"])
                tag_cache[name] = tid
                return tid
        resp = self.request("POST", "/wp-json/wp/v2/tags", json={"name": name})
        tag = self._json_or_raise(resp, f"create tag '{name}'")
        tid = int(tag["id"])
        tag_cache[name] = tid
        return tid

    def ensure_category(self, name: str, cat_cache: dict) -> int:
        """Find-or-create a top-level WordPress category (parent = 0)."""
        key = name.lower()
        if key in cat_cache:
            return int(cat_cache[key])
        if self.dry_run:
            return 0
        resp = self.request("GET", "/wp-json/wp/v2/categories",
                            params={"search": name, "per_page": 100})
        data = resp.json() if resp.status_code == 200 else []
        for cat in data:
            if str(cat.get("name", "")).lower() == name.lower() \
                    and int(cat.get("parent", 0)) == 0:
                cid = int(cat["id"])
                cat_cache[key] = cid
                return cid
        resp = self.request("POST", "/wp-json/wp/v2/categories", json={"name": name})
        cat = self._json_or_raise(resp, f"create category '{name}'")
        cid = int(cat["id"])
        cat_cache[key] = cid
        return cid

    def get_post_by_slug(self, slug: str) -> Optional[dict]:
        if self.dry_run:
            return None
        for variant in (slug, urllib.parse.quote(slug, safe="")):
            resp = self.request("GET", "/wp-json/wp/v2/posts",
                                params={"slug": variant, "status": "any", "per_page": 5})
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    return data[0]
        return None

    def create_post(self, payload: dict) -> dict:
        if self.dry_run:
            return {"id": -1, "slug": payload["slug"],
                    "link": predicted_link(self.base_url, payload["slug"])}
        resp = self.request("POST", "/wp-json/wp/v2/posts", json=payload)
        return self._json_or_raise(resp, "create post")

    def update_post(self, wp_id: int, payload: dict) -> dict:
        if self.dry_run:
            return {"id": wp_id, "slug": payload["slug"], "link": f"{self.base_url}/?p={wp_id}"}
        resp = self.request("POST", f"/wp-json/wp/v2/posts/{wp_id}", json=payload)
        return self._json_or_raise(resp, f"update post {wp_id}")

    def upload_media(self, rel: str, abs_path: str) -> dict:
        if self.dry_run:
            return {"media_id": -1, "url": f"__UPLOAD__:{rel}"}
        filename = os.path.basename(rel)
        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        with open(abs_path, "rb") as fh:
            resp = self.request("POST", "/wp-json/wp/v2/media",
                                files={"file": (filename, fh, mime)})
        data = self._json_or_raise(resp, f"upload media {rel}")
        url = data.get("source_url") or data.get("link") or data.get("guid", {}).get("rendered")
        return {"media_id": int(data.get("id", -1)), "url": url}


# ---------------------------------------------------------------------------
# Sync orchestration
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    args = parse_args(argv)
    vault = os.path.abspath(args.vault)
    state_path = os.path.join(vault, STATE_FILE)
    state = load_state(state_path)
    errors: list[str] = []

    if not args.base_url:
        log("error: --base-url (or env WP_BASE_URL) is required")
        return 1

    client = BlogClient(args.base_url, args.user, args.password, dry_run=args.dry_run)

    if args.check_auth:
        if args.dry_run:
            log("--check-auth cannot run with --dry-run")
            return 1
        try:
            me = client.check_auth()
            log(f"auth OK: {me.get('name')} <{me.get('email', '')}>")
            return 0
        except BlogSyncError as exc:
            log(f"auth FAILED: {exc}")
            return 1

    # ---- gather published notes ------------------------------------------
    basename_index = build_basename_index(vault)
    note_meta: dict[str, tuple[dict, str, str]] = {}  # rel -> (meta, body, content_md5)
    published: list[str] = []
    for rel in iter_markdown_files(vault):
        raw = read_note(vault, rel)
        if raw is None:
            continue
        meta, body = parse_frontmatter(raw)
        if should_publish(meta):
            published.append(rel)
            note_meta[rel] = (meta, body, compute_md5(raw))
    published.sort()

    log(f"found {len(published)} note(s) with publish: true "
        f"({len(state['notes'])} tracked in state)")

    # link map: rel -> final blog URL (predicted for not-yet-created notes)
    link_map = {rel: rec.get("link", "")
                for rel, rec in state["notes"].items() if rec.get("link")}
    for rel in published:
        if not link_map.get(rel):
            link_map[rel] = predicted_link(args.base_url, slugify(rel))

    media_map = state["media"]
    tag_cache = state["tags"]
    cat_cache = state["cats"]

    def upload_image(rel: str, src: str) -> str:
        abs_path = os.path.join(vault, rel)
        if not os.path.exists(abs_path):
            warn(f"{rel}: file missing, dropping image")
            return ""
        try:
            with open(abs_path, "rb") as fh:
                file_md5 = compute_md5(fh.read())
        except OSError as exc:
            warn(f"{rel}: cannot read ({exc}), dropping image")
            return ""
        existing = media_map.get(rel)
        if existing and existing.get("file_md5") == file_md5 and existing.get("url"):
            return existing["url"]
        try:
            info = client.upload_media(rel, abs_path)
        except BlogSyncError as exc:
            errors.append(f"image {rel}: {exc}")
            log(f"  [error] image {rel}: {exc}")
            return ""
        if not args.dry_run and info.get("url"):
            media_map[rel] = {"media_id": info.get("media_id", -1),
                              "url": info["url"], "file_md5": file_md5}
        return info.get("url", "")

    renderer = Renderer(vault, basename_index, on_image=upload_image)
    stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}

    def sync_note(rel: str) -> None:
        meta, body, content_md5 = note_meta[rel]
        rec = state["notes"].get(rel, {})
        cats = derive_categories(rel)
        cat_md5 = compute_md5(json.dumps(cats, ensure_ascii=False))
        if rec.get("content_md5") == content_md5 and rec.get("cat_md5") == cat_md5:
            stats["skipped"] += 1
            log(f"  [skip] {rel}")
            return

        title = extract_title(meta, body, rel)
        slug = slugify(rel)
        html = renderer.render(rel, body, link_map, media_map)
        payload: dict[str, Any] = {
            "title": title,
            "content": html,
            "slug": slug,
            "status": "publish",
        }
        tags = extract_tags(meta)
        if tags:
            tag_ids = []
            for t in tags:
                try:
                    tag_ids.append(client.ensure_tag(t, tag_cache))
                except BlogSyncError as exc:
                    errors.append(f"{rel}: tag '{t}': {exc}")
            payload["tags"] = tag_ids
        if cats:
            cat_ids = []
            for c in cats:
                try:
                    cat_ids.append(client.ensure_category(c, cat_cache))
                except BlogSyncError as exc:
                    errors.append(f"{rel}: category '{c}': {exc}")
            if cat_ids:
                payload["categories"] = cat_ids
        desc = meta.get("description")
        if isinstance(desc, str) and desc.strip():
            payload["excerpt"] = desc.strip()

        try:
            existing_id = rec.get("wp_id") if rec else None
            if not existing_id:
                existing = client.get_post_by_slug(slug)
                if existing:
                    existing_id = int(existing["id"])
            if existing_id:
                data = client.update_post(existing_id, payload)
                action = "UPDATE"
            else:
                data = client.create_post(payload)
                action = "CREATE"
        except BlogSyncError as exc:
            errors.append(f"{rel}: {exc}")
            stats["errors"] += 1
            log(f"  [error] {rel}: {exc}")
            return

        if args.dry_run:
            log(f"  [dry:{action}] {rel} -> slug={slug}")
            stats[("created" if action == "CREATE" else "updated")] += 1
            return

        wp_id = int(data.get("id", -1))
        slug = data.get("slug") or slug
        link = data.get("link") or predicted_link(args.base_url, slug)
        state["notes"][rel] = {
            "wp_id": wp_id,
            "slug": slug,
            "link": link,
            "content_md5": content_md5,
            "cat_md5": cat_md5,
            "rendered_md5": compute_md5(html),
        }
        link_map[rel] = link
        stats[("created" if action == "CREATE" else "updated")] += 1
        log(f"  [{action}] {rel} -> {link}")

    # ---- pass 1: create / update changed notes ----------------------------
    for rel in published:
        sync_note(rel)

    # ---- mark notes that are no longer published --------------------------
    for rel in list(state["notes"]):
        if rel not in published and not state["notes"][rel].get("retired"):
            state["notes"][rel]["retired"] = True
            log(f"  [retired] {rel} (blog post kept as-is)")

    # ---- pass 2: re-render everything for link convergence ----------------
    for rel in sorted(state["notes"]):
        rec = state["notes"][rel]
        if rec.get("retired") or not rec.get("wp_id"):
            continue
        if rel not in note_meta:  # file deleted but state remains
            continue
        meta, body, _ = note_meta[rel]
        html = renderer.render(rel, body, link_map, media_map)
        rendered_md5 = compute_md5(html)
        if rec.get("rendered_md5") == rendered_md5:
            continue
        p2cats = derive_categories(rel)
        payload = {"title": extract_title(meta, body, rel),
                   "content": html,
                   "slug": rec.get("slug") or slugify(rel)}
        if p2cats:
            ids = []
            for c in p2cats:
                try:
                    ids.append(client.ensure_category(c, cat_cache))
                except BlogSyncError as exc:
                    errors.append(f"{rel} (pass2): category '{c}': {exc}")
            if ids:
                payload["categories"] = ids
        try:
            if not args.dry_run:
                client.update_post(rec["wp_id"], payload)
                rec["rendered_md5"] = rendered_md5
            stats["updated"] += 1
            log(f"  [converge] {rel} -> cross-links refreshed")
        except BlogSyncError as exc:
            errors.append(f"{rel} (pass2): {exc}")
            stats["errors"] += 1

    if not args.dry_run:
        save_state(state_path, state)

    log("")
    log(f"Summary: created={stats['created']} updated={stats['updated']} "
        f"skipped={stats['skipped']} errors={stats['errors']}")
    if errors:
        log("errors:\n  " + "\n  ".join(errors))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
