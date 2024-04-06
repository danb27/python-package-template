import os
import subprocess
from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter


@pytest.fixture()
def example_project_dir(tmp_path) -> Path:
    template_path_os = cookiecutter(
        ".",
        no_input=True,
        output_dir=tmp_path,
    )
    return Path(template_path_os)


def test_template(example_project_dir: Path):
    env_path = example_project_dir / "env"

    os.chdir(example_project_dir)

    # create a new virtual environment
    result = subprocess.run(["python3", "-m", "venv", str(env_path)], check=True, capture_output=True)
    assert result.returncode == 0, f"Failed to create virtual environment"

    # activate the virtual environment and install dependencies
    result = subprocess.run([
        "bash", "-c",
        f"source {env_path / 'bin' / 'activate'} && "
        "poetry update"
    ], check=True)
    assert result.returncode == 0, f"Failed to install dependencies"

    # run pytest in the virtual environment
    result = subprocess.run([
        "bash", "-c",
        f"source {env_path / 'bin' / 'activate'} && "
        "poetry run pytest"
    ], check=False)
    assert result.returncode == 0, f"Tests failed"
