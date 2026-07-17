# Phase 1 Closeout Design

## Goal

Complete the usable Phase 1 Xiaohongshu content-attraction loop: Docker uses DeepSeek when available and safely falls back to templates, evidence-based content insights accompany rankings, and the UI lets a single user reopen projects and inspect collection history.

## DeepSeek Runtime

Docker passes `GENERATION_PROVIDER`, `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, and `DEEPSEEK_MODEL` from `.env` to the API without exposing them to the browser bundle. A `FallbackGenerator` wraps the selected DeepSeek generator. It attempts DeepSeek first and uses `TemplateGenerator` only for a `DeepSeekGenerationError`; stored draft versions identify the actual generator used. Explicit `GENERATION_PROVIDER=template` remains template-only.

## Evidence-Based Insight

After ranking, deterministic extraction reads only collected `Note.title`, `Note.content`, `content_type`, and visible metric values. It produces an `content_attraction_patterns` insight with: repeated title-hook patterns, content-format distribution, three reusable content angles, confidence, and evidence note identifiers. It never invents unavailable publication times or hidden engagement metrics. The ranking API returns this alongside its relative-performance insight, and the page renders a compact “内容引流洞察” card with linked source notes.

## Project and Collection History

Existing `GET /api/projects` is wired into the UI as a project selector. A new `GET /api/projects/{id}/collections` returns runs in reverse start time with adapter, keyword, timestamps, status, and inserted counts. Opening a project refreshes notes and collection history. The interface labels each note's collection keyword/time and shows missing public fields as “未公开”.

## Proxy Status

The local proxy adds a token-protected health endpoint. The Docker API exposes its configured proxy state through `GET /api/collection-proxy/status`; it does not make a live request or disclose tokens. The page displays “需要启动本地代理” when the Docker configuration is absent and “本地代理已配置” when present, retaining the existing safe failure prompt for unreachable proxy.

## Tests

- generator factory tests prove DeepSeek-first fallback and template-only behavior;
- analysis tests prove derived hook/format/angle evidence uses known note data;
- collection API tests prove ordered run history;
- proxy status tests prove no token value is returned;
- frontend tests prove project reopening, history display, and generator/proxy labels;
- all existing tests and production builds remain green.

## Out of Scope

No note-detail crawl, no hidden metrics, no multi-user auth, no automatic background installation of the proxy, and no livestream replay analysis.

