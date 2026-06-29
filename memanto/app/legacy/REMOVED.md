# Legacy / Dead-Code Dump

This folder is a **standalone dump for dead code**. Nothing in the active
codebase imports from `memanto/app/legacy/`, and this folder is **excluded from
CI** (ruff lint, ruff format, and mypy — see `pyproject.toml`). Files here may
have broken imports or reference symbols that no longer exist; that is expected.
Do not wire anything in `app/`, `cli/`, or the integrations to this folder.

Last cleanup: **2026-06-29**.

---

## 1. Orphaned "trust" machinery removed from active code

These fields/methods were schema-only — defined but **never populated or called**
by any live write/read flow (the write path uses an `"MVP direct store"` shortcut
that bypasses validation). Conflicts are actually handled by outright deletion via
the `memanto conflicts` CLI, not by supersession flags. All of the following were
deleted:

**`memanto/app/core.py`**
- Fields on `MemoryRecord`: `superseded_by`, `supersedes`, `validated_at`,
  `validation_count`, `contradiction_detected`.
- Methods: `compute_confidence()`, `validate()`, `mark_superseded()`,
  `detect_contradiction()`, `trust_score()`.
- The entire `ValidationPolicy` class (`validate_memory`,
  `_validate_critical_memory`, `make_provisional`) — fully bypassed by the
  write service.
- The serialization of the removed fields in `to_moorcheh_document()`.

**`memanto/app/services/memory_read_service.py`**
- Extraction + formatting of `validation_count`, `contradiction_detected`,
  `superseded_by`, `supersedes`, `validated_at` in `_format_memory_item()`.
- The dead "skip if superseded" branch in `search_as_of()` (depended on
  `superseded_by`, which is never written).
- The large commented-out `compute_confidence()` / `trust_score()` block.

**`memanto/app/models/__init__.py`**
- The five trust fields on the `MemoryItem` response model.
- The unused `SupersedeRequest` model (imported nowhere).

**`memanto/app/routes/memory.py`**
- Dead `trust_score()` comment block in the `remember` response.

**Consistency-only edits (kept in sync with the removed fields):**
- `memanto/app/ui/static/index.html` — removed the `contradiction_detected`
  and `validation_count` table badges.
- `docs/GETTING_STARTED.md` — removed the two fields from the example response.
- `sdks/typescript/openapi.json` — removed the five properties from the
  `MemoryItem` schema.

The live trust signals that **remain** are `confidence`, `provenance`,
`created_at`/`updated_at`, `status`, and TTL (`expires_at`/`ttl_seconds`).

---

## 2. Entirely-unused files moved here

Each was verified to have **no inbound import from active code** before moving:

| Moved from | Moved to | Why |
|---|---|---|
| `memanto/app/utils/idempotency.py` | `legacy/idempotency.py` | `IdempotencyHandler` / `handle_write_idempotency` never imported anywhere |
| `memanto/app/utils/tracing.py` | `legacy/tracing.py` | trace span/decorator helpers never imported |
| `memanto/app/utils/safe_deletion.py` | `legacy/safe_deletion.py` | `SafeDeletion.perform_safe_deletion` never imported |
| `memanto/app/models/phase_d.py` | `legacy/phase_d.py` | Phase-D models never imported |
| `memanto/app/models/universal_endpoints.py` | `legacy/universal_endpoints_models.py` | referenced only by the already-dead legacy `universal_*` files (renamed to avoid colliding with the existing `legacy/universal_endpoints.py` routes file) |

Pre-existing dead files already in this folder (untouched): `context.py`,
`context_summarization_service.py`, `memory.py`, `memory_validation_service.py`,
`universal_endpoints.py`, `universal_services.py`.

---

## 3. Multi-scope / namespace cleanup (2026-06-29)

The live app only ever uses `scope_type="agent"` — every memory namespace is
`memanto_agent_{agent_id}`. The broader multi-scope abstraction
(`user`/`workspace`/`session`/`project`/`task`) was exercised only by dead code.

**`ScopeType` narrowed to `Literal["agent"]`** in `constants.py` (and
`VALID_SCOPE_TYPES = {"agent"}`). The agent-only scope resolution in
`memory_read_service.generate_answer()` / `_get_search_namespaces()` was
simplified accordingly (they always build an `agent` scope now).

**Removed dead namespace machinery:**
- `routes/namespaces.py` → moved to `legacy/namespaces.py`. Its router was
  **never mounted** in `main.py` (only `health`, `sessions`→`memory`, and the
  Web UI are mounted) — the whole file was unreachable.
- `models/__init__.py`: removed `NamespaceCreateRequest`, `NamespaceResponse`,
  `NamespaceListResponse` (imported only by the dead route).
- `NamespaceService`: removed `create_namespace()`, `delete_namespace()`,
  `namespace_exists()` (used only by the dead route + the dead
  `_ensure_namespace`). Kept `list_namespaces()` — the live search path uses it.
- `MemoryWriteService`: removed the uncalled `_ensure_namespace()` and its
  lazy `namespace_service` property.
- `MemoryReadService.search_multi_scope()`: removed. Called only from the dead
  `legacy/memory.py`, and it had a broken `from memanto.memanto.app.constants`
  import (double `memanto`) proving it never ran.

`scope_type` / `scope_id` themselves remain — they are load-bearing (every
namespace is derived from them via `MemoryScope.to_namespace()`).

---

## Verification (post-cleanup)

- `pytest tests/` → **191 passed**
- `ruff check .` → clean
- `ruff format --check .` → clean
- `mypy memanto` → no issues (legacy excluded)
- `import memanto.app.main` / `import memanto.cli.main` → OK
