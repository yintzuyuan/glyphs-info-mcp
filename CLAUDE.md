# Project Guidelines

> **Maintenance mode (since 2026-05)**: superseded by the `glyphs-reference` plugin. Only bug fixes are accepted.

## Language Policy

**Communication**: Use your preferred language during development conversations and discussions.

**Public Content**: All public-facing content MUST be in English (code comments, docstrings, commit messages, PRs, issues, documentation, release notes). This is an international open-source project.

## Project-Specific Gotchas

- **Closure factory late binding**: use the closure factory pattern when registering MCP resource handlers to avoid late binding issues.
- **Resource URI format**: `glyphs://resource-type/resource-id`.
- **SDK access**: reuse `SDKNativeAccessor` for file system operations; validate SDK paths at initialization and handle both bundle and standalone structures.
