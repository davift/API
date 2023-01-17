# API

Version 3 \
2023-01-15

## Introduction

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

## Handling Parallel Connections

- Golang is meant for multi-thread processing and is capable of hadle as much parallel connections as computing resources are available in the server. This is the best oiption for production application.
- The Python and Ruby versions in this repo work similarly to the Golang, limited only by the server's resources.
- NoseJS in another hand, by default is capable of hadling 5-6 parallel connections. It requires some tweaks to spin up multiple workers that would handle a single connection per node using the modules **"cluster"** or **"pm2"**. Keep in mind, the NodeJS version implementation in this repo uses execSync (synchronous), not exec (asynchronous).

### NodeJS Cluster - Example

```
var cluster = require('cluster');
var http = require('http');

if (cluster.isMaster) {
  for (var i = 0; i < 100; i++) {
    cluster.fork();
  }
} else {
  var server = http.createServer(function (req, res) {
    res.writeHead(200);
    res.end('Hello World\n');
  });

  server.listen(80);
}
```

### NodeJS Process Manager 2 - Example

```
pm2 start app.js -i 100
```

**Note:** manually running this application does not attach its process to the session, and it works as an orchestrator engine that also provides features such as automatic application restart on crash, automatic application scaling, and monitoring of application performance.
