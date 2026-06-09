# APIP Public Beta Launch Checklist

Deployment domain: `https://apip.openvalidations.com`

## Public Site

- Confirm homepage explains OpenVals positioning: APIP is a trust platform for AI profitability intelligence.
- Confirm beta waitlist form submits successfully.
- Confirm enterprise inquiry form submits successfully.
- Confirm footer links include Methodology, Trust Center, Developers, Pricing, Disclaimer, Changelog, Status, and Contact.
- Confirm public disclaimer states:
  - Data is source-backed.
  - Some metrics are estimated or derived.
  - Trust Index measures evidence quality, not company quality.

## SEO and Social

- Confirm global title and description render in production.
- Confirm page-level metadata exists for Public Beta, Pricing, Changelog, Status, Contact, and Disclaimer.
- Confirm Open Graph image resolves at `/og-image.svg`.
- Confirm favicon resolves at `/favicon.svg`.
- Confirm canonical URLs are set for public beta pages.

## Product Trust

- Confirm Trust Center loads.
- Confirm Trust Index loads.
- Confirm Methodology page explains confidence and AI Reality Index calculations.
- Confirm public metrics display confidence, source count, and last updated values.
- Confirm source lineage is visible where metrics are published.

## API and Commercial

- Confirm `/developers` shows authentication, examples, and plans.
- Confirm `/pricing` shows Community, Research, Professional, and Enterprise tiers.
- Confirm API key creation, rotation, and revocation work in `/admin`.
- Confirm usage events are recorded per API key.
- Confirm rate limits enforce Community, Research, Professional, and Enterprise plan rules.

## Operations

- Confirm `/status` page reflects launch posture.
- Confirm `/changelog` includes the public beta release.
- Confirm `/api/v1/health` passes behind `apip.openvalidations.com`.
- Confirm GitHub Actions pass for API and web.
- Confirm Docker Compose production services start cleanly.
- Confirm Cloudflare DNS and SSL mode are configured.

## Post-Launch Metrics

Track daily:

- Beta signups
- Enterprise inquiries
- API keys created
- API usage
- Top endpoints
- Active plans

These metrics are available in the admin dashboard under the Public Beta Funnel section.

## Go / No-Go

Launch is ready only when:

- Public beta pages render on desktop and mobile.
- Waitlist and enterprise submissions are captured.
- API and web CI are green.
- Production health checks pass.
- Disclaimer, pricing, and methodology are visible from the footer.
- No newly collected research evidence can publish without human approval.
