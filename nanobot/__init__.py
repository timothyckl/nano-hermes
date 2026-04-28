"""
Nano Hermes - A lightweight personal AI assistant framework.
"""

from importlib.metadata import PackageNotFoundError, version as _pkg_version
from pathlib import Path
import tomllib

from nanobot.branding import APP_DISPLAY_NAME, APP_NAME, LEGACY_PACKAGE_NAME, LOGO, PACKAGE_NAME


def _read_pyproject_version() -> str | None:
    """Read the source-tree version when package metadata is unavailable."""
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    if not pyproject.exists():
        return None
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    return data.get("project", {}).get("version")


def _resolve_version() -> str:
    for package_name in (PACKAGE_NAME, LEGACY_PACKAGE_NAME):
        try:
            return _pkg_version(package_name)
        except PackageNotFoundError:
            continue
    # Source checkouts often import nanobot without installed dist-info.
    return _read_pyproject_version() or "0.1.5.post2"


__version__ = _resolve_version()
__logo__ = LOGO
__app_name__ = APP_NAME
__app_display_name__ = APP_DISPLAY_NAME

from nanobot.nanobot import Nanobot, RunResult

__all__ = ["Nanobot", "RunResult"]
