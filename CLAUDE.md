# Project Guidelines

## Language Policy

**Communication**: Use your preferred language during development conversations and discussions.

**Public Content**: All public-facing content MUST be in English:

- Code comments and docstrings
- Commit messages
- Pull request titles and descriptions
- Issue titles and descriptions
- Documentation files (README.md, etc.)
- Code review comments on GitHub
- Release notes

**Rationale**: This is an international open-source project. English ensures accessibility for the global developer community.

## Development Standards

### Mandatory TDD

- **No code without tests** - This is non-negotiable
- Write failing tests first (Red)
- Write minimum code to pass (Green)
- Refactor while keeping tests green
- Test coverage must be >85%

### Code Quality

- Follow PEP8 style guidelines
- Use `pathlib` for all file operations
- Never hardcode paths - use environment variables or relative paths
- All public functions/methods must have type hints
- All public functions/methods must have docstrings

### Git Workflow

- Create feature branches from `main`
- Branch naming: `type/issue-number-description` (e.g., `feat/37-add-samples`)
- All changes must go through Pull Requests
- Never use `git merge` directly - merge via GitHub PR
- Link PRs to Issues using "Closes #XX" or "Fixes #XX"

### Testing

- Use pytest for all tests
- Test file naming: `test_*.py`
- Run tests: `pytest`
- Check coverage: `pytest --cov=src --cov-report=term-missing`
- Verify types: `mypy src`
- Lint code: `ruff check .`

### Error Handling

- Use specific exception types (not bare `Exception`)
- Provide actionable error messages
- Log errors with appropriate levels (debug/info/warning/error)
- Never silently swallow exceptions
- Include context in error messages

## Project-Specific Guidelines

### MCP Resource Development

- Follow existing patterns from PR #35 (Python Templates) and PR #36 (Xcode Templates)
- Use closure factory pattern to avoid late binding issues
- Resource URIs format: `glyphs://resource-type/resource-id`
- Resource handlers must return formatted Markdown
- Cache resource scans for performance

### SDK Integration

- Reuse `SDKNativeAccessor` for file system operations
- Validate SDK paths at initialization
- Handle both bundle and standalone structures
- Extract README content when available
- Support search functionality for resources
