"""Run once: py -3.13 bootstrap.py. No environment activation is needed."""
from pathlib import Path
import os
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent
ENV = ROOT / ".venv"
PYTHON = ENV / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")


def main():
    if not (3, 12) <= sys.version_info[:2] < (3, 15):
        raise SystemExit("Python 3.12, 3.13 veya 3.14 gerekiyor.")
    if not PYTHON.exists():
        venv.EnvBuilder(with_pip=True).create(ENV)
    lock = ROOT / ("requirements-windows-py313.lock" if sys.platform == "win32"
                   and sys.version_info[:2] == (3, 13) else "requirements.txt")
    subprocess.run([str(PYTHON), "-m", "pip", "install", "-r", str(lock)],
                   cwd=ROOT, check=True)
    subprocess.run([str(PYTHON), "-m", "pip", "install", "-e", ".[dev]"],
                   cwd=ROOT, check=True)
    # Keep Jupyter files local, including in automation without a home directory.
    kernel_env = os.environ.copy()
    for name, relative in {
        "JUPYTER_CONFIG_DIR": ".cache/jupyter/config",
        "JUPYTER_DATA_DIR": ".venv/share/jupyter",
        "JUPYTER_RUNTIME_DIR": ".cache/jupyter/runtime",
    }.items():
        kernel_env[name] = str(ROOT / relative)
        (ROOT / relative).mkdir(parents=True, exist_ok=True)
    subprocess.run([str(PYTHON), "-m", "ipykernel", "install", "--sys-prefix",
                    "--name", "wearechecking", "--display-name", "WeAreChecking (.venv)"],
                   cwd=ROOT, check=True, env=kernel_env)
    subprocess.run([str(PYTHON), "-m", "wearechecking", "doctor"], cwd=ROOT, check=True)
    print("Hazır. VS Code: Select Kernel > Python Environments > .venv")


if __name__ == "__main__":
    main()
