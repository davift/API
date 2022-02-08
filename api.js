var http = require('http');
var url = require('url');
const fs = require('fs')
const { execSync } = require("child_process");

const app = '/App';
const path = '/Torrent';

async function processRequest(request, response) {
  "use strict";

  var pathname = url.parse(request.url).pathname;
//  console.log('Requested: ' + pathname);

  if (pathname == '/'){
    fs.readFile(app + '/index.html', function(error, data) {
      response.writeHead(200, { 'Content-Type': 'text/html' });
      response.write(data);
      response.end();
    })
  } else if (pathname == '/icon.jpg'){
    fs.readFile('icon.jpg', function(error, data) {
      response.writeHead(200, { 'Content-Type': 'image/jpeg' });
      response.write(data);
      response.end();
    })
  } else if (pathname == '/status'){
    response.writeHead(200, { 'Content-Type': 'text/html', 'Cache-Control': 'no-cache, no-store, must-revalidate', 'Pragma': 'no-cache', 'Expires': '0' });
    let status = {};
    let stdout = execSync('systemctl status transmission-daemon.service | head -n 3 | tail -n 1 | awk \'{print $2,$3}\'', {encoding: 'utf8'});
    if (stdout == 'active (running)\n'){
      status['transmission'] = '<span style="color:green;">Running</span>';
    } else {
      status['transmission'] = '<span style="color:red;">Not Running</span>';
    }
    status['vpn_status'] = execSync('if [ $(curl -s http://ip.me) != $(dig example.duckdns.org +short) ]; then echo \'<span style="color:green;">Connected</span>\'; else echo \'<span style="color:red;">Disconnected</span>\'; fi', {encoding: 'utf8'}).replace(/\n*$/, "");
    status['vpn_data'] = execSync('windscribe account | grep "Data Usage" | cut -c13-', {encoding: 'utf8'}).replace(/\n*$/, "");
    status['drive_used'] = execSync('df -h | head -n 2 | tail -n 1 | awk \'{print $5}\'', {encoding: 'utf8'}).replace(/\n*$/, "");
    status['drive_free'] = execSync('df -h | head -n 2 | tail -n 1 | awk \'{print $4}\'', {encoding: 'utf8'}).replace(/\n*$/, "");
    status['uptime'] = execSync('uptime -p', {encoding: 'utf8'}).replace(/\n*$/, "");
    response.write(JSON.stringify(status, null, 2));
    response.end();
  } else if (pathname == '/files'){
    let files = {};
    response.writeHead(200, { 'Content-Type': 'text/html' });
    let stdout = execSync(`find -L ${path} -type f | sed 's_${path}/__g'`, {encoding: 'utf8'});
    let list = stdout.split("\n");
    list.forEach(file => {
      if (file != ''){
        files[file] = fs.statSync(path + '/' + file).size;
      }
    });
    response.write(JSON.stringify(files, null, 2));
    response.end();
  } else if (pathname == '/halt'){
    response.writeHead(200, { 'Content-Type': 'text/html' });
    response.write('Halted');
    response.end();
    execSync('sudo shutdown now');
  } else if (pathname == '/reboot'){
    response.writeHead(200, { 'Content-Type': 'text/html' });
    response.write('Rebooting');
    response.end();
    execSync('sudo reboot');
  } else if (pathname == '/connect'){
    response.writeHead(200, { 'Content-Type': 'text/html' });
    execSync('sudo windscribe connect');
    response.write('Connected');
    response.end();
  } else if (pathname == '/disconnect'){
    response.writeHead(200, { 'Content-Type': 'text/html' });
    execSync('sudo windscribe disconnect');
    response.write('Disconnected');
    response.end();
  } else if (pathname == '/stop'){
    response.writeHead(200, { 'Content-Type': 'text/html' });
    execSync('sudo /bin/systemctl stop transmission-daemon.service');
    response.write('Stopped');
    response.end();
  } else if (pathname == '/start'){
    response.writeHead(200, { 'Content-Type': 'text/html' });
    execSync('sudo /bin/systemctl start transmission-daemon.service');
    response.write('Started');
    response.end();
  } else {
    response.writeHead(404);
    response.end();
  }
}

http.createServer(processRequest).listen(80);
