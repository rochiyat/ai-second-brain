---
name: WordPress Connector
description: Interact with WordPress sites via the WordPress REST API and Application Passwords. Supports creating posts, drafts, media uploads, and listing content.
---

# WordPress Connector Skill

A zero-dependency Python connector for WordPress using the native WordPress REST API and Application Passwords.

## Capabilities

1. **Test Auth**: Verify credentials against `/wp-json/wp/v2/users/me`.
2. **Create Post**: Create a new post as `draft` or `publish` with HTML content.
3. **List Posts**: View posts filtered by status (`publish`, `draft`, `any`).
4. **Upload Media**: Upload images or attachments directly to the Media Library.
5. **Get Post**: Retrieve full post details.

## Configuration

Credentials are stored in `.agent/skills/wordpress-connector/token.env` (git-ignored):
```env
WP_URL=https://lingkarayah.id
WP_USER=AI-Second-Brain
WP_APP_PASS=mdDN 25OA xAJ8 0z4w F2fh p3jq
```

## Usage

```bash
# Test connection & authentication
python .agent/skills/wordpress-connector/scripts/wp_client.py --action test-auth

# List latest posts
python .agent/skills/wordpress-connector/scripts/wp_client.py --action list-posts --limit 5

# Create a draft post
python .agent/skills/wordpress-connector/scripts/wp_client.py --action create-post --title "Judul Artikel" --content "<p>Isi artikel...</p>" --status draft

# Create a post from markdown/HTML file
python .agent/skills/wordpress-connector/scripts/wp_client.py --action create-post --title "Judul Artikel" --content-file "path/to/content.html" --status draft

# Upload media
python .agent/skills/wordpress-connector/scripts/wp_client.py --action upload-media --file "path/to/image.png"
```

## LiteSpeed / Apache Authorization Header Note

If the REST API returns `401 rest_not_logged_in`, the web server (LiteSpeed or Apache) is stripping the `Authorization` header before PHP receives it.
Fix by adding this line into WordPress `.htaccess`:
```apache
RewriteEngine On
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
```
