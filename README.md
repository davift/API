# API

Version 3 \
2023-01-15

## Introduction / Purpose

The purpose of this app is to provide a template for developing APIs using multiple languages. It serves as a resource for syntax, workarounds, and best practices.

Specifically, the app is a web-based tool for managing a Raspberry Pi dedicated to downloading Torrents. It includes features such as:
- displaying system metrics (e.g. uptime, used storage, VPN status),
- starting and stopping the VPN connection and Transmission (Torrent application) daemon,
- rebooting and shutting down the system,
- and listing, downloading, and deleting files being downloaded or completed.

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

This application is designed to run as a system service.

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

For **GOlang**, install the compiler:

```
sudo apt install golang
go --version
```

And replace the following file on the service configuration file:

```
ExecStart=/usr/bin/go run /App/api.go
```

For Ruby, install:

```
sudo apt  install ruby -y
ruby -v
```

And replace the following file on the service configuration file:

```
ExecStart=/usr/bin/ruby /App/api.rb
```

It assumes the /Torrent directory is where the Transmission is configured to place the downloaded files. It can be easily changed in the code.

## Starting

```
sudo systemctl daemon-reload
sudo systemctl start simpleapi.service
sudo systemctl enable simpleapi.service
```

## Moreover

Other commands such as restart or stop can be commanded as follows:

```
sudo systemctl restart simpleapi.service
sudo systemctl stop simpleapi.service
```

Python scripts can eventually be compiled:

```
python -m py_compile api.py
```
