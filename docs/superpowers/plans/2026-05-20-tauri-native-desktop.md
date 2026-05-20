# Tauri Native Desktop App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package the existing creator ranking tool as a non-programmer-friendly Tauri desktop app for Windows and macOS, with a native UI, local SQLite storage, CSV import, filtering, and Excel export.

**Architecture:** Keep Python as the local data engine and expose it through a small CLI that reads/writes SQLite and emits JSON for the desktop app. Build the desktop shell in Tauri v2 with a Vue front end; Rust commands bridge the UI to the Python CLI and handle app-data paths, while the UI owns file picking, table rendering, filtering, and download flows.

**Tech Stack:** Python 3.12, SQLite, pandas, openpyxl, PyInstaller, Tauri v2, Rust, Vue 3, TypeScript, Vite, `@tauri-apps/plugin-dialog`, `@tauri-apps/plugin-shell`

---

### Task 1: Add a Python CLI backend

**Files:**
- Create: `app/cli.py`
- Modify: `app/importer.py`
- Modify: `app/db.py`
- Modify: `requirements.txt`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_cli_import_and_list(tmp_path):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_cli.py -v`
Expected: FAIL because `app.cli` and CLI commands do not exist yet

- [ ] **Step 3: Write minimal implementation**

```python
def main() -> int:
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/cli.py app/importer.py app/db.py tests/test_cli.py requirements.txt
git commit -m "feat: add python cli backend"
```

### Task 2: Scaffold the Tauri desktop app

**Files:**
- Create: `desktop/package.json`
- Create: `desktop/tsconfig.json`
- Create: `desktop/vite.config.ts`
- Create: `desktop/index.html`
- Create: `desktop/src/main.ts`
- Create: `desktop/src/App.vue`
- Create: `desktop/src/style.css`
- Create: `desktop/src/types.ts`
- Create: `desktop/src-tauri/Cargo.toml`
- Create: `desktop/src-tauri/tauri.conf.json`
- Create: `desktop/src-tauri/capabilities/default.json`
- Create: `desktop/src-tauri/src/lib.rs`

- [ ] **Step 1: Write the failing test**

```bash
npm run build
```

Expected: FAIL because the desktop app has not been scaffolded yet

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run build`
Expected: FAIL with missing entry/config files

- [ ] **Step 3: Write minimal implementation**

Create the Vue shell, Tauri config, dialog/shell wiring, and a minimal app bootstrap.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run build`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add desktop/
git commit -m "feat: scaffold tauri desktop app"
```

### Task 3: Wire the dashboard workflows

**Files:**
- Modify: `desktop/src/App.vue`
- Modify: `desktop/src/style.css`
- Create: `desktop/src/components/CreatorTable.vue`
- Create: `desktop/src/composables/useCreators.ts`
- Modify: `desktop/src-tauri/src/lib.rs`

- [ ] **Step 1: Write the failing test**

```bash
npm run build
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run build`
Expected: FAIL until the table, filters, import, and export flow are connected

- [ ] **Step 3: Write minimal implementation**

Connect import file dialog, CSV import command, refresh, filters, and Excel export.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run build`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add desktop/src desktop/src-tauri
git commit -m "feat: connect desktop workflows"
```

### Task 4: Update docs and packaging guidance

**Files:**
- Modify: `README.md`
- Modify: `requirements.txt`
- Create: `scripts/build_backend.py`
- Create: `desktop/README.md` (optional if needed)

- [ ] **Step 1: Write the failing test**

```bash
python -m pytest -q
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest -q`
Expected: FAIL if docs-related code paths or build helpers are missing

- [ ] **Step 3: Write minimal implementation**

Document Windows/macOS install, Python sidecar build, and Tauri build steps.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add README.md requirements.txt scripts/build_backend.py
git commit -m "docs: add tauri packaging guidance"
```
