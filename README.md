# Pear Desktop Remote Server

A small macOS web remote for Pear Desktop / YouTube Music.

## Run manually

```sh
python3 server.py
```

`server.py` remains as a compatibility entry point. New installs use `main.py`.

Open the printed LAN URL on a phone or another device on the same network.

## Install at login

There is one installer script. The old `setup_startup.sh` was redundant and has been removed.

```sh
chmod +x install.sh
./install.sh
```

The script creates a LaunchAgent at `~/Library/LaunchAgents/com.user.ytremote.plist`.
Logs are written to `ytremote.log` and `ytremote.err` in the project directory.

## Project structure

- `main.py` — application entry point and restart loop.
- `pear_remote_handler.py` — HTTP routes.
- `pear_client.py` — Pear Desktop API client and progress normalization.
- `controls.py` — playback/volume action dispatch.
- `macos_control.py` — macOS volume integration.
- `templating.py` — configuration injection into `index.html`.
- `config.py` — all tunable settings.

## Tests

```sh
python3 -m unittest discover -s tests
```

The server requires macOS for system-volume control and a running Pear Desktop instance for playback operations.
