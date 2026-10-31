---
kind: dependency_management
name: Python Dependency Management via requirements.txt
category: dependency_management
scope:
    - '**'
source_files:
    - requirements.txt
---

This repository uses a straightforward Python dependency management approach centered on a single `requirements.txt` file at the project root. All third-party packages are declared with exact version pins (using `==`) to ensure reproducible builds.

**System/approach used:**
- Standard `pip`-based dependency resolution through `requirements.txt`
- No virtual environment, lockfile (`requirements.lock`), or advanced tooling (Poetry, Pipenv, conda) is present
- Dependencies are pinned to specific versions for deterministic installs

**Key files and packages:**
- `requirements.txt` — sole manifest declaring all runtime dependencies including Streamlit (1.31.0), data/ML libraries (pandas 2.2.0, numpy 1.26.3, plotly 5.18.0, scikit-learn 1.4.0), utilities (reportlab 4.0.9, bcrypt 4.1.2, python-dotenv 1.0.0, psutil 5.9.8)
- Internal packages (`core`, `auth`, `ui`, `utils`) are imported directly as local modules; no package configuration files (`setup.py`, `pyproject.toml`, `Pipfile`) exist

**Architecture and conventions:**
- Flat dependency declaration: all packages listed in one file with strict `==` pinning
- No vendoring of third-party code; dependencies are expected to be installed into the active Python environment
- Local module imports use direct package paths (`from core.database import ...`, `from auth.authentication import ...`) without any packaging abstraction
- No private registry or proxy configuration is evident

**Conventions and constraints:**
- All third-party dependencies must be pinned to exact versions via `==` in `requirements.txt` (observed across all 10 entries)
- No separate dev/test dependency files are maintained; development and production dependencies are mixed in the same manifest
- There is no automated dependency update process, lockfile generation, or vulnerability scanning visible in the repository