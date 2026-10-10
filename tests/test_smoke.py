"""Smoke test proving the package imports and the test runner is wired up."""

import library


def test_package_has_version():
    assert library.__version__
