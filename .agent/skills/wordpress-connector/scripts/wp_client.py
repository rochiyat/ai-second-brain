#!/usr/bin/env python3
"""
WordPress REST API Client
Interacts with WordPress via Application Passwords.
Zero external dependencies (uses standard library urllib).
"""

import os
import sys
import json
import base64
import ssl
import argparse
import urllib.request
import urllib.error
import mimetypes

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_ENV_PATH = os.path.join(SKILL_DIR, "token.env")

def load_config():
    config = {
        "WP_URL": os.environ.get("WP_URL"),
        "WP_USER": os.environ.get("WP_USER"),
        "WP_APP_PASS": os.environ.get("WP_APP_PASS")
    }
    if os.path.exists(TOKEN_ENV_PATH):
        with open(TOKEN_ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    config[k.strip()] = v.strip().strip("'\"")
    if not config["WP_URL"] or not config["WP_USER"] or not config["WP_APP_PASS"]:
        print(f"[ERROR] Missing config in {TOKEN_ENV_PATH} or environment variables.", file=sys.stderr)
        sys.exit(1)
    config["WP_URL"] = config["WP_URL"].rstrip("/")
    return config

def get_auth_headers(config, content_type="application/json"):
    user = config["WP_USER"]
    password = config["WP_APP_PASS"]
    auth_str = f"{user}:{password}"
    b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ai-second-brain/1.0",
        "Accept": "application/json"
    }
    if content_type:
        headers["Content-Type"] = content_type
    return headers

def make_request(endpoint, method="GET", data=None, content_type="application/json"):
    config = load_config()
    url = f"{config['WP_URL']}/wp-json/wp/v2/{endpoint.lstrip('/')}"
    headers = get_auth_headers(config, content_type=content_type)
    
    body = None
    if data is not None:
        if isinstance(data, (dict, list)):
            body = json.dumps(data).encode("utf-8")
        elif isinstance(data, bytes):
            body = data
        elif isinstance(data, str):
            body = data.encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            resp_data = resp.read().decode("utf-8")
            if resp_data:
                return json.loads(resp_data)
            return {"status": resp.status}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(err_body)
            print(f"[HTTP {e.code}] {err_json.get('message', err_body)}", file=sys.stderr)
            return err_json
        except Exception:
            print(f"[HTTP {e.code}] {err_body}", file=sys.stderr)
            return {"error": e.code, "details": err_body}
    except Exception as e:
        print(f"[REQUEST ERROR] {e}", file=sys.stderr)
        return {"error": str(e)}

def test_auth():
    print("Testing WordPress REST API authentication...")
    res = make_request("users/me")
    if isinstance(res, dict) and "id" in res:
        print(f"[SUCCESS] Authenticated as: {res.get('name')} (ID: {res.get('id')})")
        print(f"Roles: {res.get('roles')}")
        return True
    else:
        print(f"[FAILED] Authentication failed: {res}")
        return False

def list_posts(status=None, limit=10):
    endpoint = f"posts?per_page={limit}"
    if status and status != "publish":
        endpoint += f"&status={status}"
    res = make_request(endpoint)
    if isinstance(res, list):
        print(f"Found {len(res)} posts:")
        for p in res:
            title = p.get("title", {}).get("rendered", "Untitled")
            print(f"- [ID: {p.get('id')}] [{p.get('status')}] {title} ({p.get('link')})")
        return res
    return res

def create_post(title, content, status="draft", excerpt="", categories=None, tags=None, featured_media=None):
    payload = {
        "title": title,
        "content": content,
        "status": status
    }
    if excerpt:
        payload["excerpt"] = excerpt
    if categories:
        payload["categories"] = categories
    if tags:
        payload["tags"] = tags
    if featured_media:
        payload["featured_media"] = featured_media

    res = make_request("posts", method="POST", data=payload)
    if isinstance(res, dict) and "id" in res:
        print(f"[SUCCESS] Post created! ID: {res.get('id')} | Status: {res.get('status')} | URL: {res.get('link')}")
    else:
        print(f"[FAILED] Could not create post: {res}")
    return res

def upload_media(file_path):
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}", file=sys.stderr)
        return None

    filename = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    config = load_config()
    url = f"{config['WP_URL']}/wp-json/wp/v2/media"
    headers = get_auth_headers(config, content_type=mime_type)
    headers["Content-Disposition"] = f'attachment; filename="{filename}"'

    req = urllib.request.Request(url, data=file_bytes, headers=headers, method="POST")
    ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print(f"[SUCCESS] Media uploaded! ID: {res.get('id')} | URL: {res.get('source_url')}")
            return res
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"[HTTP {e.code}] {err_body}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[UPLOAD ERROR] {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description="WordPress REST API Client")
    parser.add_argument("--action", choices=["test-auth", "list-posts", "create-post", "upload-media", "get-post"], default="test-auth")
    parser.add_argument("--title", help="Post title")
    parser.add_argument("--content", help="Post HTML content or text")
    parser.add_argument("--content-file", help="Path to file containing post content")
    parser.add_argument("--status", choices=["draft", "publish", "pending", "private", "any"], default=None)
    parser.add_argument("--file", help="File path for upload-media")
    parser.add_argument("--id", type=int, help="Post ID")
    parser.add_argument("--limit", type=int, default=10, help="Limit for list-posts")

    args = parser.parse_args()

    if args.action == "test-auth":
        test_auth()
    elif args.action == "list-posts":
        list_posts(status=args.status, limit=args.limit)
    elif args.action == "get-post":
        if not args.id:
            print("[ERROR] --id is required for get-post", file=sys.stderr)
            sys.exit(1)
        res = make_request(f"posts/{args.id}")
        print(json.dumps(res, indent=2))
    elif args.action == "create-post":
        if not args.title:
            print("[ERROR] --title is required for create-post", file=sys.stderr)
            sys.exit(1)
        content = args.content or ""
        if args.content_file and os.path.exists(args.content_file):
            with open(args.content_file, "r", encoding="utf-8") as f:
                content = f.read()
        create_post(args.title, content, status=args.status or "draft")
    elif args.action == "upload-media":
        if not args.file:
            print("[ERROR] --file is required for upload-media", file=sys.stderr)
            sys.exit(1)
        upload_media(args.file)

if __name__ == "__main__":
    main()
