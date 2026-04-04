# Release process

1. Bump `version` in `pyproject.toml` and `yapplotlib/__init__.py`
2. Commit: `git commit -am "bump version to X.Y.Z"`
3. Tag: `git tag vX.Y.Z` — must be exact semver (`vX.Y.Z`), no suffix
4. Push: `git push origin main && git push origin vX.Y.Z`
5. GitHub Actions publishes to [PyPI](https://pypi.org/project/yapplotlib/)

## Auth

Uses OIDC trusted publishing — no tokens or secrets needed. The GitHub repo is configured as a trusted publisher in PyPI project settings.