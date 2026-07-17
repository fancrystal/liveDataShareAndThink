# Vertical Hot Content Product Design

## Product Contract

The Phase 1 home screen accepts a vertical topic such as “普拉提产后修复”. One action runs research and returns: (1) up to 20 current publicly visible Xiaohongshu search candidates, (2) a DeepSeek-written hot-content report explaining what is hot, evidence, probable reasons, and replication actions, and (3) a five-page, directly usable Xiaohongshu graphic-post package for a user-supplied content angle.

## Truthful Data Boundary

“Today” means the report's collection date. Search cards that expose no publication date are reported as unknown; the product must not claim they were posted today. Ranking is based only on visible metrics and collection-time cohort comparisons.

## AI Flow

DeepSeek receives structured, public-card evidence only. It returns strict JSON for report sections and a five-page graphic-post script: cover, pain point, method, evidence/disclaimer, call to action. A local SVG renderer turns these scripts into shareable 1080x1440 poster pages. DeepSeek’s public API is used for chat/JSON, not assumed to generate imagery.

## Main Interface

One “赛道爆款研究” form has a vertical-topic field, optional creation angle, and one submit button. Results appear in order: Top20 source list, AI hot-content report, then five graphic pages plus caption/tags. Project/database details remain secondary history, not the primary workflow.

