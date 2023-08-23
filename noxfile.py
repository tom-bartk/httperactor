import pathlib
import nox

SOURCE_DIR = "src/httperactor"
PYTHON_DEFAULT_VERSION = "3.11"
DEPENDENCIES = ["httpx", "pydepot"]
LINT_DEPENDENCIES = [
    "black==23.7.0",
    "mypy==1.5.0",
    "ruff==0.0.284",
]
RESULTS_DIR = pathlib.Path('./reports').resolve()
RESULTS_DIR.mkdir(exist_ok=True)

@nox.session(python=PYTHON_DEFAULT_VERSION)
def test(session: nox.Session) -> None:
    session.install(*DEPENDENCIES)
    session.install("pytest", "pytest-asyncio", "pytest-cov")
    output_file = RESULTS_DIR / "test.xml"
    session.run("pytest", "--junit-xml", str(output_file), "--cov=src.httperactor", "--cov-report=term-missing")
    session.notify("coverage")


@nox.session(python=PYTHON_DEFAULT_VERSION)
def coverage(session: nox.Session) -> None:
    session.install("coverage[toml]")
    output_file = RESULTS_DIR / "coverage.xml"
    session.run("coverage", "xml", "-o", str(output_file))
    session.run("coverage", "erase")


@nox.session(python=PYTHON_DEFAULT_VERSION)
def lint(session: nox.Session) -> None:
    session.install(*DEPENDENCIES)
    session.install(*LINT_DEPENDENCIES)
    lint_output = RESULTS_DIR / "lint.xml"
    session.run("ruff", "check", "--format", "junit", "--output-file", str(lint_output), "src")

    session.run("black", "--check", "tests", "src/httperactor")

    typing_output = RESULTS_DIR / "typing.xml"
    session.run("mypy", "--junit-xml", str(typing_output), SOURCE_DIR)
