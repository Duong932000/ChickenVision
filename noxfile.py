"""Cross-platform task runner (uv-backed) — see CLAUDE.md section 1 for why nox over make."""

import nox

nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["lint", "fmt_check", "typecheck", "tests"]

PYTHON = "3.11"
LOCATIONS = ["src", "tests", "noxfile.py"]


def _uv_sync(session: nox.Session) -> None:
    session.run_install(
        "uv",
        "sync",
        "--group=dev",
        "--python",
        session.python,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )


@nox.session(python=PYTHON)
def lint(session: nox.Session) -> None:
    _uv_sync(session)
    session.run("ruff", "check", *LOCATIONS)


@nox.session(python=PYTHON)
def fmt_check(session: nox.Session) -> None:
    _uv_sync(session)
    session.run("ruff", "format", "--check", *LOCATIONS)


@nox.session(python=PYTHON)
def fmt(session: nox.Session) -> None:
    _uv_sync(session)
    session.run("ruff", "format", *LOCATIONS)


@nox.session(python=PYTHON)
def typecheck(session: nox.Session) -> None:
    _uv_sync(session)
    session.run("mypy", "src/chickenvision")


@nox.session(python=PYTHON)
def tests(session: nox.Session) -> None:
    _uv_sync(session)
    session.run("pytest", *session.posargs)
