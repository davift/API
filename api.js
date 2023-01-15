var http = require('http');
var url = require('url');
const fs = require('fs');
const { execSync } = require("child_process");

const path = '/Torrent';

const server = http.createServer((req, res) => {
  "use strict";
  const pathname = url.parse(req.url).pathname;
  console.log('Requested: ' + pathname);

  if (pathname == '/'){
    res.setHeader('Content-Type', 'text/html');
    fs.createReadStream('index.html').pipe(res);
  } else if (pathname == '/icon.jpg'){
    res.setHeader('Content-Type', 'image/jpeg');
    fs.createReadStream('icon.jpg').pipe(res);
  } else if (pathname == '/status'){
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');

    let status = {};

    // Note: I decided to use execSync to simplify the code.
    // For better performance in production the exec is best
    // because it is asynchromnous by default.
    try {
      let out = execSync('dig +short myip.opendns.com @resolver1.opendns.com', {encoding: 'utf8'}).toString();
      status['public IP'] = out.replace(/\n*$/, "");
    } catch(err) {
      console.error(err);
    }
    try {
      let out = execSync('[ $(curl -s l2.io/ip) != $(dig ' + String(process.env.DYNAMIC_DNS) + ' +short) ] && echo \'<span style="color:green;">Connected</span>\' || echo \'<span style="color:red;">Disconnected</span>\'', {encoding: 'utf8'}).toString();
      status['vpn'] = out.replace(/\n*$/, "");
    } catch(err) {
      console.error(err);
    }
    try {
      let out = execSync('if [ "$(systemctl status transmission-daemon.service | head -n 3 | tail -n 1 | awk \'{print $2,$3}\')" != "active (running)" ]; then echo \'<span style="color:red;">Not Running</span>\'; else echo \'<span style="color:green;">Running</span>\'; fi', {encoding: 'utf8'}).toString();
      status['transmission'] = out.replace(/\n*$/, "");
    } catch(err) {
      console.error(err);
    }
    try {
      let out = execSync('uptime -p | cut -c4-', {encoding: 'utf8'}).toString();
      status['uptime'] = out.replace(/\n*$/, "");
    } catch(err) {
      console.error(err);
    }
    try {
      let out = execSync('df -h | grep \'\/$\' | awk \'{print $4}\'', {encoding: 'utf8'}).toString();
      status['free space'] = out.replace(/\n*$/, "");
    } catch(err) {
      console.error(err);
    }
    
    res.write(JSON.stringify(status, null, 2));
    res.end();
  } else if (pathname == '/files'){
    let files = {};
    res.setHeader('Content-Type', 'application/json');
    let stdout;
    try {
      stdout = execSync(`find -L ${path} -type f | sed 's_${path}/__g'`);
    } catch (err) {
      throw err;
    }
    let list = stdout.toString().split("\n");
    list.forEach(file => {
      if (file != ''){
        files[file] = fs.statSync(path + '/' + file).size;
      }
    });
    res.write(JSON.stringify(files, null, 2));
    res.end();
  } else if (pathname == '/halt'){
    res.setHeader('Content-Type', 'text/html');
    res.write('Halted');
    res.end();
    execSync('sudo shutdown now');
  } else if (pathname == '/reboot'){
    res.setHeader('Content-Type', 'text/html');
    res.write('Rebooting');
    res.end();
    execSync('sudo reboot');
  } else if (pathname == '/connect'){
    res.setHeader('Content-Type', 'text/html');
    res.write('Connected');
    res.end();
    execSync('sudo windscribe connect');
  } else if (pathname == '/disconnect'){
    res.setHeader('Content-Type', 'text/html');
    res.write('Disconnected');
    res.end();
    execSync('sudo windscribe disconnect');
  } else if (pathname == '/stop'){
    res.setHeader('Content-Type', 'text/html');
    res.write('Stopped');
    res.end();
    execSync('sudo /bin/systemctl stop transmission-daemon.service');
  } else if (pathname == '/start'){
    res.setHeader('Content-Type', 'text/html');
    res.write('Started');
    res.end();
    execSync('sudo /bin/systemctl start transmission-daemon.service');
  } else {
    res.writeHead(404);
    res.end();
  }
});

server.listen(80);
