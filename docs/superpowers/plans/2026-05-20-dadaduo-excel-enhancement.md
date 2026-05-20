# Dadaduo Excel Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve and use the real Dadaduo Excel fields for import, scoring, filtering, display, and export.

**Architecture:** Extend the Python data model with Dadaduo-specific optional fields while keeping the original standard CSV path compatible. SQLite schema migration uses additive `ALTER TABLE` columns for existing local databases. Vue continues using Composition API and receives the enriched records from the existing JSON CLI.

**Tech Stack:** Python, pandas, SQLite, pytest, Vue 3, TypeScript, Tauri.

---

### Task 1: Backend Import And Scoring

**Files:**
- Modify: `app/config.py`
- Modify: `app/db.py`
- Modify: `app/importer.py`
- Modify: `app/scoring.py`
- Test: `tests/test_importer.py`
- Test: `tests/test_cli.py`

- [ ] Write failing tests for Dadaduo fields and settlement range parsing.
- [ ] Verify tests fail on missing fields.
- [ ] Add optional DB columns with additive migration.
- [ ] Normalize Dadaduo Excel columns into the new fields.
- [ ] Update scoring to use Dadaduo signals when rows have Dadaduo data.
- [ ] Verify Python tests pass.

### Task 2: Filtering And Export

**Files:**
- Modify: `app/filtering.py`
- Modify: `app/cli.py`
- Test: `tests/test_cli.py`

- [ ] Write failing tests for creator level, product count, like-fan ratio, and settlement filters.
- [ ] Add CLI filter arguments and filtering logic.
- [ ] Verify exported Excel contains filtered Dadaduo rows and new columns.

### Task 3: Desktop UI

**Files:**
- Modify: `desktop/src/types.ts`
- Modify: `desktop/src/App.vue`
- Modify: `desktop/src/components/CreatorTable.vue`
- Modify: `desktop/src/composables/useCreators.ts`

- [ ] Extend TypeScript record and filter types.
- [ ] Add Dadaduo filter controls.
- [ ] Update metrics and table columns to show real Dadaduo fields.
- [ ] Run `npm run build`.

### Task 4: Package

**Files:**
- Output: `desktop/src-tauri/target/release/bundle/macos/达人榜单.app`
- Output: `desktop/src-tauri/target/release/bundle/dmg/达人榜单_0.1.0_aarch64.dmg`

- [ ] Build backend sidecar if needed.
- [ ] Run `npm run tauri build`.
- [ ] Verify generated bundle paths.
