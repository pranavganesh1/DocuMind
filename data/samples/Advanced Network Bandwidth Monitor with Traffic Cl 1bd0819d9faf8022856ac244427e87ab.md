# Advanced Network Bandwidth Monitor with Traffic Classification & Auto-Throttling (Two Windows Devices Setup)

## Step-by-Step Implementation Guide

### Architecture Overview

- **Server Device**: Will handle network monitoring, traffic classification, data logging, and auto-throttling.
- **Client Device**: Will connect to the server to view real-time statistics and historical data through a web interface.

## Setting Up the Server Device (Windows)

### Step 1: Install Required Software

1. **Install Python**
    - Download the latest Python installer from [https://www.python.org/downloads/](https://www.python.org/downloads/)
    - Run the installer and check "Add Python to PATH" before installing
    - Complete the installation
2. **Install Python Packages**
    
    ```
    pip install psutil scapy flask numpy matplotlib
    
    ```
    

### Step 2: Create the Main Monitoring Script

1. Create a folder for your project:
    
    ```
    mkdir BandwidthMonitor
    cd BandwidthMonitor
    
    ```
    
2. Create a file called `bandwidth_monitor.py`:
    
    ```python
    import psutil
    from scapy.all import *
    import time
    import threading
    from flask import Flask, render_template, jsonify
    import os
    import numpy as np
    from datetime import datetime
    import subprocess
    import ctypes
    
    # Check for administrator privileges
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("This script requires administrator privileges. Please run as administrator.")
        exit()
    
    # Configuration
    NETWORK_INTERFACE = "Ethernet"  # Change to your network interface name
    BANDWIDTH_LOG_FILE = "bandwidth_log.txt"
    THRESHOLD_MBPS = 5  # Alert threshold in MB/s
    ALERT_DURATION = 600  # Time in seconds to maintain alert (10 minutes)
    SERVER_PORT = 5000
    
    # Global variables
    device_stats = {}
    traffic_classification = {}
    alert_status = {}
    historical_data = []
    
    # Function to get device names from ARP table
    def get_device_names():
        devices = {}
        arp_output = subprocess.check_output("arp -a", shell=True).decode('utf-8', errors='ignore')
        for line in arp_output.splitlines():
            parts = line.split()
            if len(parts) >= 3 and "-" in parts[1]:
                ip = parts[1]
                mac = parts[3].replace("-", ":")
                devices[mac] = {"ip": ip, "name": "Unknown"}  # Windows ARP doesn't show names
        return devices
    
    # Function to classify traffic based on port numbers
    def classify_traffic(packet):
        if packet.haslayer(TCP):
            dport = packet[TCP].dport
            sport = packet[TCP].sport
        elif packet.haslayer(UDP):
            dport = packet[UDP].dport
            sport = packet[UDP].sport
        else:
            return "Unknown"
    
        # Traffic classification rules
        if dport == 443 or sport == 443:
            return "Streaming"  # HTTPS (could be streaming service)
        elif dport == 80 or sport == 80:
            return "Browsing"  # HTTP
        elif dport in [27015, 27000, 27020] or sport in [27015, 27000, 27020]:
            return "Gaming"  # Common gaming ports
        elif dport == 5004 or sport == 5004:
            return "Video Calls"  # VoIP/RTP
        else:
            return "Other"
    
    # Packet processing function
    def process_packet(packet):
        global device_stats, traffic_classification
    
        # Only process IP packets
        if not packet.haslayer(IP):
            return
    
        # Windows uses different layer names
        if not packet.haslayer(Ether):
            return
    
        src_mac = packet[Ether].src
        dst_mac = packet[Ether].dst
    
        # Update device statistics
        if src_mac not in device_stats:
            device_stats[src_mac] = {"upload": 0, "download": 0, "last_update": time.time()}
        if dst_mac not in device_stats:
            device_stats[dst_mac] = {"upload": 0, "download": 0, "last_update": time.time()}
    
        # Classify traffic
        traffic_type = classify_traffic(packet)
    
        # Update traffic classification stats
        if src_mac not in traffic_classification:
            traffic_classification[src_mac] = {}
        if traffic_type not in traffic_classification[src_mac]:
            traffic_classification[src_mac][traffic_type] = 0
        traffic_classification[src_mac][traffic_type] += len(packet)
    
        # Update upload/download stats
        device_stats[src_mac]["upload"] += len(packet)
        device_stats[dst_mac]["download"] += len(packet)
        device_stats[src_mac]["last_update"] = time.time()
        device_stats[dst_mac]["last_update"] = time.time()
    
    # Background thread to update rates and clean up old data
    def update_rates():
        global device_stats, alert_status
        while True:
            time.sleep(1)
    
            # Get device names
            device_names = get_device_names()
    
            # Calculate rates
            current_time = time.time()
            for mac, stats in list(device_stats.items()):
                # Remove devices that haven't been active recently
                if current_time - stats["last_update"] > 30:
                    del device_stats[mac]
                    continue
    
                # Calculate rate in MB/s
                upload_rate = stats["upload"] / 1024 / 1024 / 1  # per second
                download_rate = stats["download"] / 1024 / 1024 / 1
    
                # Update alert status
                if upload_rate > THRESHOLD_MBPS or download_rate > THRESHOLD_MBPS:
                    alert_status[mac] = {
                        "status": True,
                        "time": current_time,
                        "upload_rate": upload_rate,
                        "download_rate": download_rate,
                        "device_name": device_names.get(mac, "Unknown")
                    }
                elif mac in alert_status and current_time - alert_status[mac]["time"] > ALERT_DURATION:
                    del alert_status[mac]
    
                # Reset counters for next interval
                stats["upload"] = 0
                stats["download"] = 0
    
    # Function to log historical data
    def log_historical_data():
        global historical_data
        while True:
            time.sleep(3600)  # Log data every hour
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            total_upload = sum(stats["upload"] for stats in device_stats.values())
            total_download = sum(stats["download"] for stats in device_stats.values())
    
            historical_data.append({
                "timestamp": current_time,
                "total_upload": total_upload,
                "total_download": total_download
            })
    
            # Save to file
            with open(BANDWIDTH_LOG_FILE, "a") as f:
                f.write(f"{current_time},{total_upload},{total_download}\\n")
    
            # Keep only the last 24 hours of data in memory
            if len(historical_data) > 24:
                historical_data = historical_data[-24:]
    
    # Prediction function using moving average
    def predict_usage():
        if len(historical_data) < 24:
            return None  # Not enough data
    
        # Extract last 24 hours of data
        recent_uploads = [entry["total_upload"] for entry in historical_data[-24:]]
        recent_downloads = [entry["total_download"] for entry in historical_data[-24:]]
    
        # Calculate moving averages
        upload_avg = np.mean(recent_uploads)
        download_avg = np.mean(recent_downloads)
    
        return {
            "predicted_upload": upload_avg,
            "predicted_download": download_avg
        }
    
    # Flask web server setup
    app = Flask(__name__)
    
    @app.route('/')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/stats')
    def stats():
        global device_stats, alert_status, traffic_classification
    
        # Get device names
        device_names = get_device_names()
    
        # Format data for response
        formatted_stats = []
        for mac, stats in device_stats.items():
            upload_rate = stats["upload"] / 1024 / 1024  # MB/s
            download_rate = stats["download"] / 1024 / 1024
    
            formatted_stats.append({
                "mac": mac,
                "name": device_names.get(mac, "Unknown"),
                "upload": round(upload_rate, 2),
                "download": round(download_rate, 2),
                "traffic": traffic_classification.get(mac, {})
            })
    
        alerts = []
        for mac, alert in alert_status.items():
            alerts.append({
                "device": device_names.get(mac, "Unknown"),
                "upload_rate": round(alert["upload_rate"], 2),
                "download_rate": round(alert["download_rate"], 2),
                "time": datetime.fromtimestamp(alert["time"]).strftime("%H:%M:%S")
            })
    
        prediction = predict_usage()
    
        return jsonify({
            "stats": formatted_stats,
            "alerts": alerts,
            "historical": historical_data[-24:],  # Last 24 entries
            "prediction": prediction
        })
    
    # Function to apply firewall rules
    def apply_firewall_rules(mac, action):
        try:
            if action == "throttle":
                # Throttle bandwidth (Windows implementation)
                subprocess.run([
                    "netsh", "advfirewall", "firewall", "add", "rule",
                    "name=Throttle_" + mac,
                    "dir=out",
                    "action=throttle",
                    "remoteip=any",
                    "throttle rate=1Mbps",
                    "enabled=yes"
                ], check=True)
    
                subprocess.run([
                    "netsh", "advfirewall", "firewall", "add", "rule",
                    "name=Throttle_" + mac,
                    "dir=in",
                    "action=throttle",
                    "remoteip=any",
                    "throttle rate=1Mbps",
                    "enabled=yes"
                ], check=True)
    
            elif action == "unthrottle":
                # Remove throttling rules
                subprocess.run([
                    "netsh", "advfirewall", "firewall", "delete", "rule",
                    "name=Throttle_" + mac
                ], check=True)
    
            elif action == "block":
                # Block all traffic
                subprocess.run([
                    "netsh", "advfirewall", "firewall", "add", "rule",
                    "name=Block_" + mac,
                    "dir=out",
                    "action=block",
                    "remoteip=any",
                    "enabled=yes"
                ], check=True)
    
                subprocess.run([
                    "netsh", "advfirewall", "firewall", "add", "rule",
                    "name=Block_" + mac,
                    "dir=in",
                    "action=block",
                    "remoteip=any",
                    "enabled=yes"
                ], check=True)
    
            elif action == "unblock":
                # Remove blocking rules
                subprocess.run([
                    "netsh", "advfirewall", "firewall", "delete", "rule",
                    "name=Block_" + mac
                ], check=True)
    
        except subprocess.CalledProcessError as e:
            print(f"Error applying firewall rules: {e}")
    
    # Start packet sniffing
    def start_sniffing():
        sniff(iface=NETWORK_INTERFACE, prn=process_packet, store=0)
    
    if __name__ == '__main__':
        # Start background threads
        rate_thread = threading.Thread(target=update_rates)
        rate_thread.daemon = True
        rate_thread.start()
    
        log_thread = threading.Thread(target=log_historical_data)
        log_thread.daemon = True
        log_thread.start()
    
        # Create templates directory if it doesn't exist
        if not os.path.exists("templates"):
            os.makedirs("templates")
    
        # Create dashboard HTML file
        dashboard_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bandwidth Monitor</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .device { border: 1px solid #ccc; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .alert { background-color: #ffdddd; border-color: #ff5555; }
                .graph { height: 200px; border: 1px solid #ccc; margin: 10px 0; }
            </style>
        </head>
        <body>
            <h1>Network Bandwidth Monitor</h1>
            <div id="stats"></div>
            <div id="alerts"></div>
            <div id="historical"></div>
            <div id="prediction"></div>
            <script>
                function updateDashboard() {
                    fetch('/stats')
                        .then(response => response.json())
                        .then(data => {
                            let statsHtml = '<h2>Real-time Stats</h2>';
                            data.stats.forEach(device => {
                                let className = '';
                                let alertBadge = '';
                                if (device.upload > """ + str(THRESHOLD_MBPS) + """ || device.download > """ + str(THRESHOLD_MBPS) + """) {
                                    className = 'alert';
                                    alertBadge = '<span style="color:red">ALERT</span>';
                                }
                                statsHtml += `
                                    <div class="device ${className}">
                                        <strong>${device.name} (${device.mac})</strong> ${alertBadge}
                                        <div>Upload: ${device.upload} MB/s</div>
                                        <div>Download: ${device.download} MB/s</div>
                                        <div>Traffic Types:</div>
                                        <ul>
                                            ${Object.entries(device.traffic).map(([type, value]) =>
                                                `<li>${type}: ${(value / 1024 / 1024).toFixed(2)} MB</li>`
                                            ).join('')}
                                        </ul>
                                    </div>
                                `;
                            });
    
                            let alertsHtml = '<h2>Alerts</h2>';
                            if (data.alerts.length > 0) {
                                alertsHtml += '<ul>';
                                data.alerts.forEach(alert => {
                                    alertsHtml += `
                                        <li>${alert.device} - Upload: ${alert.upload_rate} MB/s, Download: ${alert.download_rate} MB/s (${alert.time})</li>
                                    `;
                                });
                                alertsHtml += '</ul>';
                            } else {
                                alertsHtml += '<p>No active alerts</p>';
                            }
    
                            let historicalHtml = '<h2>Historical Data</h2><div class="graph">Historical graph will appear here</div>';
                            let predictionHtml = '<h2>Prediction</h2>';
                            if (data.prediction) {
                                predictionHtml += `
                                    <p>Predicted Upload: ${data.prediction.predicted_upload.toFixed(2)} MB</p>
                                    <p>Predicted Download: ${data.prediction.predicted_download.toFixed(2)} MB</p>
                                `;
                            } else {
                                predictionHtml += '<p>Not enough data for prediction</p>';
                            }
    
                            document.getElementById('stats').innerHTML = statsHtml;
                            document.getElementById('alerts').innerHTML = alertsHtml;
                            document.getElementById('historical').innerHTML = historicalHtml;
                            document.getElementById('prediction').innerHTML = predictionHtml;
                        });
                }
    
                // Update dashboard every second
                setInterval(updateDashboard, 1000);
                updateDashboard();
            </script>
        </body>
        </html>
        """
    
        with open("templates/dashboard.html", "w") as f:
            f.write(dashboard_html)
    
        # Start packet sniffing in a thread
        sniff_thread = threading.Thread(target=start_sniffing)
        sniff_thread.daemon = True
        sniff_thread.start()
    
        # Start Flask server
        app.run(host='0.0.0.0', port=SERVER_PORT)
    
    ```
    

### Step 3: Create Firewall Rules for Auto-Throttling

The script above already includes Windows-compatible firewall rule management using `netsh`.

### Step 4: Set Up Automatic Start

1. Create a shortcut to your Python script
2. Right-click the shortcut > Properties
3. In the "Shortcut" tab, prepend "runas /user:Administrator" to the target path:
    
    ```
    runas /user:Administrator "C:\\Path\\to\\python.exe C:\\Path\\to\\bandwidth_monitor.py"
    
    ```
    
4. Save the shortcut
5. Press Win + R, type `shell:startup`, and place the shortcut there

## Setting Up the Client Device (Windows)

### Step 1: Install Required Software

1. **Install Python**
    - Download the latest Python installer from [https://www.python.org/downloads/](https://www.python.org/downloads/)
    - Run the installer and check "Add Python to PATH" before installing
    - Complete the installation
2. **Install Python Packages**
    
    ```
    pip install requests
    
    ```
    

### Step 2: Create a Simple Client Script

1. Create a folder for your client:
    
    ```
    mkdir BandwidthClient
    cd BandwidthClient
    
    ```
    
2. Create a file called `client.py`:
    
    ```python
    import requests
    import sys
    
    def main():
        if len(sys.argv) < 2:
            print("Usage: python client.py <server_ip>")
            return
    
        server_ip = sys.argv[1]
    
        try:
            response = requests.get(f'http://{server_ip}:{5000}')
            if response.status_code == 200:
                print(f"Connected to server at {server_ip}")
                print("Open a web browser and visit <http://localhost:5000> to view the dashboard")
            else:
                print(f"Connection failed with status code {response.status_code}")
        except requests.ConnectionError:
            print("Failed to connect to server. Please check the IP address and try again.")
    
    if __name__ == '__main__':
        main()
    
    ```
    

### Step 3: Run the Client Script

```
python client.py <server_device_ip>

```

## Testing the System

### On the Server Device:

1. Find your network interface name:
    - Open Command Prompt as Administrator
    - Run `netsh interface show interface`
    - Note the name of your active connection (e.g., "Ethernet" or "Wi-Fi")
2. Edit the `bandwidth_monitor.py` script:
    - Change `NETWORK_INTERFACE` to match your interface name
3. Run the monitoring script as Administrator:
    - Right-click Command Prompt and select "Run as administrator"
    - Navigate to your project folder
    - Run `python bandwidth_monitor.py`
4. Check the web interface by visiting `http://localhost:5000` in a browser on the server device.

### On the Client Device:

1. Run the client script with the server's IP address:

```
python client.py <server_ip>

```

1. Open a web browser and visit `http://<server_ip>:5000` to view the dashboard.

## Troubleshooting

### Common Issues and Solutions:

1. **Connection Refused**:
    - Ensure the server's Windows Firewall allows incoming connections on port 5000
    - Verify the server IP address is correct
    - Check if the bandwidth-monitor script is running
2. **No Device Detection**:
    - Ensure the network interface in the script matches your actual interface
    - Verify ARP table is populated (run `arp -a` on the server)
    - Check if devices are on the same network
3. **Incorrect Traffic Classification**:
    - Review and expand the port classification rules in the script
    - Consider using more advanced traffic analysis techniques
4. **Auto-Throttling Not Working**:
    - Ensure the script is running with administrator privileges
    - Verify the firewall_rules function is correctly implemented
    - Check Windows Firewall settings

## Enhancing Security

### On the Server Device:

1. Restrict access to the web interface by adding authentication:
    
    ```python
    from flask import request
    from flask_basicauth import BasicAuth
    
    app = Flask(__name__)
    app.config['BASIC_AUTH_USERNAME'] = 'admin'
    app.config['BASIC_AUTH_PASSWORD'] = 'secret'
    basic_auth = BasicAuth(app)
    
    @app.route('/')
    @basic_auth.required
    def dashboard():
        return render_template('dashboard.html')
    
    ```
    
2. Use HTTPS instead of HTTP for the web interface:
    - Generate self-signed certificates:
        
        ```
        openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
        
        ```
        
    - Update the Flask server code to use SSL:
        
        ```python
        if __name__ == '__main__':
            app.run(host='0.0.0.0', port=SERVER_PORT, ssl_context=('cert.pem', 'key.pem'))
        
        ```
        

## Conclusion

You now have a complete network bandwidth monitoring system that works across two Windows devices. The server device handles all monitoring, classification, and management tasks, while the client device provides a user-friendly interface to view the data. This setup allows you to effectively monitor and control network usage in your environment.