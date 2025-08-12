from importlib.metadata import version


def test_package_version_string() -> None:
    assert isinstance(version("cb-adv-bot"), str)
