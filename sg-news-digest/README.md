# Singapore & Business Daily Digest

Sends a daily Telegram digest of Singapore news and global business/markets news,
pulled from RSS feeds (CNA, Straits Times, TODAY, CNBC). Runs on GitHub Actions
so it works even when your computer is off.

## Setup

1. Create a new GitHub repository (private is fine) and push this folder to it:

   ```bash
   cd sg-news-digest
   git init
   git add .
   git commit -m "Daily Singapore & business news digest"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

2. In the repo on GitHub, go to **Settings → Secrets and variables → Actions → New repository secret**
   and add two secrets:

   - `TELEGRAM_BOT_TOKEN` — your bot token from @BotFather
   - `TELEGRAM_CHAT_ID` — your Telegram chat ID

3. That's it. The workflow (`.github/workflows/daily-digest.yml`) runs every day
   at 07:00 Singapore time (23:00 UTC). You can also trigger it manually from
   the **Actions** tab → "Daily Singapore & Business Digest" → **Run workflow**
   to test it right away.

## Customizing

- Edit `SG_FEEDS` / `BUSINESS_FEEDS` in `digest.py` to change news sources.
- Edit `MAX_ITEMS_PER_SECTION` to change how many headlines per section.
- Edit the cron line in `.github/workflows/daily-digest.yml` to change the time
  (cron is in UTC; Singapore is UTC+8 year-round, no daylight saving).
