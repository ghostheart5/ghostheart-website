# GhostHeart Journal publishing

The live journal is `/journal/`; its RSS 2.0 feed is `/journal/feed.xml`. Metricool is already connected to that RSS URL.

## Existing entries

`.github/content/journal.json` is the public source for entries that have already been released. The repository is public, so future or draft copy must not be committed there early.

The builder updates all public journal surfaces together:

- the Journal index and article page;
- the RSS feed used by Metricool;
- the homepage's latest-entry link; and
- the journal section of `sitemap.xml`.

Run `py -3 .github/scripts/build_journal.py`, then `py -3 .github/scripts/validate_site.py` on Windows. Website checks regenerate those files and fail when committed output differs from the source.

## Scheduled entries without another subscription

Keep approved future copy in the private SharePoint folder:

`GhostHeart_Studios/10_GHOSTHEART/Website/Journal_Schedule`

Use `.github/content/journal-post-template.json` as the exact JSON shape. Each scheduled post must have:

- a unique permanent slug;
- an ISO 8601 publication timestamp with an America/Chicago offset;
- founder-approved title, summary, paragraphs, and links;
- an image path that already exists on the public website; and
- `status` set to `approved`.

Create one existing Production Register row for the item, using `Area = GhostHeart`, `Type = Website`, `Status = Approved`, the scheduled date, and the private JSON file as the master/final link. Reuse the existing Production Register rather than creating a second publishing register.

The disabled Power Automate flow `GhostHeart Website and Journal Publisher` should run every 15 minutes and select only exact due rows. Its GitHub **Create a repository dispatch event** action uses:

- Repository owner: `ghostheart5`
- Repository: `ghostheart-website`
- Event name: `publish_journal`
- Event payload: `{ "post": <parsed contents of the exact approved JSON file> }`

The GitHub connector, Teams connector, SharePoint connector, and Office 365 Outlook connector are standard connectors. The dispatch starts `.github/workflows/publish-approved-journal.yml`, which validates the payload, refuses early or changed duplicate slugs, builds the site, deploys GitHub Pages, and then calls the notification workflow.

## Teams and email notification route

Use one disabled Power Automate webhook flow named `GhostHeart Website Deployment Notifications`:

1. Trigger: Microsoft Teams **When a Teams webhook request is received**, authentication set to **Anyone**. Keep the generated URL only in the GitHub repository secret `GHOSTHEART_NOTIFY_WEBHOOK`.
2. Action: post the formatted result to the `GhostHeart` channel in the private `GhostHeart Studios` team.
3. Action: send the matching result with Office 365 Outlook to `signal@myghostheart.com`.
4. Never include the webhook URL, connector token, or unpublished journal body in either message.

Success means GitHub Pages returned a completed deployment. A GitHub commit or an accepted repository dispatch is not presented as a live publication.

The two Power Automate flows, the GitHub secret, and the GitHub Pages source change remain activation gates. Save new flows Off and verify zero runs before a controlled test and activation.
