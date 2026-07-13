# Presence

Home automation system for controlling doors electronically and logging accesses

## Setup

0. Install virtualenv. In debian derivates just run

```sh
sudo apt install python3-venv
```

1. Create a python3.4 virtualenv inside project's directory and activate it

```sh
python -m venv venv
source venv/bin/activate
```

2. Install the required modules

```sh
pip install -r requirements-dev.txt
```

3. Create the db. Default is sqlite, you will be asked to create a superuser

```sh
python manage.py migrate
```

4. You are now able to run the app. The webserver will be available at the specified port.

```sh
python manage.py runserver 8080
```

## Modules

- `gatecontrol` — Provides abstract interface and REST API for doors control and logging
- `hlcs` — Implementation based on the hardware used at Hacklab Cosenza

## Usage

The available doors (`internal` and `external`) are defined in the `GATES` dictionary in `presence/settings.py`.

List the doors and their state by running the server and querying it

```sh
python manage.py runserver 8080
curl http://localhost:8080/gates/
```

To issue the `open_gate` command send an authenticated POST request at the relative endpoint

```sh
curl -X POST http://localhost:8080/gates/internal/open/
```
