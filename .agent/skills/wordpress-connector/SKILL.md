---
name: WordPress Connector
description: Interact with WordPress sites via the WordPress REST API and Application Passwords. Supports creating posts, drafts, media uploads, and listing content.
---

# WordPress Connector Skill

A zero-dependency Python connector for WordPress using the native WordPress REST API and Application Passwords.

## Capabilities

1. **Test Auth**: Verify credentials against `/wp-json/wp/v2/users/me`.
2. **Create Post**: Create a new post as `draft` or `publish` with HTML content.
3. **Update Post**: Update title, content, or status of an existing post.
4. **Delete Post**: Move post to trash or permanently delete (`--force`).
5. **List Posts**: View posts filtered by status (`publish`, `draft`, `any`).
6. **Upload Media**: Upload images or attachments directly to the Media Library.
7. **Get Post**: Retrieve full post details.

## Configuration

Credentials are stored in `.agent/skills/wordpress-connector/token.env` (git-ignored):
```env
WP_URL=https://lingkarayah.id
WP_USER=adminla
WP_APP_PASS=mdDN 25OA xAJ8 0z4w F2fh p3jq
```

## Usage

```bash
# Test connection & authentication
python .agent/skills/wordpress-connector/scripts/wp_client.py --action test-auth

# List latest posts (published)
python .agent/skills/wordpress-connector/scripts/wp_client.py --action list-posts --limit 5

# List draft posts
python .agent/skills/wordpress-connector/scripts/wp_client.py --action list-posts --status draft

# Create a draft post
python .agent/skills/wordpress-connector/scripts/wp_client.py --action create-post --title "Judul Artikel" --content "<p>Isi artikel...</p>" --status draft

# Update a post
python .agent/skills/wordpress-connector/scripts/wp_client.py --action update-post --id 123 --title "Judul Baru" --status draft

# Delete a post (move to trash or permanent)
python .agent/skills/wordpress-connector/scripts/wp_client.py --action delete-post --id 123
python .agent/skills/wordpress-connector/scripts/wp_client.py --action delete-post --id 123 --force

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
