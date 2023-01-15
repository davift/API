package main

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
)

func halt(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "text/html")
	w.Write([]byte("Halted"))

	_, _ = exec.Command("bash", "-c", "sudo shutdown -h 1").Output()
}

func reboot(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "text/html")
	w.Write([]byte("Rebooting"))

	_, _ = exec.Command("bash", "-c", "sudo shutdown -r 1").Output()
}

func connect(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "text/html")

	_, _ = exec.Command("bash", "-c", "sudo windscribe connect").Output()
	w.Write([]byte("Connected"))
}

func disconnect(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "text/html")

	_, _ = exec.Command("bash", "-c", "sudo windscribe disconnect").Output()
	w.Write([]byte("Disconnected"))
}

func start(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "text/html")

	_, _ = exec.Command("bash", "-c", "sudo systemctl start transmission-daemon.service").Output()
	w.Write([]byte("Started"))
}

func stop(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "text/html")

	_, _ = exec.Command("bash", "-c", "sudo systemctl stop transmission-daemon.service").Output()
	w.Write([]byte("Stopped"))
}

func status(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	cmd1, _ := exec.Command("bash", "-c", "dig +short myip.opendns.com @resolver1.opendns.com").Output()
	cmd2, _ := exec.Command("bash", "-c", "[ $(curl -s l2.io/ip) != $(dig "+os.Getenv("DYNAMIC_DNS")+" +short) ] && echo '<span style=\"color:green;\">Connected</span>' || echo '<span style=\"color:red;\">Disconnected</span>'").Output()
	cmd3, _ := exec.Command("bash", "-c", "if [ \"$(systemctl status transmission-daemon.service | head -n 3 | tail -n 1 | awk '{print $2,$3}')\" != \"active (running)\" ]; then echo '<span style=\"color:red;\">Not Running</span>'; else echo '<span style=\"color:green;\">Running</span>'; fi").Output()
	cmd4, _ := exec.Command("bash", "-c", "uptime -p | cut -c4-").Output()
	cmd5, _ := exec.Command("bash", "-c", "df -h | grep '/$' | awk '{print $4}'").Output()

	status := map[string]interface{}{
		"public IP":    string(cmd1),
		"vpn":          string(cmd2),
		"transmission": string(cmd3),
		"uptime":       string(cmd4),
		"free space":   string(cmd5),
	}

	output, _ := json.MarshalIndent(status, "", "  ")
	w.Write(output)
}

func files(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	files := map[string]int64{}

	err := filepath.Walk("/Torrent", func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
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
	w.Header().Set("Content-Type", "text/html")
	w.Write(indexHTMLContent)
}

func icon(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "image/jpeg")
	w.Write(iconImageContent)
}

// Note: it loads the index.html and icon.jpg in memory once during the start for better perfoamnce
var indexHTMLContent []byte
var iconImageContent []byte

func init() {
	var err error
	indexHTMLContent, err = ioutil.ReadFile("index.html")
	if err != nil {
		log.Fatal(err)
	}
	iconImageContent, err = ioutil.ReadFile("icon.jpg")
	if err != nil {
		log.Fatal(err)
	}
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
