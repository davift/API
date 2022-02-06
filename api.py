#!/usr/bin/env python3
import subprocess, json, glob, os, time
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import unquote

def http_server(host_port,content_type="application/json"):
  class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:

      def send_200(content_type="application/json"):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.send_header("Cache-Control", 'no-cache, no-store, must-revalidate')
        self.send_header("Pragma", 'no-cache')
        self.send_header("Expires", '0')
        self.end_headers()

      class Output:
        pass

      self.path = unquote(self.path)
      app = '/App'
      path = '/Torrent'

      if self.path == '/files':
        list = {}
        path=r"/Torrent"
        files = glob.glob(path + r'/**', recursive=True)
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()
        for file in files:
          if os.path.isfile(file):
            list[file.replace(path + '/', '', 1)] = os.stat(file).st_size

        self.wfile.write(bytes(json.dumps(list, indent=4), 'utf-8'))
        return

      elif self.path == '/status':
        send_200()
        output = Output()

        runCmd1 = subprocess.getoutput('systemctl status transmission-daemon.service | head -n 3 | tail -n 1 | awk \'{print $2,$3}\'')
        if runCmd1 != 'active (running)':
          output.transmission = '<span style="color:red;">Not Running</span>'
        else:
          output.transmission = '<span style="color:green;">Running</span>'
        runCmd2 = subprocess.getoutput('curl -s http://ip.me')
        runCmd3 = subprocess.getoutput('dig example.duckdns.org +short') ## Dynamic DNS or static IP
        if runCmd2 == runCmd3:
          output.vpn_status = '<span style="color:red;">Disconnected</span>'
        else:
          output.vpn_status = '<span style="color:green;">Connected</span>'
        output.vpn_data = subprocess.getoutput('windscribe account | grep "Data Usage" | cut -c13-') ## Very slow!
        output.drive_used = subprocess.getoutput('df -h | head -n 2 | tail -n 1 | awk \'{print $5}\'')
        output.drive_free = subprocess.getoutput('df -h | head -n 2 | tail -n 1 | awk \'{print $4}\'')
        output.uptime = subprocess.getoutput('uptime -p | cut -c4-')

        self.wfile.write(bytes(json.dumps(output.__dict__, indent=4), 'utf-8'))
        return

      elif self.path == '/halt':
        send_200('text/plain')
        self.wfile.write(bytes('Halted', 'utf-8'))
        subprocess.getoutput('shutdown now')
        return

      elif self.path == '/reboot':
        send_200('text/plain')
        self.wfile.write(bytes('Rebooting', 'utf-8'))
        subprocess.getoutput('reboot')
        return

      elif self.path == '/connect':
        subprocess.getoutput('sudo windscribe connect')
        send_200()
        self.wfile.write(bytes('Connected', 'utf-8'))
        return

      elif self.path == '/disconnect':
        subprocess.getoutput('sudo windscribe disconnect')
        send_200()
        self.wfile.write(bytes('Disconnected', 'utf-8'))
        return

      elif self.path == '/stop':
        subprocess.getoutput('sudo /bin/systemctl stop transmission-daemon.service')
        send_200()
        self.wfile.write(bytes('Paused', 'utf-8'))
        return

      elif self.path == '/start':
        subprocess.getoutput('sudo /bin/systemctl start transmission-daemon.service')
        send_200()
        self.wfile.write(bytes('Started', 'utf-8'))
        return

      elif self.path == '/' or self.path == '/icon.jpg':
        if self.path == '/':
          send_200('text/html')
          url = '/index.html'
        elif self.path == '/icon.jpg':
          send_200('image/jpeg')
          url = self.path
        else:
          return
        file = open(app + url, "rb")
        self.wfile.write(bytes(file.read()))
        file.close()
        return

      else:
        self.send_response(404)
        self.end_headers()
        return

    def log_message(self, format, *args):
      pass
  class _TCPServer(TCPServer):
    allow_reuse_address = True
  httpd = _TCPServer(host_port, CustomHandler)
  httpd.serve_forever()

try:
  http_server(('0.0.0.0',80))
except KeyboardInterrupt:
  print(' Interrupted')
  exit()
