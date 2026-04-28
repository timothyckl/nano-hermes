"""
Nano Hermes - A lightweight personal AI assistant framework.
"""

from importlib.metadata import PackageNotFoundError, version as _pkg_version
from pathlib import Path
import tomllib

APP_NAME = "nano-hermes"
APP_DISPLAY_NAME = "Nano Hermes"
APP_DIR_NAME = ".nano-hermes"
PACKAGE_NAME = "nano-hermes"
REPOSITORY_URL = "https://github.com/timothyckl/nano-hermes"
LOGO = "🪽"


def _read_pyproject_version() -> str | None:
    """Read the source-tree version when package metadata is unavailable."""
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    if not pyproject.exists():
        return None
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    return data.get("project", {}).get("version")


def _resolve_version() -> str:
    try:
        return _pkg_version(PACKAGE_NAME)
    except PackageNotFoundError:
        # Source checkouts often import nano_hermes without installed dist-info.
        return _read_pyproject_version() or "0.1.5.post2"


__version__ = _resolve_version()
__logo__ = LOGO
__app_name__ = APP_NAME
__app_display_name__ = APP_DISPLAY_NAME

from nano_hermes.nano_hermes import NanoHermes, RunResult

__all__ = ["NanoHermes", "RunResult"]
