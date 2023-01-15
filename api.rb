require 'socket'
require 'json'

class CustomHandler
  def _send_response(content_type='application/json')
    @client.puts "HTTP/1.1 200 OK\r\n" +
                "Content-type: #{content_type}\r\n" +
                "Cache-Control: no-cache, no-store, must-revalidate\r\n" +
                "Pragma: no-cache\r\n" +
                "Expires: 0\r\n\r\n"
  end

  def initialize(client)
    @client = client
    request = client.gets
    # Prints to the console
    #puts request

    if request.include? '/files'
      files = {}
      path = '/Torrent'
      begin
        Dir.foreach(path) do |file|
          file_path = File.join(path, file)
          files[file_path.gsub("#{path}/", "")] = File.size?(file_path)
        end
        _send_response
        client.puts files.to_json
      rescue => e
        client.puts "HTTP/1.1 500 Internal Server Error\r\n\r\n"
        client.puts e.message
      end

    elsif request.include? '/status'
      dynamicDns = ENV['DYNAMIC_DNS']
      output = {
        "public IP": `dig +short myip.opendns.com @resolver1.opendns.com`,
        "vpn": `[ $(curl -s l2.io/ip) != $(dig #{dynamicDns} +short) ] && echo '<span style="color:green;">Connected</span>' || echo '<span style="color:red;">Disconnected</span>'`,
        "transmission": `if [ "$(systemctl status transmission-daemon.service | head -n 3 | tail -n 1 | awk '{print $2,$3}')" != "active (running)" ]; then echo '<span style="color:red;">Not Running</span>'; else echo '<span style="color:green;">Running</span>\'; fi`,
        "uptime": `uptime -p | cut -c4-`,
        "free space": `df -h | grep '/$' | awk '{print $4}'`,
      }
      _send_response
      client.puts output.to_json

    elsif request.include? '/start'
      `sudo /bin/systemctl start transmission-daemon.service`
      _send_response
      client.puts 'Started'

    elsif request.include?('/') || request.include?('index.html') || request.include?('/icon.jpg')
      if request.include?('/') || request.include?('index.html')
        _send_response('text/html')
        url = 'index.html'
      elsif request.include?('/icon.jpg')
        _send_response('image/jpeg')
        url = 'icon.jpg'
      else
        return
      end
      file = File.open(url, 'rb')
      client.puts file.read
      file.close

    else
      client.puts "HTTP/1.1 404 Not Found\r\n\r\n"
    end
    client.close
  end
end

server = TCPServer.new(80)
puts 'Starting server, use <Ctrl-C> to stop'
loop do
  Thread.start(server.accept) do |client|
    CustomHandler.new(client)
  end
end
