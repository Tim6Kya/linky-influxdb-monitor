# Linky InfluxDB Monitor

Real-time monitoring solution for French Linky smart meters using Raspberry Pi, InfluxDB, and Grafana.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Raspberry Pi](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)

## Features

- Real-time data collection from Linky TIC interface
- Automatic data transmission to InfluxDB
- Local CSV backup for data redundancy
- Compatible with Grafana for beautiful dashboards
- Easy to configure and deploy
- Lightweight and runs 24/7 on Raspberry Pi Zero

## Hardware Requirements

- **Raspberry Pi Zero WH** (with headers for GPIO)
- **Micro USB cable** for power
- **Micro SD card** (8GB minimum, Class 10 recommended)
- **TIC cable** to connect to Linky meter (I1/I2 terminals)
- **Raspberry Pi 3 Model B+** (or any server running InfluxDB)
- **Local network** (LAN/Wi-Fi)

## Software Requirements

- Python 3.7+
- InfluxDB 2.x
- Grafana (optional, for visualization)

### Python Dependencies
pyserial
influxdb-client

## Installation

### 1. Clone the Repository
git clone https://github.com/yourusername/linky-influxdb-monitor.git
cd linky-influxdb-monitor

### 2. Install Dependencies
pip3 install -r requirements.txt

### 3. Configure Serial Port (Raspberry Pi)
Enable UART on your Raspberry Pi Zero:
sudo raspi-config
# Navigate to: Interface Options > Serial Port
# Disable login shell over serial: No
# Enable serial port hardware: Yes

Edit `/boot/config.txt`:
sudo nano /boot/config.txt

Add/modify:
enable_uart=1
dtoverlay=disable-bt

Reboot:
sudo reboot

### 4. Configure the Script
Edit `linky_monitor.py` and update the configuration section:
URL = "http://YOUR_INFLUXDB_SERVER_IP:8086"
TOKEN = "your-influxdb-token-here"
ORG = "your-organization"
BUCKET = "your-bucket-name"

**⚠️ IMPORTANT:** Never commit your actual token to GitHub! Use the `config.example.py` template.

### 5. Set Up InfluxDB

On your InfluxDB server (Raspberry Pi 3 B+):

1. Create a new bucket named `linky-data`
2. Generate an API token with write permissions
3. Note your organization name

## Usage

### Run Manually
python3 linky_monitor.py

### Run as a Service (Recommended)

Create a systemd service for automatic startup:
sudo nano /etc/systemd/system/linky-monitor.service

Add:
[Unit]
Description=Linky Meter Monitor
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/linky-influxdb-monitor/linky_monitor.py
WorkingDirectory=/home/pi/linky-influxdb-monitor
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target

Enable and start:
sudo systemctl enable linky-monitor.service
sudo systemctl start linky-monitor.service
sudo systemctl status linky-monitor.service

## Grafana Dashboard

Import the included `grafana-dashboard.json` to visualize:
- Real-time power consumption (VA)
- Energy index evolution (Wh)
- Daily/weekly/monthly statistics
- Cost estimation (configure your kWh rate)

## Troubleshooting

### No data received from Linky

- Check TIC cable connection (I1/I2 terminals)
- Verify serial port: `ls -l /dev/ttyAMA0`
- Test serial communication: `cat /dev/ttyAMA0`

### InfluxDB connection errors

- Verify network connectivity: `ping YOUR_INFLUXDB_IP`
- Check token permissions in InfluxDB
- Ensure bucket exists

### Permission denied on serial port
sudo usermod -a -G dialout pi
sudo reboot

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- French electricity provider Enedis for the Linky TIC specification
- InfluxData for the excellent time-series database
- Grafana Labs for the visualization platform
- Raspberry Pi Foundation

---

**⭐ If this project helped you, please give it a star!**
