# BrightSign LS424 — Red-on-black news ticker

A lean HTML/CSS/JavaScript ticker customized for the 2019 BrightSign LS424 (Series 4). The **only visible element** is a single bright-red headline scrolling from right to left across the vertical center of a pure black screen. No logos, labels, footer, news source names, browser controls or borders appear.

## What plays and what refreshes

**Playback is continuous, not one headline for six hours.** At all times the player loops through up to **24 different news headlines** (headline 1, then 2, ... then 24, then back to 1). Each line slides horizontally across the center of a black screen in red. The six-hour schedule changes the **list of headlines**, not the animation timing. BrightSign checks for updated JSON every five minutes; if the list has changed, the browser switches lists after finishing its current headline. This makes it safe to keep the screen running 24/7.

**No personal computer needs to stay on** if you enable the GitHub Actions workflow and GitHub Pages. The Action fetches the feeds and deploys the site in one job; this matters because committing a file with GitHub's default action token does *not* trigger a separate Pages build.

## Files

- `site/index.html` — the projector display (no Adobe, no external libraries or fonts).
- `site/headlines.json` — placeholder/demo data **NOT LIVE NEWS**.
- `scripts/update_news.py` — Python RSS to JSON updater (standard library only).
- `.github/workflows/publish-news.yml` — *optional* six-hour cloud scheduler and GitHub Pages deployment.
- `tests` — offline news parser tests.

### Quick local demo (no GitHub account required)

From the project folder:

```bash
python3 -m http.server 8000 --directory site
```

Open http://localhost:8000 in a desktop browser. For a demo content update, edit `site/headlines.json` or run this safe offline test:

```bash
python3 scripts/update_news.py --fixture tests/example-feed.xml
```

To fetch current RSS titles instead (Internet required):

```bash
python3 scripts/update_news.py
```

The script won't replace previous valid JSON when all RSS fetches fail. Two default sources are BBC World and NPR World; publishers' RSS policies and redistribution/attribution requirements should be checked for public exhibition use.

## Option A: Host on any web server — no GitHub

1. Upload the *contents* of `site/` (both `index.html` and `headlines.json`) to the SAME directory under one public HTTPS website, e.g. `https://example.org/ticker/index.html` and `https://example.org/ticker/headlines.json`.
2. Point BrightSign's HTML page/state to `https://example.org/ticker/index.html`.
3. Run `python3 scripts/update_news.py` every six hours on an always-on computer or server, using Windows Task Scheduler, macOS launchd, or cron.
4. Publish the generated `site/headlines.json` file to your website after each successful run. This can be automated through your host's SFTP, deploy API, object storage upload, or direct webroot write (if Python runs on the same server). **Generating JSON locally does NOT automatically put it on the internet**.
5. The BrightSign HTML checks `headlines.json` every five minutes, applying new titles on the next headline transition. No video export, Adobe automation, or recurring player presentation re-publish is needed.

**Important:** Same-origin hosting makes browser data access simple. A public static web host alone does not schedule RSS updates. You also need an automated updater and deployment mechanism.

### An easy non-GitHub hosting option: Cloudflare Pages

You can manually deploy the `site` folder by dragging it into Cloudflare Pages via **Direct Upload** (https://developers.cloudflare.com/pages/get-started/direct-upload/). The site will display the bundled demo headlines. To automatically update every six hours, use an always-on computer/server to run Python and deploy the `site` folder using Cloudflare's `wrangler` CLI:

```bash
python3 scripts/update_news.py
npx wrangler pages deploy site --project-name YOUR_CLOUDFLARE_PROJECT
```

Requires Node.js/npm, Wrangler authorization (`npx wrangler login`) and an already created Pages Direct Upload project. Test manually first, then schedule BOTH commands every six hours. For reliability, do not deploy if Python fails; the previous website should remain unchanged. Cloudflare Workers scheduled tasks are another serverless (more advanced) GitHub-free approach.

### Option B: Use GitHub Pages + Actions (also optional)

Upload the repository, including hidden `.github`, to a GitHub repository. Enable **Settings → Pages → Source: GitHub Actions**, then run the workflow manually once. The supplied workflow refreshes RSS and publishes the website four times per day using GitHub-hosted runners. You don't need to leave your own computer on. GitHub scheduled runs aren't guaranteed to start on time and can be disabled after prolonged inactivity on public repositories, so monitor freshness for long-running installations.

## Installing on a BrightSign LS424

- Connect the player to Ethernet/internet, HDMI projector, and an appropriate microSD card. Configure its clock/NTP; older LS424 devices can lose time across power loss, which may break HTTPS connections.
- Check BrightSignOS version. Modern BrightSign Author explicitly lists LS424 with minimum **BrightSignOS 8.0**. Update with the appropriate compatible firmware after testing/backup if required.
- Create a full-screen **HTML** presentation in BrightSign Author / BrightAuthor:connected, or in BrightAuthor Classic add an **HTML Site** with **URL** pointing to your hosted `index.html`. Enable external data/network loading as required by the chosen editor. Publish the presentation initially. Afterwards, news changes happen on the website, not in BrightSign presentations.
- If the web URL cannot load after boot offline, the player may display nothing. A production offline-first version can package the HTML locally on its microSD and fetch a separately hosted, CORS-enabled JSON endpoint; this requires a different setup than the simple same-origin hosted page.
- BrightSign documents that a player can also run a standalone HTML site from a storage device without an authoring program. However, remote JSON refresh must still be set up separately for that architecture.

## Appearance settings

Edit `site/index.html`: 

- `color: #ff2020;` → headline red. For deeper red, use `#ff0000` or `#e10000`.
- `background: #000;` → true black.
- `font-family: "Courier New", Courier, monospace;` → ticker-like fixed-width type; no external font dependence.
- `font-size: 66px; (and a smaller value in the @media query)` → type size.
- `letter-spacing: .085em;` → ticker spacing.
- `var SPEED = 125;` → speed in px/s. Smaller is slower (try 90); larger is faster (try 170).
- `POLL_MS = 5 * 60 * 1000;` → how frequently the player checks for fresh headlines.
- `MAX_HEADLINES` in `scripts/update_news.py` and `.slice(0, 24)` in `site/index.html` → matching caps on number of headlines (default 24).

This sample uses a simple Courier-like face, not a proprietary LED dot-matrix font. If a true dot-matrix typeface is important, use a properly licensed webfont hosted with your site, after confirming performance on the LS424. No font files are included.

## Reliability checks

- CSS transform animates only one text layer (minimal rendering load for the LS424).
- Headlines update at the end of the current animation, not halfway through a headline.
- Fetch errors keep the last working set; browser localStorage is *best-effort*, not guaranteed after device reboots.
- Data shown in `site/headlines.json` is demo data until Python and your deployment are working.
- For production, add an independent alert if the JSON `updated_at` timestamp gets older than 7 hours. Check the player's remote online status separately.
- BrightSign LS424 has entry-level HTML performance; smoothness must be verified on the physical player before opening the installation.

Sources: 
- https://docs.brightsign.biz/hardware/ls424
- https://www.brightsign.biz/wp-content/uploads/2023/04/LS4-datasheet.pdf
- https://docs.brightsign.biz/author/brightsign-author
- https://docs.brightsign.biz/setup-faqs
- https://brightsign.atlassian.net/wiki/spaces/BA44/pages/84414698/4.4-HTML%2BSites
- https://developers.cloudflare.com/pages/get-started/direct-upload/

## Cloud scheduling caveats

GitHub scheduled workflows are best-effort: runs may start late or be skipped under load. On public repositories, scheduled workflows may be disabled after 60 days without qualifying repository activity. For permanent unattended installations, add a separate stale-feed monitor or choose a paid/managed scheduler with better operational guarantees. The display continues showing the last valid list if an update fails. The supplied workflow is scheduled at 00:17, 06:17, 12:17 and 18:17 **UTC**.

After uploading this full project to a **public GitHub repository**, choose **Settings > Pages > Build and deployment > Source: GitHub Actions**. Under **Actions**, run the **Refresh and publish news projection** workflow manually once. Confirm the published `headlines.json` is real news (`demo: false`) and then use the site's HTTPS URL as the BrightSign HTML source.
