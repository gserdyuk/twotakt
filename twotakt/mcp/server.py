import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("twotakt")

TWOTAKT_MANIFEST = "twotakt.json"
MODEL_DIR = "model"
MODEL_FILES = ["resources.py", "activities.py", "sim_config.py"]


@mcp.tool()
def load_workspace(path: str) -> dict:
    """Load a twotakt workspace. Returns manifest and model Python files."""
    workspace = Path(path)

    if not workspace.is_dir():
        raise ValueError(f"Directory not found: {path}")

    manifest_path = workspace / TWOTAKT_MANIFEST
    if not manifest_path.exists():
        raise ValueError(f"Not a twotakt workspace (no {TWOTAKT_MANIFEST}): {path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    model_dir = workspace / MODEL_DIR
    model_files = {}
    if model_dir.exists():
        for py_file in model_dir.glob("*.py"):
            model_files[py_file.name] = py_file.read_text(encoding="utf-8")

    return {
        "manifest": manifest,
        "model_files": model_files,
    }


@mcp.tool()
def save_workspace(path: str, manifest: dict, model_files: dict) -> dict:
    """Save a twotakt workspace. Writes manifest and model Python files to disk."""
    workspace = Path(path)
    workspace.mkdir(parents=True, exist_ok=True)

    manifest_path = workspace / TWOTAKT_MANIFEST
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    model_dir = workspace / MODEL_DIR
    model_dir.mkdir(exist_ok=True)

    (model_dir / "__init__.py").touch()

    written = []
    for filename, content in model_files.items():
        if not filename.endswith(".py"):
            raise ValueError(f"Only .py files allowed in model/: {filename}")
        (model_dir / filename).write_text(content, encoding="utf-8")
        written.append(filename)

    return {"ok": True, "path": str(workspace.resolve()), "written": written}


def main():
    mcp.run()


if __name__ == "__main__":
    main()
