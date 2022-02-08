package main

import (
  "os"
  "os/exec"
  "path/filepath"
  "net/http"
  "io/ioutil"
  "log"
  "encoding/json"
)

func halt(w http.ResponseWriter, req *http.Request) {
  w.Header().Set("Content-Type", "text/html")
  w.Write([]byte("Halted"))

  _, _ = exec.Command("bash" ,"-c", "sudo shutdown -h 1").Output()
}

func reboot(w http.ResponseWriter, req *http.Request) {
  w.Header().Set("Content-Type", "text/html")
  w.Write([]byte("Rebooting"))

  _, _ = exec.Command("bash" ,"-c", "sudo shutdown -r 1").Output()
}

func connect(w http.ResponseWriter, req *http.Request) {
  w.Header().Set("Content-Type", "text/html")

  _, _ = exec.Command("bash" ,"-c", "sudo windscribe connect").Output()
  w.Write([]byte("Connected"))
}

func disconnect(w http.ResponseWriter, req *http.Request) {
  w.Header().Set("Content-Type", "text/html")

  _, _ = exec.Command("bash" ,"-c", "sudo windscribe disconnect").Output()
  w.Write([]byte("Disconnected"))
}

func start(w http.ResponseWriter, req *http.Request) {
  w.Header().Set("Content-Type", "text/html")

  _, _ = exec.Command("bash" ,"-c", "sudo systemctl start transmission-daemon.service").Output()
  w.Write([]byte("Started"))
}

func stop(w http.ResponseWriter, req *http.Request) {
  w.Header().Set("Content-Type", "text/html")

  _, _ = exec.Command("bash" ,"-c", "sudo systemctl stop transmission-daemon.service").Output()
  w.Write([]byte("Stopped"))
}

func status(w http.ResponseWriter, req *http.Request) {
  status := map[string]string{}
  w.Header().Set("Content-Type", "application/json")

  cmd1, _ := exec.Command("bash" ,"-c", "systemctl status transmission-daemon.service | head -n 3 | tail -n 1 | awk '{print $2,$3}'").Output()
  if string(cmd1) == "active (running)\n" {
    status["transmission"] = "<span style=\"color:green;\">Running</span>"
  } else {
    status["transmission"] = "<span style=\"color:red;\">Not Running</span>"
  }

  cmd2, _ := exec.Command("bash" ,"-c", "if [ $(curl -s http://ip.me) != $(dig example.duckdns.org +short) ]; then echo '<span style=\"color:green;\">Connected</span>'; else echo '<span style=\"color:red;\">Disconnected</span>'; fi").Output()
  status["vpn_status"] = string(cmd2)

  cmd3, _ := exec.Command("bash" ,"-c", "windscribe account | grep \"Data Usage\" | cut -c13-").Output()
  status["vpn_data"] = string(cmd3)

  cmd4, _ := exec.Command("bash" ,"-c", "df -h | head -n 2 | tail -n 1 | awk '{print $5}'").Output()
  status["drive_used"] = string(cmd4)

  cmd5, _ := exec.Command("bash" ,"-c", "df -h | head -n 2 | tail -n 1 | awk '{print $4}'").Output()
  status["drive_free"] = string(cmd5)

  cmd6, _ := exec.Command("bash" ,"-c", "uptime -p").Output()
  status["uptime"] = string(cmd6)

  output, _ := json.Marshal(status)
  w.Write(output)
}

func files(w http.ResponseWriter, req *http.Request) {
  w.Header().Set("Content-Type", "application/json")
  files := map[string]int64{}

  err := filepath.Walk("/Torrent", func(path string, info os.FileInfo, err error) error {
    if err != nil {
      return err
    }
    if !info.IsDir(){
      files[path] = info.Size()
    }
    return nil
  })
  if err != nil {
    log.Println(err)
  }

  output, _ := json.Marshal(files)
  w.Write(output)
}

func root(w http.ResponseWriter, req *http.Request) {
  file := "index.html"
  content, err := ioutil.ReadFile(file)
  if err != nil {
    log.Fatal(err)
  }

  w.Header().Set("Content-Type", "text/html")
  w.Write(content)
}

func icon(w http.ResponseWriter, req *http.Request) {
  file := "icon.jpg"
  content, err := ioutil.ReadFile(file)
  if err != nil {
    log.Fatal(err)
  }

  w.Header().Set("Content-Type", "image/jpeg")
  w.Write(content)
}

func main() {
  http.HandleFunc("/", root)
  http.HandleFunc("/icon.jpg", icon)
  http.HandleFunc("/status", status)
  http.HandleFunc("/connect", connect)
  http.HandleFunc("/disconnect", disconnect)
  http.HandleFunc("/start", start)
  http.HandleFunc("/stop", stop)
  http.HandleFunc("/halt", halt)
  http.HandleFunc("/reboot", reboot)
  http.HandleFunc("/files", files)
  http.ListenAndServe(":80", nil)
}
