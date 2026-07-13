# Xiaohongshu DOM Collection Design

Status: approved for planning

## Goal

Complete the Phase 1 content-acquisition loop for one local user: search Xiaohongshu with that user's existing local login, import public result cards into the existing project database, then reuse the existing ranking and draft-generation workflow.

## Scope and safety boundary

- This is a read-only, user-initiated keyword collection action. It never publishes, likes, comments, follows, or saves content.
- The application does not persist, expose, log, or commit Cookie values. A local-only browser gateway reads the existing `xhs-cli` session in memory solely to open a browser page.
- The collector reads only public search-result card fields that are visible to the signed-in user: note URL and ID, title, visible description, author display name and ID when available, content type, and visible engagement counts.
- Phase 1 does not collect note detail pages, followers, comments, livestream data, background jobs, proxy rotation, CAPTCHA bypassing, or automatic retries.

## Why this replaces the current CLI parser

The installed `xhs-cli` can create and retain a valid local login session and can open the current Xiaohongshu search page. Its legacy JSON parser, however, expects `window.__INITIAL_STATE__`, which the current page no longer exposes. The product will therefore retain the CLI only as a local-session bootstrap and add a page-DOM adapter as the supported collection path.

## Architecture

`XiaohongshuDomAdapter` implements the existing `PlatformAdapter` protocol. Its browser gateway opens a keyword search page under the local session, waits for result cards, extracts a bounded list of card DTOs from stable DOM selectors, and maps them to the existing `FixturePayload` / `CollectedNote` model.

The existing `CollectionService` remains the only writer. It creates a `CollectionRun`, upserts notes and authors, and creates metric snapshots. A failed browser or parsing operation creates no partial import and becomes a safe 422 response with an actionable message that excludes credentials and raw page data.

```text
UI keyword form
  -> POST /api/projects/{project_id}/collections/xiaohongshu?keyword=...
  -> CollectionService + XiaohongshuDomAdapter
  -> local signed-in browser page
  -> normalized FixturePayload
  -> collection runs, notes, authors, metric snapshots
  -> existing rank and draft endpoints
```

## Backend components

- `browser_gateway.py`: a small protocol and concrete gateway boundary for searching a locally signed-in page; browser startup and DOM extraction stay outside domain/service code.
- `xiaohongshu_dom_adapter.py`: validates the keyword, invokes the gateway, normalizes visible counts and URLs, and raises redacted domain errors.
- `router.py`: exposes the user-triggered `POST .../collections/xiaohongshu` endpoint and maps collection errors to 422.
- `CollectionService`: gains an atomic failure path that marks a started run failed only if a run has been created; collection failures before payload creation do not create notes or snapshots.

The exact browser automation dependency is isolated behind the gateway. Tests use captured public-card DTOs, never a real browser session, network request, QR code, or Cookie.

## UI components

The existing React application remains the primary product UI. It gains a `XiaohongshuImport` panel alongside the sample import:

- keyword input and explicit “collect public results” action;
- loading state explaining that the local signed-in browser is being used;
- completion summary with notes and snapshots imported;
- a concise error state for login expiry, browser unavailable, no results, or DOM compatibility changes;
- a notes preview after successful import, clearly labelled with the keyword and collection time.

The separate port-17777 Vue page stays a non-production visual preview and is not a second frontend source of truth.

## Data and error behavior

The current note, author, metric snapshot, and collection run tables remain the Phase 1 schema. Provenance in `Note.source` records `adapter: "xiaohongshu-dom"`, the query, and collection timestamp. Missing visible metrics remain `null`, never fabricated as zero.

Recognized user-facing errors are: blank keyword, unavailable local session/browser, user login or verification needed, no result cards within the bounded wait, and incompatible page structure. No error includes Cookie values, environment variables, page HTML, screenshots, or full browser logs.

## Testing and verification

- Unit tests cover adapter keyword validation, normalization of public-card DTOs, missing optional counts, and redaction-safe failures.
- API tests cover successful import through an injected fake adapter and 422 error mapping.
- Frontend tests cover enabled/disabled state, successful summary, and visible error feedback.
- One manual, local-only verification uses the already logged-in Xiaohongshu browser session with a harmless keyword. Its outcome is reported separately from automated tests.

## Acceptance criteria

1. A user can create a project, enter a keyword, import visible public Xiaohongshu search results, and see the imported count.
2. Imported notes appear in a project preview and are usable by the existing ranking endpoint.
3. Failed collection leaves no notes or metric snapshots from that request and provides a credential-safe message.
4. Fixed-sample import remains available for demo and offline development.
5. No credential, QR image, browser profile, or raw page snapshot is tracked in Git.
