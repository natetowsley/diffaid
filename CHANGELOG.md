# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [0.2.1] - 2026-01-10
### Fixed
- **Reliable `.env` discovery for CLI installs**: DiffAid now loads `.env` starting from the user’s current working directory (and searches upward), instead of failing when installed/running from `site-packages`.
  - Resolves cases where `.env` existed in the project folder but `GEMINI_API_KEY` was still reported missing.

## [0.2.0] - 2026-01-10
### Added
- **`--json` flag**: Output raw JSON for automation, CI/CD integration, and scripting
  - Includes `strict_mode` and `exit_code` metadata when used with `--strict`
- **`--strict` flag**: Treat warnings as errors (exit code 1), useful for CI/CD pipelines
- **`--detailed` flag** (`-d`): Perform comprehensive line-by-line review with all suggestions
  - Default mode now provides high-level overview (5-10 key findings)
  - Detailed mode provides thorough analysis of all logical changes
- **`--version` flag (`-v`): Display version currently installed
- **`.env` file support**: Persistent API key configuration via python-dotenv
  - Users can create `.env` file with `GEMINI_API_KEY=your-key`
  - No need to set environment variable in every terminal session
- **Severity guidelines**: Explicit AI instructions for consistent classification
  - ERROR: Runtime crashes, security vulnerabilities, data corruption
  - WARNING: Performance issues, deprecated APIs, missing error handling
  - NOTE: Style improvements, refactoring opportunities, documentation
- **Dual prompt system**: Separate prompts for default and detailed modes
  - PROMPT_DEFAULT: High-level review, 5-10 impactful findings
  - PROMPT_DETAILED: Comprehensive review of all changes
- **Message quality guidance**: AI receives examples of good vs bad messages
  - Emphasis on descriptive messages with function/variable names
  - Reduces vague messages like "Fix this" or "Error here"

### Changed
- **Removed line numbers from findings**: `lines` field removed from Finding model
  - Git diffs don't provide reliable absolute line numbers
  - Focus on descriptive messages with function/class/variable names instead
  - Findings now show only file paths, not approximate line ranges
- **Improved API key error messages**: Better instructions for `.env` setup
- **CLI output refinements**: 
  - Removed line number display from findings output
  - Added "Strict Mode" indicator when warnings are treated as errors
  - Cleaner arrow symbol (→) for file paths
- **Enhanced CLI help text**: Updated examples to show new flags

### Fixed
- **Inconsistent severity classification**: AI now classifies issues consistently between default and detailed modes
- **Schema validation**: Prompts explicitly require lowercase severity values ("error", not "Error")

### Dependencies
- Added `python-dotenv` for `.env` file support
- Added `[tool.setuptools]` packages configuration to pyproject.toml

### Notes
- Version 0.1.0 mentioned "strict mode" in help text but didn't implement it - now fully functional
- Line numbers were inaccurate in 0.1.0 - removing them improves UX by avoiding misleading info

## [0.1.0] - 2026-01-06
### Added
- Initial release of **DiffAid**, an AI-assisted CLI that reviews **staged git diffs** before you commit. (Entry point: `diffaid` → `diffaid.cli:app`) 
- CLI implemented with **Typer** and **Rich** for readable terminal output (summary + colored findings + totals).
- Git integration to fetch staged changes via `git diff --staged`, including a check that `git` is installed and available in `PATH`.
- Gemini review engine using the **google-genai** client with a default model of `gemini-2.5-flash`.
- Strict JSON-based response contract for AI output, with parsing + schema enforcement using **Pydantic** (`ReviewResult` / `Finding`).
- Friendly error handling for common failures:
  - Not a git repo / git failures
  - Missing `GEMINI_API_KEY` (includes setup instructions)
  - AI returning malformed JSON or invalid schema
- Exit codes:
  - `0` = no errors found (including “no staged changes”)
  - `1` = at least one `error` finding
  - `2` = tool/runtime error (git or API issues)

### Tests
- Pytest coverage for:
  - CLI flows (no staged changes, errors, warnings-only, no-issues, and git failures) using Typer’s `CliRunner` + mocks.
  - Git diff retrieval behavior + error cases.
  - Pydantic model validation (invalid severity, empty/multiple findings).

### Notes
- The CLI help text mentions “warnings in strict mode,” but strict mode behavior is not implemented in v0.1.0.

[0.2.1]: https://github.com/natetowsley/diffaid/releases/tag/v0.2.1
[0.2.0]: https://github.com/natetowsley/diffaid/releases/tag/v0.2.0
[0.1.0]: https://github.com/natetowsley/diffaid/releases/tag/v0.1.0
