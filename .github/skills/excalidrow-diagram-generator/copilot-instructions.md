  ## 📋 PRE-EDIT CHECKLIST

**Adherence to these rules is mandatory, ALWAYS check this file and follow these rules.**

---

## 🧭 Guiding Principles

1. **Simplicity First**: Use a minimal, pythonic approach. Avoid unnecessary complexity, libraries, or build tools.
2. **Security & Privacy by Design**: A strict Content Security Policy (CSP) and a "no tracking" policy are non-negotiable.
3. **Best practices**: Use modern APIs and do not support legacy code.

---

## ⚠️ Prohibited Practices

* ❌ **No Cookies or Tracking**: Do not use `document.cookie` or any form of user tracking/analytics. Use `localStorage` or `sessionStorage` for client-side state only.
* ❌ **No Inline Scripts or Styles**: All JavaScript and CSS must be in external files. This is enforced by our CSP.
* ❌ **No Legacy Code**: Do not use `var`, jQuery, or write code for Internet Explorer compatibility.
* ❌ **No Unsafe DOM Manipulation**: Avoid `innerHTML`. Use `textContent` for text and `createElement` for creating elements.

---

## 🔄 Version Control & Commit Workflow

This project uses a manual versioning process. It is your responsibility to keep it accurate.

**Manual Workflow:**

1. **Code**: Make your changes following all guidelines.

   * Increment the version number (`MAJOR.MINOR.PATCH`) for each file you changed.
   * Update the `timestamp` to the current Unix timestamp.
   * Schema example:

```json
{
  "nav": "1.0.X",
  "main": "1.0.X",
  "page-init": "1.0.X",
  "style": "1.0.X",
  "html": "1.0.X",
  "pages": {
    "home": "1.0.X",
    "about": "1.0.X",
    "credits": "1.0.X"
  },
  "timestamp": 1736448000
}
```

4. **Update `CHANGELOG.md`**:

   * Add a new entry under the current date.
   * Use SemVer headings and clear sections `Added`, `Changed`, `Fixed`.

```
## [1.2.3] - 2025-09-11
### Added
- video.js: keyboard shortcut “K” for pause

### Changed
- style.css: increased spacing scale

### Fixed
- nav.js: mobile overlap on iOS
```

5. **Commit**: Write a short, descriptive commit message (e.g., `fix(nav): correct mobile layout overlap`).

**Pre-commit checklist:**

* Browser tested, no console errors.
* Shortcuts intact.
* `versions.json` bumped correctly.
* `CHANGELOG.md` updated.

---

## 📐 Code Standards

### Python (3.11+)

- **Version**: New code MUST target Python 3.11+ and be type‑checked (mypy/pyright) in strict mode where possible. [web:2][web:5]
- **Modules**: Each module SHOULD expose a single `init()` function and a corresponding `teardown()` function as its public entry points. [web:1][web:3]
- **Typing**: All public functions, methods, and module‑level variables MUST have explicit type hints and return annotations. [web:2][web:8]
- **Immutability**: Configuration and settings objects MUST be defined as dataclasses with `@dataclass(frozen=True)` or equivalent immutable types (e.g. `NamedTuple`). [web:7][web:10][web:13]
- **Configuration Loading**: Runtime configuration MUST be loaded once at startup and passed explicitly (dependency injection), never accessed via mutable singletons. [web:3][web:8]
- **Error Handling (sync)**: Public APIs MUST catch and wrap low‑level exceptions in domain‑specific exceptions with clear messages; only specialized code may catch the generic `Exception`. [web:15]
- **Error Handling (async)**: All `async` entry points MUST be awaited via `asyncio.gather()` or similar with a top‑level `try/except` that logs and normalizes errors. [web:6][web:9][web:12]
- **Task Management**: Background tasks created with `asyncio.create_task()` MUST be tracked and awaited or explicitly cancelled; fire‑and‑forget tasks are forbidden. [web:6][web:9]
- **Logging**: User‑visible errors MUST be surfaced via structured logging using the standard `logging` module or an approved wrapper, never via `print()`. [web:3][web:11]
- **Style**: Code MUST follow PEP 8 (naming, formatting, imports) and pass the configured linters/formatters (e.g. Ruff, Black, isort) without warnings. [web:2][web:5][web:4]



### Documentation

* Use MkDocs for all functions and modules. Include `@param`, `@returns`, and `@throws` where applicable.

---

## 🔒 Security

* **Content Security Policy (CSP)**: Enforce strict `default-src 'self'`.
* **HTTP Headers**: Ensure server provides security headers, especially `X-Content-Type-Options: nosniff` and restrictive `Permissions-Policy`.
* **Asset Origin**: All assets must be same-origin. If external assets are used, they must include Subresource Integrity (SRI) hashes.