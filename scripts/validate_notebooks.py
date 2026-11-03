"""Validate structure, or execute exercises without solving them."""
from pathlib import Path
import argparse
import os
ROOT = Path(__file__).resolve().parents[1]
for name, relative in {
    "JUPYTER_CONFIG_DIR": ".cache/jupyter/config",
    "JUPYTER_DATA_DIR": ".venv/share/jupyter",
    "JUPYTER_RUNTIME_DIR": ".cache/jupyter/runtime",
    "IPYTHONDIR": ".cache/ipython",
    "MPLCONFIGDIR": ".cache/matplotlib",
}.items():
    os.environ.setdefault(name, str(ROOT / relative))
    Path(os.environ[name]).mkdir(parents=True, exist_ok=True)
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--structure-only", action="store_true")
    args = parser.parse_args()
    output = ROOT / "reports/executed"
    output.mkdir(parents=True, exist_ok=True)
    for source in sorted((ROOT / "notebooks").glob("*.ipynb")):
        notebook = nbformat.read(source, as_version=4)
        nbformat.validate(notebook)
        if not args.structure_only:
            NotebookClient(notebook, timeout=120, kernel_name="wearechecking",
                           resources={"metadata": {"path": str(ROOT)}},
                           allow_errors=False).execute()
            nbformat.write(notebook, output / source.name)
            html, _ = HTMLExporter(template_name="lab").from_notebook_node(notebook)
            (output / source.with_suffix(".html").name).write_text(html, encoding="utf-8")
        print(f"OK: {source.name} ({'structure' if args.structure_only else 'executed'})")
    print("Pending student exercises remain pending; this is not milestone completion.")

if __name__ == "__main__":
    main()
