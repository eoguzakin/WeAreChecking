from pathlib import Path


def project_root(start=None):
    location = Path(start or Path.cwd()).resolve()
    if location.is_file():
        location = location.parent
    for candidate in (location, *location.parents):
        marker = candidate / "pyproject.toml"
        if marker.exists() and 'name = "wearechecking"' in marker.read_text(encoding="utf-8"):
            return candidate
    raise FileNotFoundError("Open the WeAreChecking folder and run the command from there.")


def prepare_dirs(root=None):
    root = Path(root) if root else project_root()
    for name in (".cache/fastf1", "data/snapshots", "reports/predictions"):
        (root / name).mkdir(parents=True, exist_ok=True)
    return root
