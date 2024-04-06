import os
import subprocess
from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter


@pytest.fixture()
def cloned_directory(tmp_path):
    original_dir = os.getcwd()
    cloned_dir = cookiecutter(
        ".",
        no_input=True,
        output_dir=tmp_path,
    )

    os.chdir(cloned_dir)
    try:
        yield Path(cloned_dir)
    except:  # noqa
        os.chdir(original_dir)
        raise
    finally:
        os.chdir(original_dir)


@pytest.fixture()
def example_project_env(cloned_directory):
    env_path = Path(cloned_directory) / "env"

    # create a dummy git repository (needed for pre-commit)
    result = subprocess.run(["git", "init"], check=True, capture_output=True)
    assert result.returncode == 0, f"Failed to create git repository"

    # stage all files
    result = subprocess.run(["git", "add", "."], check=True, capture_output=True)
    assert result.returncode == 0, f"Failed to stage files"

    # create a new virtual environment
    result = subprocess.run(["python3", "-m", "venv", str(env_path)], check=True)
    assert result.returncode == 0, f"Failed to create virtual environment"

    # activate the virtual environment and install dependencies
    result = subprocess.run([
        "bash", "-c",
        f"source {env_path / 'bin' / 'activate'} && "
        "poetry update"
    ], check=True)
    assert result.returncode == 0, f"Failed to install dependencies"

    yield env_path


def test_template_pytest(example_project_env: Path):
    # run pytest in the virtual environment
    result = subprocess.run([
        "bash", "-c",
        f"source {example_project_env / 'bin' / 'activate'} && "
        "poetry run pytest"
    ], check=False)
    assert result.returncode == 0, f"Tests failed"


def test_template_precommit(example_project_env: Path):
    # run pre-commit in the virtual environment
    result = subprocess.run([
        "bash", "-c",
        f"source {example_project_env / 'bin' / 'activate'} && "
        "pre-commit install &&"
        "pre-commit run --all-files && ls -la"
    ], check=False)
    print(os.listdir())
    assert result.returncode == 0, f"pre-commit failed"
