# API

Version 1 \
2021-12-12

## Introduction / Purpose

The first purpose is to create a template for future developments of APIs using multiple languages and as a source for quick reference for syntax, workaround, and best practices, etc.
The second purpose is to create a WebUI to manage a RaspberryPi dedicated to downloading Torrents with the following features:
- List the system metrics, such as up-time, used storage, VPN status and data usage, and more,
- Start and stop the VPN connection and the Transmission (Torrent application) daemon,
- Reboot and halt the system,
- List, download, and delete files from the torrent directory.

## Installation

It is recommended to clone this repo then rename the directory to `/App`:

```
git clone git@github.com:davift/API.git
sudo mv API /App
```

This application is designed to run as a service in the syste.

```
sudo nano /etc/systemd/system/simpleapi.service
```

Paste the following content:

```
[Unit]
Description=Python API on port 80
After=network.target

[Service]
Type=simple
WorkingDirectory=/Torrent
ExecStart=/usr/bin/python3 /App/api.py
Restart=on-abort

[Install]
WantedBy=multi-user.target
```

It assumes the /Torrent directory is where the Transmission is configured to place the downloaded files but these both locations can be changed in `/App/api.py`:

```
 Line #32                         app = '/App'
 Line #33                         path = '/Torrent'
```

## Execution

```
sudo systemctl daemon-reload
sudo systemctl start simpleapi.service
sudo systemctl enable simpleapi.service
```

## Additionals

Other commands such as restart or stop can be commanded as follows:

```
sudo systemctl restart simpleapi.service
sudo systemctl stop simpleapi.service
```

