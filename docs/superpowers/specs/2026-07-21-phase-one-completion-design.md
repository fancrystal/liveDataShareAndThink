# Phase 1 Completion Design

## Goal

Complete the single-user Xiaohongshu content-attraction workflow: each research request produces a current-keyword Top20, a Chinese-only evidence-based AI report, and five downloadable 1080×1440 PNG post images with copy-ready caption and tags.

## Data boundary

Each research call creates one collection run. Rankings used by that response are limited to notes whose source query and most recent collection timestamp match that run; prior project history is not mixed into the daily result. “Today” means the collection date, not an unsupported claim about each note's publication date.

## AI boundary

Both DeepSeek requests receive public title, visible content, visible metrics, collection date, score and source URL. The reporter and post packager require simplified-Chinese text, reject English letters, validate their JSON schema, and retry once with a correction instruction before returning a Chinese API error.

## Deliverable images

The browser renders each generated page with local Canvas text layout at 1080×1440. Users can preview all pages, download an individual PNG or all five PNGs, and copy the complete caption plus hashtags. No image-generation API or new secret is required.

## Out of scope

This work does not add automatic publishing, CAPTCHA bypassing, global Xiaohongshu rankings, comments/detail-page crawling, scheduled jobs, or Phase 2 live-stream review.
