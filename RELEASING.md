# Release process

## Dev release (TestPyPI)

1. Bump `version` in `pyproject.toml` and `yapplotlib/__init__.py` (e.g. `0.2.0`)
2. Commit: `git commit -am "bump version to 0.2.0"`
3. Tag: `git tag v0.2.0-dev1`
4. Push: `git push origin develop && git push origin v0.2.0-dev1`
5. GitHub Actions publishes to [TestPyPI](https://test.pypi.org/project/yapplotlib/)
6. Verify: `uv run --with yapplotlib --index-url https://test.pypi.org/simple/ python -c "import yapplotlib; print(yapplotlib.__version__)"`

## Production release (PyPI)

1. Ensure version in `pyproject.toml` and `__init__.py` is correct and committed on `main`
2. Tag: `git tag v0.2.0`
3. Push: `git push origin main && git push origin v0.2.0`
4. GitHub Actions publishes to [PyPI](https://pypi.org/project/yapplotlib/)

## Auth

Uses OIDC trusted publishing — no tokens or secrets needed. Make sure the GitHub repo is configured as a trusted publisher in both PyPI and TestPyPI project settings.
