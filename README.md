# API

Version 2 \
2022-02-07

## Introduction / Purpose

The first purpose is to create a template for future developments of APIs using multiple languages and as a source for quick reference for syntax, workaround, and best practices, etc.
The second purpose is to create a WebUI to manage a RaspberryPi dedicated to downloading Torrents with the following features:
- List the system metrics, such as up-time, used storage, VPN status and data usage, and more,
- Start and stop the VPN connection and the Transmission (Torrent application) daemon,
- Reboot and halt the system,
- List, download, and delete files from the torrent directory.

![listener_screenshot](https://github.com/davift/API/blob/main/screenshot.png)

## Disclaimer

This code is a laboratory (PoC), not intended to be exposed directly to the public Internet or be used in production environment.

Read, customize, learn, and use it at your own risk because it has security risks:

- The code uses the modules to execute shell commands,
- It has multiple unauthenticated endpoints,
- By design, it binds on all interfaces,
- And there is no inputs validation/sanitization.

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
WorkingDirectory=/App
Environment="DYNAMIC_DNS=your-domain-here.duckdns.org"
ExecStart=/usr/bin/python3 /App/api.py
Restart=on-abort

[Install]
WantedBy=multi-user.target
```

The service configuration above executes the Python version of the application. \
To execute the **NodeJS** version install runtime by issuing:

```
sudo apt install nodejs -y
node -v
```

And replace the following file on the service configuration file:

```
ExecStart=/usr/bin/node /App/api.js
```

Same for **GOlang**, install the compiler:

```
sudo apt install golang
go --version
```

And replace the following file on the service configuration file:

```
ExecStart=/usr/bin/go run /App/api.go
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

Python scripts can eventually be compiled:

```
python -m py_compile api.py
```
