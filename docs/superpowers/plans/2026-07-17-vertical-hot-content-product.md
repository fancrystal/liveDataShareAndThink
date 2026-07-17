# Vertical Hot Content Product Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the workflow UI with one-click vertical hot-content research and an AI-generated five-page Xiaohongshu post package.

**Architecture:** A research service orchestrates the existing public search gateway, stores up to 20 cards, ranks visible evidence, and calls DeepSeek JSON analysis. A post-package service turns the report and user angle into structured copy plus local SVG poster pages.

### Task 1: Research contract and persistence

- [ ] Add a `VerticalResearchRequest`/`VerticalResearchReport` API contract, run collection with the supplied topic, rank up to 20 notes, and persist report metadata/evidence.
- [ ] Test collection-size cap, missing-date disclosure, and evidence-only output.

### Task 2: DeepSeek analysis and post package

- [ ] Add strict JSON DeepSeek prompts for hot reasons, replication checklist, caption/tags, and five page scripts; template fallback preserves a usable report.
- [ ] Render each script as an SVG 1080x1440 local asset; test JSON validation and renderer output.

### Task 3: One-screen product UI

- [ ] Add the vertical-topic/creation-angle form and a result screen containing Top20, AI report, replication checklist, caption, tags, and graphic page previews.
- [ ] Test one-click execution and visible AI result sections.

