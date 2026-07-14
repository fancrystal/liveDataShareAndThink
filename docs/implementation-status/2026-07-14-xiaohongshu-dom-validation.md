# Phase 1 Xiaohongshu DOM Collection Validation

Date: 2026-07-14

## Verified local flow

Using an existing local `xhs-cli` login session and the keyword `skincare`:

- The search page exposed 20 public result cards.
- The collector imported 20 notes into the local development database.
- Each card exposed a public like count.
- The existing ranking endpoint returned 20 ranked notes.

## Data fidelity rules

Search cards did not expose a reliable publication time, favorite count, comment count, or share count. Those values are stored as `null`; collection time is never substituted for publication time.

When publication time is unknown, Phase 1 ranking skips the velocity component and returns low confidence. The note remains eligible for relative engagement ranking.

## Safety boundary

The flow is user-triggered and read-only. It reuses the local `xhs-cli` session in memory only; it does not persist, log, expose, or commit Cookie values, and it does not publish, like, comment, save, or follow.

