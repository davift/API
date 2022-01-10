#!/usr/bin/env python3
import subprocess, json, glob, os, time
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import unquote

def http_server(host_port,content_type="application/json"):
	class CustomHandler(SimpleHTTPRequestHandler):
		def do_GET(self) -> None:

			def send_301():
				self.send_response(301)
				self.send_header("Location", '/')
				self.send_header("Cache-Control", 'no-cache, no-store, must-revalidate')
				self.send_header("Pragma", 'no-cache')
				self.send_header("Expires", '0')
				self.end_headers()

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

			if self.path == '/status':
				send_200()
				output = Output()

				output.transmission = subprocess.getoutput('systemctl status transmission-daemon.service | head -n 3 | tail -n 1 | awk \'{print $2,$3}\'')
				runCmd1 = subprocess.getoutput('curl -s http://ip.me')
				runCmd2 = subprocess.getoutput('dig dftsue.duckdns.org +short') ## Dynamic DNS or static IP
				if runCmd1 == runCmd2:
					output.vpn_status = 'OFF'
				else:
					output.vpn_status = 'ON'
#				output.vpn_data = subprocess.getoutput(app + '/vpn.sh status | grep "Data Usage" | cut -c13-') ## Makes the script refresh slower
				output.drive_used = subprocess.getoutput('df -h | head -n 2 | tail -n 1 | awk \'{print $5}\'')
				output.drive_free = subprocess.getoutput('df -h | head -n 2 | tail -n 1 | awk \'{print $4}\'')
				output.uptime = subprocess.getoutput('uptime -p | cut -c4-')

				self.wfile.write(bytes(json.dumps(output.__dict__, indent=4), 'utf-8'))
				return

			elif self.path == '/halt':
				send_200('text/plain')

				self.wfile.write(bytes('System Halted!', 'utf-8'))
				subprocess.getoutput('shutdown now')
				return

			elif self.path == '/reboot':
				subprocess.getoutput('reboot')
				send_301()
				return

			elif self.path == '/start':
				subprocess.getoutput(app + '/vpn.sh on')
				send_301()
				return

			elif self.path == '/stop':
				subprocess.getoutput(app + '/vpn.sh off')
				send_301()
				return

			elif self.path == '/pause':
				subprocess.getoutput(app + '/transmission.sh off')
				send_301()
				return

			elif self.path == '/resume':
				subprocess.getoutput(app + '/transmission.sh on')
				send_301()
				return

#			elif self.path.find('/del?') == 0:
#				delete = path + self.path.replace('del?', '', 1).replace(' ', '\ ')
#				subprocess.getoutput('rm -f ' + delete)
#				send_200()
#				return

			elif self.path == '/' or self.path == '/icon-32x32.jpg':
				if self.path == '/':
					send_200('text/html')
					url = '/index.html'

				else:
					send_200('image/jpeg')
					url = self.path

				file = open(app + url, "rb")
				self.wfile.write(bytes(file.read()))
				file.close()
				return

			elif self.path == '/files':
				self.send_response(200)
				self.send_header("Content-type", content_type)
				self.end_headers()

				list = {}
				path=r"/Torrent"
				files = glob.glob(path + r'/**', recursive=True)
				for file in files:
					if os.path.isfile(file):
						list[file.replace(path + '/', '', 1)] = os.stat(file).st_size

				self.wfile.write(bytes(json.dumps(list, indent=4), 'utf-8'))
				return

			else:
#				if os.path.isfile(path + self.path):
#					self.send_response(200)
#					self.send_header("Content-type", "")
#					self.send_header("Content-Disposition", "attachment; filename=" + os.path.basename(path + self.path))
#					self.send_header("Content-Transfer-Encoding", "binary")
#					self.send_header("Content-Length", os.stat(path + self.path).st_size)
#					self.end_headers()
#
#					file = open(path + self.path, "rb")
#					try:
#						self.wfile.write(bytes(file.read()))
#						file.close()
#					except:
#						file.close()
#					return

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
