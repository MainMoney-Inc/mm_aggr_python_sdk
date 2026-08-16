# Conventions

- Python 3.11+ (develop on 3.13/3.14). Type hints and mypy-compatible code.
- Package layout: `src/mm_aggr/`. uv is the primary toolchain; Poetry is supported.
- pytest, ruff. No empty `except:` swallows.
- Currency: never mix amounts across currencies.
