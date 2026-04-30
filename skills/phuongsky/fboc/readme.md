# Facebook Advanced (fboc)

A CLI tool for managing Facebook Pages and posts via the Graph API.

## Quick Start

### 1. Configure your access token

**Option A: Using facebook-config.json (Recommended)**

Edit `facebook-config.json` in this directory:
```json
{
  "FB_PAGE_ACCESS_TOKEN": "FB_PAGE_ACCESS_TOKEN",
  "FB_APP_ID": "(OPTIONAL) YOUR_APP_ID_HERE",
  "FB_APP_SECRET": "(OPTIONAL) YOUR_APP_SECRET_HERE",
  "description": "Replace the placeholder values with your actual Facebook credentials. Never commit this file with real secrets to version control."
}
```

**Option B: Using environment variable**

```powershell
$env:FB_PAGE_ACCESS_TOKEN = "your_page_access_token_here"
```

For permanent storage with environment variable, add to your PowerShell profile:

```powershell
# Edit your profile
notepad $PROFILE

# Add this line:
$env:FB_PAGE_ACCESS_TOKEN = "your_page_access_token_here"
```

### 2. Get a Page Access Token

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create an app or use existing
3. Use Graph API Explorer to generate token with:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_show_list`

### 3. Run the CLI

```powershell
facebook-advanced --help
```

## Commands

### List Posts

```powershell
facebook-advanced fb-post-list <page_id> [--limit 25] [--fields fields]
```

Example:
```powershell
facebook-advanced fb-post-list 123456789 --limit 10
```

### Create Post

```powershell
facebook-advanced fb-post-create <page_id> --message "Your message" [--link "https://example.com"]
```

Example:
```powershell
facebook-advanced fb-post-create 123456789 --message "Hello Facebook!" --link "https://example.com"
```

### List Comments

```powershell
facebook-advanced fb-comment-list <post_id> [--limit 25]
```

### Create Comment

```powershell
facebook-advanced fb-comment-create <post_id> --message "Your comment"
```

## Options

- `--message` - Post/comment text content
- `--link` - URL to share with post
- `--picture` - Image file path for post
- `--limit` - Number of items (default: 25)
- `--fields` - Comma-separated fields to retrieve
- `--help` - Show help message

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FB_PAGE_ACCESS_TOKEN` | Yes | Your Facebook Page Access Token |
| `FB_APP_ID` | No | Your Facebook App ID |
| `FB_APP_SECRET` | No | Your Facebook App Secret |

## Cron Jobs (openclaw)
```cron
# Cron Jobs UI
- New Job
`Assistant task prompt *` 
Example:
```
facebook-advanced fb-post-list 123456789 --limit 10
```
- Add job

# Terminal

openclaw cron add \
  --name "Tên job" \
  --cron "biểu thức cron" \
  --tz "Asia/Ho_Chi_Minh" \     # Múi giờ Việt Nam
  --session isolated \          # Nên dùng isolated để tránh làm bẩn context chính
  --message "facebook-advanced fb-post-list 123456789 --limit 10" \
  --announce                    # (tùy chọn) Gửi thông báo khi chạy xong

# CLI 
```powershell
```
openclaw cron add --name "Reminder" --at "2m" --session main --system-event "Reminder: Xem lại tài liệu" --wake now --delete-after-run

openclaw cron add --name "Morning Briefing" --cron "0 9 * * *" --tz "Asia/Ho_Chi_Minh" --session isolated --message "facebook-advanced fb-post-list 123456789 --limit 10" --deliver

## Troubleshooting

### "facebook-advanced: command not found"

Make sure the package is properly installed and in your PATH:

```powershell
# Check installation
npm list facebook-advanced -g

# Reinstall if needed
npm install -g facebook-advanced
```

### "FB_PAGE_ACCESS_TOKEN not set"

Set the environment variable:

```powershell
$env:FB_PAGE_ACCESS_TOKEN = "your_token_here"
```

### Token expired

Facebook tokens expire. Generate a new one from Graph API Explorer or extend it using the Graph API.

## License

MIT
