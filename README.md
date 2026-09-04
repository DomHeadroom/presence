# Presence

Home automation system for controlling doors electronically and logging accesses

## Setup

0. Install [uv](https://docs.astral.sh/uv/getting-started/installation/). On DietPi:

```sh
dietpi-software install 217
```

or with the official installer (no root required):

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

1. Install the required modules. This creates a `.venv` with a Python 3.12+ interpreter (developed on 3.14) and installs the project plus dev tooling.

```sh
uv sync
```

On the Raspberry Pi that drives the real gates, sync the `prod` extra instead. This pulls in `rpi-lgpio`, `mysqlclient` and `gunicorn`; `rpi-lgpio` requires kernel >= 5.11 and must not be installed alongside the classic `RPi.GPIO`.

```sh
uv sync --extra prod
```

2. Create the db. Default is sqlite, you will be asked to create a superuser

```sh
uv run python src/manage.py migrate
```

3. You are now able to run the app. The webserver will be available at the specified port.

```sh
uv run python src/manage.py runserver 8080
```

## Modules

- `gatecontrol` — Provides abstract interface and REST API for doors control and logging
- `hlcs` — Implementation based on the hardware used at Hacklab Cosenza

## Usage

The available doors (`internal` and `external`) are defined in the `GATES` dictionary in `src/presence/settings.py`.

List the doors and their state by running the server and querying it

```sh
uv run python src/manage.py runserver 8080
curl http://localhost:8080/gates/
```

To issue the `open_gate` command send an authenticated POST request at the relative endpoint

```sh
curl -X POST http://localhost:8080/gates/internal/open/
```
