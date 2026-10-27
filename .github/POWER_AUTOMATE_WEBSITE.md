# GhostHeart website automation build sheet

This build uses services already connected to GhostHeart. It does not require Mailchimp Standard, Metricool Premium, Zapier, Make, or another paid subscription.

## Verified destinations

- Microsoft 365 identity: `signal@myghostheart.com`
- Team: `GhostHeart Studios`
- Team ID: `fda17bcb-3345-4f43-a7a3-cc0fc4b4c188`
- Channel: `GhostHeart`
- Channel ID: `19:c3402bb7448f4c00abdd99a694e74efa@thread.tacv2`
- Public site: `https://www.myghostheart.com/`
- Public journal: `https://www.myghostheart.com/journal/`
- RSS: `https://www.myghostheart.com/journal/feed.xml`

## Flow 1: GhostHeart Website and Journal Publisher

Keep this flow Off while building and checking it.

1. **Recurrence** — every 15 minutes, time zone `Central Time`.
2. **Get items** — existing SharePoint `Production Register`.
3. **Filter array** — exact rows where:
   - Area is `GhostHeart`;
   - Type is `Website`;
   - Status is `Approved`;
   - scheduled/release date is present and is less than or equal to `utcNow()`;
   - the row's next action is `Publish journal`; and
   - its master/final link points inside the exact private `Journal_Schedule` folder.
4. **Duplicate guard** — continue only when exactly one row matches the stable list item ID. Zero rows is a quiet no-op; more than one is a blocking Teams/email exception.
5. **Get file content using path** — read the exact JSON file from SharePoint.
6. **Parse JSON** — use `.github/content/journal-post-template.json` as the schema model.
7. **Create a repository dispatch event** — standard GitHub connector, event `publish_journal`, payload with one top-level `post` object.
8. **Update item** — set Next Action to `Dispatch accepted; awaiting verified website deployment`. Do not mark the item Released here.

## Flow 2: GhostHeart Website Deployment Notifications

Keep this flow Off while building and checking it.

1. **When a Teams webhook request is received** — Teams standard connector, authentication `Anyone`.
2. **Condition** — require `status` to be `success` or `failure` and `event` to be one of:
   - `journal_published`
   - `journal_publish_failed`
   - `website_deployed`
   - `website_deploy_failed`
3. **Post message in a chat or channel** — Flow bot, channel `GhostHeart` in `GhostHeart Studios`.
4. **Send an email (V2)** — to `signal@myghostheart.com` with the same state, public URL when successful, and GitHub run URL as evidence.

Suggested success message:

> GHOSTHEART WEBSITE — LIVE\n\nThe approved website update deployed successfully.\n\nPage: {page_url}\nEvidence: {run_url}\nCommit: {commit}

Suggested failure message:

> GHOSTHEART WEBSITE — NEEDS ATTENTION\n\nThe scheduled website update did not complete. No live claim was recorded.\n\nEvidence: {run_url}

## Activation sequence

1. Save both flows.
2. Turn both flows Off.
3. Verify both show Off and zero runs.
4. Create the Teams webhook URL and store it as the GitHub Actions secret `GHOSTHEART_NOTIFY_WEBHOOK`.
5. Change the repository's GitHub Pages source from branch deployment to GitHub Actions.
6. Commit and push the reviewed website plus these workflows.
7. Run one controlled test with a harmless approved test entry or a manual website deployment.
8. Verify the public page, Teams message, email, workflow run, and absence of duplicates.
9. Turn on the two flows only after the controlled test is accepted.
