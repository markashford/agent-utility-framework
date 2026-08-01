# Contributing

Thanks for contributing to Energent Agents.

## Development setup

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements-dev.txt`.
3. Run tests with `python3 -m pytest -q` before opening a PR.

## Pull request guidelines

- Keep pull requests focused and small when possible.
- Add or update tests for behavior changes.
- Update README for user-facing changes.
- Use clear conventional commit messages (`feat:`, `fix:`, `docs:`, `test:`).

## Quality checks

- All tests must pass locally.
- New features should include at least one automated test when practical.
- Avoid introducing required external services in unit tests.
