#!/usr/bin/env python3
import subprocess, os, json
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs

class CustomHandler(BaseHTTPRequestHandler):

    def _send_response(self, content_type='application/json'):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.send_header("Cache-Control", 'no-cache, no-store, must-revalidate')
        self.send_header("Pragma", 'no-cache')
        self.send_header("Expires", '0')
        self.end_headers()

    def do_GET(self):

        print(self.path)

        if '/files' in self.path:
            files = {}
            path = '/Torrent'
            try:
                for dirpath, dirnames, filenames in os.walk(path):
                    for file in filenames:
                        file_path = os.path.join(dirpath, file)
                        files[file_path.replace(path + '/', '')] = os.stat(file_path).st_size
                self._send_response()
                self.wfile.write(json.dumps(files, indent=4).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        elif '/status' in self.path:
            dynamicDns = os.environ.get('DYNAMIC_DNS')
            output = {
                "public IP": subprocess.run('dig +short myip.opendns.com @resolver1.opendns.com', shell=True, capture_output=True, text=True).stdout,
                "vpn": subprocess.run('[ $(curl -s l2.io/ip) != $(dig ' + str(dynamicDns) + ' +short) ] && echo \'<span style="color:green;">Connected</span>\' || echo \'<span style="color:red;">Disconnected</span>\'', shell=True, capture_output=True, text=True).stdout,
                "transmission": subprocess.run('if [ "$(systemctl status transmission-daemon.service | head -n 3 | tail -n 1 | awk \'{print $2,$3}\')" != "active (running)" ]; then echo \'<span style="color:red;">Not Running</span>\'; else echo \'<span style="color:green;">Running</span>\'; fi', shell=True, capture_output=True, text=True).stdout,
                "uptime": subprocess.run('uptime -p | cut -c4-', shell=True, capture_output=True, text=True).stdout,
                "free space": subprocess.run('df -h | grep \'\/$\' | awk \'{print $4}\'', shell=True, capture_output=True, text=True).stdout,
            }
            self._send_response()
            self.wfile.write(json.dumps(output, indent=4).encode())

        elif '/halt' in self.path:
          self._send_response('text/plain')
          subprocess.getoutput('sudo shutdown now')
          return

        elif '/reboot' in self.path:
          self._send_response('text/plain')
          self.wfile.write(bytes('Rebooting', 'utf-8'))
          subprocess.getoutput('sudo reboot')
          return

        elif '/connect' in self.path:
          subprocess.getoutput('sudo windscribe connect')
          self._send_response()
          self.wfile.write(bytes('Connected', 'utf-8'))
          return

        elif '/disconnect' in self.path:
          subprocess.getoutput('sudo windscribe disconnect')
          self._send_response()
          self.wfile.write(bytes('Disconnected', 'utf-8'))
          return

        elif '/stop' in self.path:
          subprocess.getoutput('sudo /bin/systemctl stop transmission-daemon.service')
          self._send_response()
          self.wfile.write(bytes('Paused', 'utf-8'))
          return

        elif '/start' in self.path:
          subprocess.getoutput('sudo /bin/systemctl start transmission-daemon.service')
          self._send_response()
          self.wfile.write(bytes('Started', 'utf-8'))
          return
        elif '/' in self.path or 'index.html' in self.path or '/icon.jpg' in self.path:
          if '/' in self.path or 'index.html' in self.path:
            self._send_response('text/html')
            url = 'index.html'
          elif self.path == '/icon.jpg':
            self._send_response('image/jpeg')
            url = 'icon.jpg'
          else:
            return
          file = open(url, "rb")
          self.wfile.write(bytes(file.read()))
          file.close()
          return

        else:
            self.send_response(404)
            self.end_headers()
            return

    def log_message(self, format, *args):
      pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

try:
    server = ThreadedHTTPServer(('0.0.0.0', 80), CustomHandler)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()
except KeyboardInterrupt:
    print(' Interrupted')
    server.socket.close()
