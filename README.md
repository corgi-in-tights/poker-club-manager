# Poker Club Manager

Self-hostable site designed for poker club management, including checking in, blind timers, etc.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: GPLv3

## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## Contributing to the project

### Installation
1. Clone the repository
2. Ensure [uv](https://github.com/astral-sh/uv) is installed by running `uv --version`
3. Run `uv sync --group dev` to additionally install the dev dependencies
4. (Optional) add the pre-commit hook to force linting with `uv run pre-commit install`

This site is meant to be built and mounted onto Docker containers, though you may use `uv` directly if need be
1. Ensure [Docker][https://www.docker.com/] is installed and the daemon is running with `docker --version`
2. You may run the compose files manually, or use [just](https://github.com/casey/just)
3. `just build` to create the Docker image
4. Then, `just up` into `just logs`
5. Site should be running up at https://localhost:8000

### Running the project
In development, the database is initialized in an empty Postgres container, to fill it:
`just manage migrate`, then, `just manage seed`
If running with uv directly, you will need to provide envs manually, see /.envs/local for reference.

You may also want to create a superuser using `just manage createsuperuser`, follow the prompts.

I would recommend working without autosave, or the refresh can be funky (refreshes every save even if the save is invalid). Sometimes cache can be annoying for static files, work in incognito, that way you can close the window to clear the cache.

#### New to Django Templates?
Read:
- docs/template-syntax.md
- docs/views-template.md

### Type checks

Running type checks with mypy:

    uv run mypy poker_club_manager

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    uv run coverage run -m pytest
    uv run coverage html
    uv run open htmlcov/index.html

#### Running tests with pytest

    uv run pytest
