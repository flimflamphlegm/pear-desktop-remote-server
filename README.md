# Pear Desktop Remote Server

A small macOS web remote for Pear Desktop / YouTube Music.

## Demo

![Pear Desktop Remote demo](docs/assets/demo.jpeg)

## Run manually

```sh
python3 server.py
```

`server.py` remains a compatibility entry point. New installations use `main.py`.

Open the printed LAN URL on a phone or another device on the same network.

## Install at login

```sh
chmod +x install.sh
./install.sh
```

The script creates a LaunchAgent at `~/Library/LaunchAgents/com.user.ytremote.plist`.
Logs are written to `ytremote.log` and `ytremote.err` in the project directory.

## Project structure

```text
.
├── docs/assets/demo.jpeg
├── install.sh
├── main.py
├── server.py
├── src/pear_remote/
│   ├── config.py
│   ├── controls.py
│   ├── macos_control.py
│   ├── main.py
│   ├── net_utils.py
│   ├── pear_client.py
│   ├── pear_remote_handler.py
│   ├── templating.py
│   └── index.html
└── tests/
```

## Tests

```sh
python3 -m unittest discover -s tests
```

The server requires macOS for system-volume control and a running Pear Desktop instance for playback operations.
