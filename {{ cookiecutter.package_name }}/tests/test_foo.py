from {{ cookiecutter.package_slug }} import bar


def test_bar():
    assert bar() == 1
